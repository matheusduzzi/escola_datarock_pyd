"""Os números por trás de cada gráfico da aula «Escolher gráfico pela pergunta».

Rode de dentro da pasta da aula:
    python3 resumos.py --pergunta distribuicao
    python3 resumos.py --pergunta relacao
    python3 resumos.py --pergunta composicao
    python3 resumos.py --pergunta evolucao
    python3 resumos.py --tabela

Cada pergunta imprime a tabela que o gráfico desenharia, quantas marcas ele teria e quem fica fora.
--tabela escreve resultados.csv, uma linha por inscrição das duas edições, para você contar o que precisar.
Os dados vêm de ../dados/triatlo. Parcial vazia fica vazia: nada vira zero.
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

DADOS = Path('..') / 'dados' / 'triatlo'
ETAPAS = ['natacao', 't1', 'ciclismo', 't2', 'corrida']


def segundos(texto):
    if texto is None:
        return pd.NA
    h, m, s = (int(p) for p in texto.split(':'))
    return h * 3600 + m * 60 + s


def carregar():
    """Uma linha por inscrição das duas edições, com o resultado quando existe."""
    for nome in ['api_resultados.json', 'inscricoes_2024.csv', 'inscricoes_2025.csv', 'atletas.csv']:
        if not (DADOS / nome).is_file():
            print(f'arquivo não encontrado: {DADOS / nome}. Rode de dentro da pasta da aula, no kit do curso.')
            sys.exit(2)
    res = pd.DataFrame(json.loads((DADOS / 'api_resultados.json').read_text(encoding='utf-8')))
    res = res.drop_duplicates(subset=['edicao', 'id_inscricao'])  # cópias iguais, vistas na aula 26
    parciais = pd.json_normalize(res['parciais'].tolist())
    parciais.index = res.index
    for etapa in ETAPAS:
        res[etapa] = parciais[etapa].map(segundos).astype('Int64')
    res['oficial'] = res['tempo_oficial'].map(segundos).astype('Int64')
    insc = pd.concat([pd.read_csv(DADOS / 'inscricoes_2024.csv'),
                      pd.read_csv(DADOS / 'inscricoes_2025.csv', sep=';')]).drop_duplicates()
    insc['edicao'] = insc['id_inscricao'].str[:4].astype(int)
    atletas = pd.read_csv(DADOS / 'atletas.csv')
    t = insc.merge(atletas[['id_atleta', 'sexo', 'ano_nascimento']], on='id_atleta', how='left', validate='many_to_one')
    t = t.merge(res[['edicao', 'id_inscricao', 'status', 'oficial'] + ETAPAS], on=['edicao', 'id_inscricao'],
                how='left', validate='one_to_one')
    t['idade'] = t['edicao'] - t['ano_nascimento']
    t['status'] = t['status'].fillna('sem resultado')
    return t


def minutos(serie):
    return (serie.astype('Float64') / 60).round(1)


def distribuicao(t):
    d = t[t.edicao == 2025]
    c = d[d.oficial.notna()]
    horas = c.oficial.astype(float) / 3600
    print('Pergunta: em que tempo a maior parte de quem terminou cruzou a linha em 2025?')
    print(f'marcas no gráfico: {len(c)} atletas com tempo oficial (cada um entra numa faixa)')
    fora = d[d.oficial.isna()].status.value_counts()
    print('ficam fora, sem tempo oficial: ' + ', '.join(f'{k} {v}' for k, v in fora.items()) + f' (total {fora.sum()})')
    print(f'mínimo {horas.min():.1f} h | mediana {horas.median():.1f} h | média {horas.mean():.1f} h | máximo {horas.max():.1f} h')
    print('faixa de tempo oficial   atletas')
    faixas = pd.cut(horas, bins=range(8, 17), right=False)
    for faixa, n in faixas.value_counts().sort_index().items():
        print(f'  {faixa.left:>2} h a {faixa.right:>2} h        {n:>4}  ' + '#' * round(n / 2))
    print('cada # = 2 atletas')


def relacao(t):
    c = t[(t.edicao == 2025) & (t.status == 'concluiu')].copy()
    c['natacao_min'] = minutos(c.natacao).astype(float)
    c['corrida_min'] = minutos(c.corrida).astype(float)
    print('Pergunta: quem nada mais rápido também corre mais rápido? (2025, quem concluiu)')
    print(f'marcas no gráfico: {len(c)} pontos, um por atleta (natação e corrida, em minutos)')
    r = c.natacao.astype(float).corr(c.corrida.astype(float))
    print(f'correlação entre natação e corrida: {r:.2f}')
    c['quarto'] = pd.qcut(c.natacao_min, 4, labels=['25% mais rápidos', 'segundo quarto', 'terceiro quarto',
                                                    '25% mais lentos'])
    g = c.groupby('quarto', observed=True).agg(atletas=('corrida_min', 'size'),
                                               natacao_mediana=('natacao_min', 'median'),
                                               corrida_mediana=('corrida_min', 'median'),
                                               corrida_min=('corrida_min', 'min'),
                                               corrida_max=('corrida_min', 'max'))
    print('na natação, em quartos             atletas  natação (mediana)  corrida (mediana)  corrida (mín. a máx.)')
    for nome, l in g.iterrows():
        print(f'  {nome:<32} {int(l.atletas):>4}  {l.natacao_mediana:>12.1f} min  {l.corrida_mediana:>12.1f} min'
              f'  {l.corrida_min:>8.1f} a {l.corrida_max:.1f} min')


def composicao(t):
    d = t[t.edicao == 2025]
    ordem = ['concluiu', 'DNF', 'DNS', 'DSQ', 'sem resultado']
    n = d.status.value_counts().reindex(ordem, fill_value=0)
    largaram = n.drop(['DNS', 'sem resultado']).sum()
    print('Pergunta: dos inscritos de 2025, quantos terminaram?')
    print(f'inscritos: {n.sum()} | com resultado no arquivo: {n.drop("sem resultado").sum()} | largaram: {largaram}')
    print('status          atletas   % dos inscritos   % de quem largou')
    for k, v in n.items():
        pl = f'{100 * v / largaram:>10.1f}' if k not in ('DNS', 'sem resultado') else '         -'
        print(f'  {k:<14} {v:>6}   {100 * v / n.sum():>12.1f}      {pl}')
    print(f'  {"total":<14} {n.sum():>6}   {100.0:>12.1f}      {100.0:>10.1f}')


def evolucao(t):
    print('Pergunta: em que parte da prova os atletas foram ficando pelo caminho?')
    print('ponto da prova         2024    %     2025    %   (atletas ainda na prova; % de quem largou)')
    linhas = {}
    for ed in (2024, 2025):
        d = t[(t.edicao == ed) & t.status.isin(['concluiu', 'DNF', 'DSQ'])]
        linhas[ed] = [('largada', len(d)),
                      ('fim da natação', int(d.natacao.notna().sum())),
                      ('fim do ciclismo', int(d.ciclismo.notna().sum())),
                      ('chegada', int(d.corrida.notna().sum())),
                      ('chegada sem DSQ', int((d.status == 'concluiu').sum()))]
    for i, (ponto, _) in enumerate(linhas[2024]):
        a, b = linhas[2024][i][1], linhas[2025][i][1]
        print(f'  {ponto:<18} {a:>6} {100 * a / linhas[2024][0][1]:>5.1f}   {b:>6} {100 * b / linhas[2025][0][1]:>5.1f}')
    ed = pd.read_csv(DADOS / 'edicoes.csv')
    for _, e in ed.iterrows():
        print(f'{e.edicao}: natação {e.natacao_km} km, máxima de {e.temperatura_max_c} °C, {e.observacao}')


def tabela(t):
    saida = t[['edicao', 'id_inscricao', 'id_atleta', 'categoria', 'sexo', 'idade', 'status']].copy()
    for etapa in ETAPAS:
        saida[f'{etapa}_min'] = minutos(t[etapa])
    saida['oficial_h'] = (t.oficial.astype('Float64') / 3600).round(2)
    saida.to_csv('resultados.csv', index=False)
    print(f'resultados.csv: {len(saida)} linhas (uma por inscrição) x {saida.shape[1]} colunas')
    print('colunas: ' + ', '.join(saida.columns))
    print(saida.groupby('edicao').status.value_counts().unstack(fill_value=0).to_string())


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    grupo = ap.add_mutually_exclusive_group(required=True)
    grupo.add_argument('--pergunta', choices=['distribuicao', 'relacao', 'composicao', 'evolucao'])
    grupo.add_argument('--tabela', action='store_true', help='escreve resultados.csv')
    args = ap.parse_args()
    dados = carregar()
    if args.tabela:
        tabela(dados)
    else:
        globals()[args.pergunta](dados)
