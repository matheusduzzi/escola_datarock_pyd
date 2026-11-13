"""As transformações do relatório do triatlo. Aula «Escrever testes de dados e funções».

Cada função diz no comentário o que promete. Os testes cobram essas promessas.

Para usar no Python, de dentro da pasta da aula:
    from transformacoes import ler_dados, montar_tabela, taxa_conclusao, ritmo_natacao

Os dados vêm de ../dados/triatlo. Usa o pandas.
"""
import json
from pathlib import Path

import pandas as pd

DADOS = Path('..') / 'dados' / 'triatlo'
ETAPAS = ['natacao', 't1', 'ciclismo', 't2', 'corrida']
LARGARAM = ['concluiu', 'DNF', 'DSQ']  # DNS e "sem resultado" não largaram


class ResultadoDuplicado(ValueError):
    """A API mandou duas versões diferentes do mesmo resultado."""


class ResultadoSemInscricao(ValueError):
    """A API mandou o resultado de uma inscrição que não está nos arquivos de inscrição."""


def segundos(texto):
    """'1:14:19' vira 4459. Vazio (None) continua vazio: tempo que não existe não é zero."""
    if texto is None:
        return pd.NA
    h, m, s = (int(p) for p in texto.split(':'))
    return h * 3600 + m * 60 + s


# ---------------------------------------------------------------- a tabela

def montar_tabela(inscricoes, resultados):
    """Uma linha por inscrição, com o resultado da API quando existe.

    inscricoes: DataFrame com id_inscricao, id_atleta, numero_peito, categoria e equipe.
    resultados: a lista de resultados da API, como vem do JSON.

    A chave é a edição com o id_inscricao: nenhuma inscrição aparece duas vezes. Linha de inscrição
    repetida e cópia idêntica de resultado contam uma vez só. Duas versões diferentes do mesmo resultado
    param com ResultadoDuplicado. Resultado de uma inscrição que não existe para com ResultadoSemInscricao.
    Inscrição sem resultado fica com o status 'sem resultado'.

    Tipos: edicao, id_atleta e numero_peito são int64. Os tempos (natacao_s, t1_s, ciclismo_s, t2_s,
    corrida_s e oficial_s) são Int64, o inteiro do pandas que aceita vazio: tempo que não existe fica <NA>.
    """
    insc = inscricoes.drop_duplicates().copy()
    insc['edicao'] = insc['id_inscricao'].str[:4].astype('int64')

    linhas, vistos = [], {}
    for r in resultados:
        chave = (r['edicao'], r['id_inscricao'])
        if chave in vistos:
            if vistos[chave] != r:
                raise ResultadoDuplicado(f'duas versões diferentes do resultado {chave[1]} ({chave[0]})')
            continue
        vistos[chave] = r
        linha = {'edicao': r['edicao'], 'id_inscricao': r['id_inscricao'], 'status': r['status'],
                 'oficial_s': segundos(r['tempo_oficial'])}
        for etapa in ETAPAS:
            linha[f'{etapa}_s'] = segundos(r['parciais'][etapa])
        linhas.append(linha)
    colunas_tempo = [f'{e}_s' for e in ETAPAS] + ['oficial_s']
    res = pd.DataFrame(linhas, columns=['edicao', 'id_inscricao', 'status'] + colunas_tempo)
    res['edicao'] = res['edicao'].astype('int64')
    for c in colunas_tempo:
        res[c] = res[c].astype('Int64')

    sobra = res.merge(insc[['edicao', 'id_inscricao']], how='left', indicator=True)
    sobra = sobra[sobra['_merge'] == 'left_only']
    if len(sobra):
        raise ResultadoSemInscricao(f'{len(sobra)} resultado(s) sem inscrição: ' +
                                    ', '.join(f'{i} ({e})' for e, i in zip(sobra.edicao, sobra.id_inscricao)))

    t = insc.merge(res, on=['edicao', 'id_inscricao'], how='left', validate='one_to_one')
    t['status'] = t['status'].fillna('sem resultado')
    colunas = ['edicao', 'id_inscricao', 'id_atleta', 'numero_peito', 'categoria', 'status'] + colunas_tempo
    return t[colunas].reset_index(drop=True)


# ---------------------------------------------------------------- regra de negócio

def taxa_conclusao(tabela, por='edicao'):
    """Taxa de conclusão sobre quem largou, por grupo.

    Largou quem tem status concluiu, DNF ou DSQ. DNS e 'sem resultado' não largaram.
    Retorna uma linha por grupo com inscritos, largaram, concluiram (int64) e taxa_pct (float),
    a porcentagem de quem concluiu entre quem largou. Grupo sem ninguém que largou fica com a taxa vazia (NaN).
    """
    g = tabela.groupby(por)['status']
    saida = pd.DataFrame({
        'inscritos': g.size(),
        'largaram': g.apply(lambda s: int(s.isin(LARGARAM).sum())),
        'concluiram': g.apply(lambda s: int((s == 'concluiu').sum())),
    }).astype('int64')
    saida['taxa_pct'] = (100 * saida['concluiram'] / saida['largaram'].where(saida['largaram'] > 0)).astype(float)
    return saida


# ---------------------------------------------------------------- conta com decimais

def ritmo_natacao(tabela, edicoes):
    """Ritmo da natação, em minutos por 100 metros, de quem tem a parcial de natação.

    edicoes: DataFrame de edicoes.csv, com a distância da natação de cada edição em natacao_km.
    A distância muda de uma edição para outra (3,8 km em 2024 e 1,9 km em 2025): o ritmo usa a da edição
    de cada linha. Retorna uma Series de float com o mesmo índice da tabela; sem a parcial, a linha não entra.
    """
    km = tabela['edicao'].map(edicoes.set_index('edicao')['natacao_km'])
    com_natacao = tabela['natacao_s'].notna()
    minutos = tabela.loc[com_natacao, 'natacao_s'].astype(float) / 60
    return (minutos / (km[com_natacao] * 10)).rename('ritmo_min_100m')


def ritmo_corrida(tabela, edicoes):
    """Ritmo da corrida, em minutos por quilômetro, só de quem concluiu a prova.

    Usa a distância da corrida de cada edição (corrida_km de edicoes.csv). Retorna uma Series de float
    com o mesmo índice da tabela. DNF, DSQ e DNS ficam fora, mesmo quando têm a parcial da corrida.
    """
    km = tabela['edicao'].map(edicoes.set_index('edicao')['corrida_km'])
    ok = (tabela['status'] == 'concluiu') & tabela['corrida_s'].notna()
    return (tabela.loc[ok, 'corrida_s'].astype(float) / 60 / km[ok]).rename('ritmo_min_km')


def melhor_por_atleta(tabela):
    """O melhor tempo oficial de cada atleta, entre as edições que ele concluiu.

    Uma linha por id_atleta (a chave), só de quem concluiu pelo menos uma edição. Colunas: id_atleta,
    melhor_s (o menor tempo oficial, em segundos), edicao (a edição desse tempo) e concluidas (quantas
    edições o atleta concluiu). Todas int64. Empate entre edições fica com a mais antiga.
    """
    c = tabela[tabela['status'] == 'concluiu']
    c = c.sort_values(['id_atleta', 'oficial_s', 'edicao'])
    melhor = c.drop_duplicates('id_atleta', keep='first')
    saida = pd.DataFrame({'id_atleta': melhor['id_atleta'].to_numpy(),
                          'melhor_s': melhor['oficial_s'].to_numpy(),
                          'edicao': melhor['edicao'].to_numpy()})
    saida['concluidas'] = saida['id_atleta'].map(c.groupby('id_atleta').size())
    return saida.astype('int64').reset_index(drop=True)


# ---------------------------------------------------------------- leitura dos arquivos

def ler_dados(pasta=DADOS):
    """Inscrições das duas edições (DataFrame), resultados da API (lista) e edições (DataFrame)."""
    pasta = Path(pasta)
    for nome in ['inscricoes_2024.csv', 'inscricoes_2025.csv', 'api_resultados.json', 'edicoes.csv']:
        if not (pasta / nome).is_file():
            raise FileNotFoundError(f'arquivo não encontrado: {pasta / nome}. '
                                    'Rode de dentro da pasta da aula, no kit do curso.')
    inscricoes = pd.concat([pd.read_csv(pasta / 'inscricoes_2024.csv'),
                            pd.read_csv(pasta / 'inscricoes_2025.csv', sep=';')], ignore_index=True)
    resultados = json.loads((pasta / 'api_resultados.json').read_text(encoding='utf-8'))
    edicoes = pd.read_csv(pasta / 'edicoes.csv')
    return inscricoes, resultados, edicoes
