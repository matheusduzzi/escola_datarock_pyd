"""Versões com defeito das funções de transformacoes.py. Aula «Escrever testes de dados e funções».

Cada defeito é um erro que alguém poderia fazer de verdade: a função roda, não dá erro e retorna um
resultado que parece certo. O conftest.py troca a função certa por uma dessas versões quando você roda
    python3 -m pytest --defeito D3
e os testes dizem se pegam o defeito.

D1 a D5 são das funções da aula. E1 a E5 são das funções do exercício.
"""
import pandas as pd

import transformacoes as tr
from transformacoes import ETAPAS, LARGARAM

_certas = {nome: getattr(tr, nome) for nome in ['montar_tabela', 'taxa_conclusao', 'ritmo_natacao',
                                                 'ritmo_corrida', 'melhor_por_atleta']}


# ---------------------------------------------------------------- defeitos das funções da aula

def d1_taxa_conclusao(tabela, por='edicao'):
    largaram = LARGARAM + ['DNS']  # "DNS também estava inscrito na largada"
    g = tabela.groupby(por)['status']
    saida = pd.DataFrame({'inscritos': g.size(),
                          'largaram': g.apply(lambda s: int(s.isin(largaram).sum())),
                          'concluiram': g.apply(lambda s: int((s == 'concluiu').sum()))}).astype('int64')
    saida['taxa_pct'] = (100 * saida['concluiram'] / saida['largaram'].where(saida['largaram'] > 0)).astype(float)
    return saida


def d2_montar_tabela(inscricoes, resultados):
    # a linha de inscrição repetida não sai: o drop_duplicates e o validate do merge foram retirados
    insc = inscricoes.copy()
    insc['edicao'] = insc['id_inscricao'].str[:4].astype('int64')
    certa = _certas['montar_tabela'](inscricoes, resultados)
    res = certa.drop(columns=['id_atleta', 'numero_peito', 'categoria'])
    t = insc.merge(res, on=['edicao', 'id_inscricao'], how='left')
    return t[list(certa.columns)].reset_index(drop=True)


def d3_montar_tabela(inscricoes, resultados):
    t = _certas['montar_tabela'](inscricoes, resultados)
    for c in [f'{e}_s' for e in ETAPAS] + ['oficial_s']:
        t[c] = t[c].astype(float)  # "em float fica mais fácil fazer conta"; o vazio vira NaN
    return t


def d4_ritmo_natacao(tabela, edicoes):
    return _certas['ritmo_natacao'](tabela, edicoes).round(1)  # arredonda antes de sair


def d5_ritmo_natacao(tabela, edicoes):
    com_natacao = tabela['natacao_s'].notna()
    minutos = tabela.loc[com_natacao, 'natacao_s'].astype(float) / 60
    return (minutos / 38).rename('ritmo_min_100m')  # 3,8 km fixo, o percurso de 2024


# ---------------------------------------------------------------- defeitos das funções do exercício

def e1_melhor_por_atleta(tabela):
    c = tabela[tabela['status'] == 'concluiu'].sort_values(['id_atleta', 'edicao'])
    melhor = c.drop_duplicates('id_atleta', keep='last')  # fica a edição mais recente, não a melhor
    saida = pd.DataFrame({'id_atleta': melhor['id_atleta'].to_numpy(),
                          'melhor_s': melhor['oficial_s'].to_numpy(),
                          'edicao': melhor['edicao'].to_numpy()})
    saida['concluidas'] = saida['id_atleta'].map(c.groupby('id_atleta').size())
    return saida.astype('int64').reset_index(drop=True)


def e2_melhor_por_atleta(tabela):
    c = tabela[tabela['status'] == 'concluiu'].sort_values(['numero_peito', 'oficial_s', 'edicao'])
    melhor = c.drop_duplicates('numero_peito', keep='first')  # a chave é o número de peito
    saida = pd.DataFrame({'id_atleta': melhor['id_atleta'].to_numpy(),
                          'melhor_s': melhor['oficial_s'].to_numpy(),
                          'edicao': melhor['edicao'].to_numpy()})
    saida['concluidas'] = melhor['numero_peito'].map(c.groupby('numero_peito').size()).to_numpy()
    return saida.astype('int64').reset_index(drop=True)


def e3_melhor_por_atleta(tabela):
    saida = _certas['melhor_por_atleta'](tabela)
    saida['melhor_s'] = saida['melhor_s'].astype(float)  # o tempo vira float
    return saida


def e4_ritmo_corrida(tabela, edicoes):
    ok = (tabela['status'] == 'concluiu') & tabela['corrida_s'].notna()
    return (tabela.loc[ok, 'corrida_s'].astype(float) / 60 / 42).rename('ritmo_min_km')  # 42 km redondos


def e5_ritmo_corrida(tabela, edicoes):
    km = tabela['edicao'].map(edicoes.set_index('edicao')['corrida_km'])
    ok = tabela['corrida_s'].notna()  # quem tem a parcial da corrida entra, mesmo sem concluir
    return (tabela.loc[ok, 'corrida_s'].astype(float) / 60 / km[ok]).rename('ritmo_min_km')


# código: (função trocada, versão com defeito, o que está errado)
DEFEITOS = {
    'D1': ('taxa_conclusao', d1_taxa_conclusao, 'DNS entra entre quem largou'),
    'D2': ('montar_tabela', d2_montar_tabela, 'a linha de inscrição repetida conta duas vezes'),
    'D3': ('montar_tabela', d3_montar_tabela, 'os tempos viram float, e o vazio vira NaN'),
    'D4': ('ritmo_natacao', d4_ritmo_natacao, 'o ritmo sai arredondado em uma casa'),
    'D5': ('ritmo_natacao', d5_ritmo_natacao, 'a distância da natação é 3,8 km nas duas edições'),
    'E1': ('melhor_por_atleta', e1_melhor_por_atleta, 'fica o tempo da edição mais recente, e não o melhor'),
    'E2': ('melhor_por_atleta', e2_melhor_por_atleta, 'a chave é o número de peito, e não o id_atleta'),
    'E3': ('melhor_por_atleta', e3_melhor_por_atleta, 'o melhor tempo vira float'),
    'E4': ('ritmo_corrida', e4_ritmo_corrida, 'a corrida tem 42 km redondos, e não 42,2'),
    'E5': ('ritmo_corrida', e5_ritmo_corrida, 'quem não concluiu entra no ritmo, se tem a parcial da corrida'),
}


def ativar(codigo):
    """Troca a função certa de transformacoes.py pela versão com defeito. Retorna a descrição."""
    nome, funcao, descricao = DEFEITOS[codigo]
    setattr(tr, nome, funcao)
    return f'{codigo} em {nome}: {descricao}'
