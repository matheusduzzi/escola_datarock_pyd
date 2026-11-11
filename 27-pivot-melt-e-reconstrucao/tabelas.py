"""Monta a tabela larga dos resultados do triatlo, a mesma da página do Caio.

Uso, de dentro da pasta da aula:
    python3 tabelas.py

Lê ../dados/triatlo/api_resultados.json, tira as cópias iguais (como na aula 26) e escreve
resultados_largo.csv nesta pasta: uma linha por resultado, uma coluna por etapa, mais o
status, o número de peito e o tempo oficial. Tudo em segundos. Tempo vazio fica vazio (<NA>).
"""
import json
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
DADOS = AQUI.parent / 'dados' / 'triatlo'
ETAPAS = ['natacao', 't1', 'ciclismo', 't2', 'corrida']
CHAVE = ['edicao', 'id_inscricao']
ATRIBUTOS = ['numero_peito', 'status', 'tempo_oficial']
COLUNAS = CHAVE + ['numero_peito', 'status'] + ETAPAS + ['tempo_oficial']


def segundos(texto):
    """'1:14:19' vira 4459. Tempo vazio (None) continua vazio."""
    if texto is None:
        return None
    h, m, s = (int(x) for x in texto.split(':'))
    return h * 3600 + m * 60 + s


def ler_resultados():
    """Uma linha por resultado do arquivo da API, com as cópias."""
    linhas = []
    for r in json.loads((DADOS / 'api_resultados.json').read_text(encoding='utf-8')):
        linha = {c: r[c] for c in ['edicao', 'id_inscricao', 'numero_peito', 'status']}
        for etapa in ETAPAS:
            linha[etapa] = segundos(r['parciais'][etapa])
        linha['tempo_oficial'] = segundos(r['tempo_oficial'])
        linhas.append(linha)
    tabela = pd.DataFrame(linhas)[COLUNAS]
    tabela[ETAPAS + ['tempo_oficial']] = tabela[ETAPAS + ['tempo_oficial']].astype('Int64')
    return tabela


def ler_largo():
    """A tabela larga sem as cópias iguais: uma linha por edição e inscrição."""
    return ler_resultados().drop_duplicates().reset_index(drop=True)


def ler_inscricoes():
    """As inscrições das duas edições, sem as linhas repetidas do arquivo de 2025."""
    i24 = pd.read_csv(DADOS / 'inscricoes_2024.csv', dtype={'id_inscricao': str})
    i25 = pd.read_csv(DADOS / 'inscricoes_2025.csv', sep=';', dtype={'id_inscricao': str})
    return pd.concat([i24, i25], ignore_index=True).drop_duplicates().reset_index(drop=True)


if __name__ == '__main__':
    bruto, largo = ler_resultados(), ler_largo()
    largo.to_csv(AQUI / 'resultados_largo.csv', index=False)
    print(f'resultados no arquivo da API: {len(bruto)} | cópias iguais tiradas: {len(bruto) - len(largo)}')
    print(f'largo: {largo.shape[0]} linhas x {largo.shape[1]} colunas -> resultados_largo.csv')
    print('\nstatus:', ', '.join(f'{s} {n}' for s, n in largo['status'].value_counts().items()))
    print('\nA inscrição 2025-0016 no largo:')
    print(largo[largo['id_inscricao'] == '2025-0016'].to_string(index=False))
