"""Monta a planilha do histórico dos atletas que a federação pediu ao Caio.

Uso, de dentro da pasta da aula:
    python3 historico.py

Escreve historico_largo.csv nesta pasta: uma linha por atleta (id_atleta) e uma coluna por
etapa e edição, como natacao_2024 ou corrida_2025, com o tempo em segundos. Quem não correu
uma edição, ou não tem tempo numa etapa, fica com a célula vazia.
"""
import pandas as pd

from tabelas import AQUI, ETAPAS, ler_inscricoes, ler_largo

EDICOES = [2024, 2025]
COLUNAS = [f'{etapa}_{ano}' for ano in EDICOES for etapa in ETAPAS]


def montar():
    """Uma linha por atleta. Começa com tudo vazio e preenche célula por célula."""
    atleta_de = dict(zip(*[ler_inscricoes()[c] for c in ['id_inscricao', 'id_atleta']]))
    linhas = {}
    for r in ler_largo().to_dict('records'):
        linha = linhas.setdefault(atleta_de[r['id_inscricao']], {c: None for c in COLUNAS})
        for etapa in ETAPAS:
            if not pd.isna(r[etapa]):
                linha[f'{etapa}_{r["edicao"]}'] = int(r[etapa])
    planilha = pd.DataFrame([{'id_atleta': a, **linhas[a]} for a in sorted(linhas)])
    planilha[COLUNAS] = planilha[COLUNAS].astype('Int64')
    return planilha


if __name__ == '__main__':
    planilha = montar()
    planilha.to_csv(AQUI / 'historico_largo.csv', index=False)
    print(f'historico_largo.csv: {planilha.shape[0]} atletas x {planilha.shape[1]} colunas')
    print('colunas: ' + ', '.join(planilha.columns))
