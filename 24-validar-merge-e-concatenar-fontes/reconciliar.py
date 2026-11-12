"""Junta a planilha do posto de chegada aos resultados da API e confere se as contas fecham.

Uso, de dentro da pasta da aula:
    python3 reconciliar.py --passo caio          # a versão do Caio: concat, drop_duplicates e merge
    python3 reconciliar.py --passo copias        # as cópias de cada fonte: iguais e com versões diferentes
    python3 reconciliar.py --passo peito         # o posto ganha o id_inscricao pela edição e pelo peito
    python3 reconciliar.py --passo empilhar      # a API e o posto numa tabela só, com a coluna fonte
    python3 reconciliar.py --passo sobreposicao  # o que o posto tem que a API já tinha
    python3 reconciliar.py --passo base          # a base com o posto de 2025 e a reconciliação

No exercício, use as funções no Python:
    from reconciliar import *
    t = carregar()
    posto = ler_posto(2024)

Lê ../dados/triatlo e posto/. As tabelas entram como chegam, com as linhas repetidas.
"""
import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
DADOS = AQUI.parent / 'dados' / 'triatlo'
POSTO = AQUI / 'posto'
ARQUIVOS = ['inscricoes_2024.csv', 'inscricoes_2025.csv', 'api_resultados.json']
CHAVE = ['edicao', 'id_inscricao']
CAMPOS = ['status', 'tempo_oficial']
COLUNAS = ['edicao', 'id_inscricao', 'numero_peito', 'status', 'tempo_oficial']


class ReconciliacaoNaoFecha(Exception):
    """Uma conta de linhas ou de valores não fechou."""


def parar(mensagem):
    print(mensagem)
    print('Rode de dentro da pasta da aula, no kit do curso.')
    sys.exit(2)


def carregar():
    """As tabelas como chegam: inscricoes (as duas edições, com a coluna edicao) e resultados (a API)."""
    faltando = [n for n in ARQUIVOS if not (DADOS / n).is_file()]
    if faltando:
        parar(f'arquivo não encontrado: {DADOS / faltando[0]}')
    partes = []
    for edicao, sep in ((2024, ','), (2025, ';')):
        tabela = pd.read_csv(DADOS / f'inscricoes_{edicao}.csv', sep=sep, dtype={'id_inscricao': str, 'equipe': str})
        partes.append(tabela.assign(edicao=edicao))
    inscricoes = pd.concat(partes, ignore_index=True)
    brutos = json.loads((DADOS / 'api_resultados.json').read_text(encoding='utf-8'))
    resultados = pd.DataFrame([{c: r[c] for c in COLUNAS} for r in brutos])
    return {'inscricoes': inscricoes, 'resultados': resultados}


def ler_posto(edicao):
    """A planilha do posto de uma edição, como chegou: edicao, peito, status, tempo."""
    arquivo = POSTO / f'posto_{edicao}.csv'
    if not arquivo.is_file():
        parar(f'arquivo não encontrado: {arquivo}')
    return pd.read_csv(arquivo, sep=';', dtype={'tempo': str})


def segundos(tempo):
    """'H:MM:SS' vira segundos (inteiro); vazio continua vazio."""
    return pd.to_timedelta(tempo).dt.total_seconds().astype('Int64')


def copias(tabela, chave, nome):
    """Separa as linhas repetidas pela chave. Retorna (sem_copias, conflitos).

    Cópia igual em todas as colunas conta uma vez. Chave repetida com conteúdo diferente sai
    inteira de sem_copias e vai para conflitos: nenhuma coluna diz qual versão é a certa.
    """
    chave = [chave] if isinstance(chave, str) else list(chave)
    unicas = tabela.drop_duplicates()
    diferente = unicas.duplicated(chave, keep=False)
    conflitos, sem = unicas[diferente], unicas[~diferente]
    print(f'{nome}: {len(tabela)} linhas | cópias iguais: {len(tabela) - len(unicas)} | '
          f'chaves com versões diferentes: {len(conflitos.drop_duplicates(chave))} ({len(conflitos)} linhas) | '
          f'ficam: {len(sem)}')
    return sem, conflitos


def achar_inscricao(posto, inscricoes):
    """Põe o id_inscricao em cada linha do posto, pela edição e pelo peito. Retorna (com_inscricao, sem_inscricao).

    O posto vem sem cópias. As colunas passam a ter os nomes da API: peito vira numero_peito e
    tempo vira tempo_oficial. Linha cujo peito não existe naquela edição vai para sem_inscricao.
    """
    faltam = [c for c in ('edicao', 'peito', 'status', 'tempo') if c not in posto.columns]
    if faltam:
        raise ValueError(f'a planilha do posto não tem as colunas {faltam}: veja os nomes no LEIA-ME do posto')
    posto = posto.rename(columns={'peito': 'numero_peito', 'tempo': 'tempo_oficial'})
    chaves = inscricoes[['edicao', 'numero_peito', 'id_inscricao']].drop_duplicates()
    juntos = posto.merge(chaves, on=['edicao', 'numero_peito'], how='left', validate='many_to_one', indicator=True)
    print('_merge:', juntos['_merge'].value_counts().to_dict())
    com = juntos[juntos['_merge'] == 'both'][COLUNAS]
    sem = juntos[juntos['_merge'] == 'left_only'][COLUNAS]
    return com, sem


def empilhar(api, posto):
    """A API e o posto numa tabela só, com a coluna fonte. Para se as colunas não forem as mesmas."""
    if list(api.columns) != list(posto.columns):
        raise ValueError(f'colunas diferentes: api {list(api.columns)} | posto {list(posto.columns)}')
    return pd.concat([api.assign(fonte='api'), posto.assign(fonte='posto')], ignore_index=True)


def sobreposicao(empilhada, chave=CHAVE, campos=CAMPOS):
    """Chaves que estão nas duas fontes. Retorna (iguais, diferentes), uma linha por chave, lado a lado."""
    nas_duas = empilhada.groupby(chave)['fonte'].transform('nunique') > 1
    api = empilhada[nas_duas & (empilhada['fonte'] == 'api')]
    posto = empilhada[nas_duas & (empilhada['fonte'] == 'posto')]
    lado = api[chave + campos].merge(posto[chave + campos], on=chave, suffixes=('_api', '_posto'),
                                     validate='one_to_one')
    igual = pd.Series(True, index=lado.index)
    for c in campos:
        igual &= lado[f'{c}_api'].fillna('') == lado[f'{c}_posto'].fillna('')
    return lado[igual], lado[~igual]


def valores(resultados):
    """Por edição: quantos de cada status e a soma do tempo oficial de quem concluiu, em segundos."""
    r = resultados.assign(segundos=segundos(resultados['tempo_oficial']))
    tabela = r.groupby(['edicao', 'status']).size().unstack(fill_value=0)
    tabela['tempo_concluiu_s'] = r[r['status'] == 'concluiu'].groupby('edicao')['segundos'].sum()
    return tabela.astype('int64')


def montar_base(inscricoes, resultados):
    """Uma linha por inscrição, com o resultado quando existe (how left, validate one_to_one)."""
    base = inscricoes.merge(resultados.drop(columns='numero_peito'), on=CHAVE, how='left',
                            validate='one_to_one', indicator=True)
    base['status'] = base['status'].fillna('sem resultado')
    return base


def fechar(nome, esquerda, direita):
    """Uma conta da reconciliação: imprime e para se os dois lados não forem iguais."""
    print(f'  {nome}: {esquerda} = {direita}  {"fecha" if esquerda == direita else "NÃO FECHA"}')
    if esquerda != direita:
        raise ReconciliacaoNaoFecha(f'a conta "{nome}" não fechou')


# ---------------------------------------------------------------- os passos da aula

def passo_caio(t):
    print('A versão do Caio: renomeia as colunas, empilha, tira as linhas repetidas e junta pelo peito.\n')
    posto = ler_posto(2025).rename(columns={'peito': 'numero_peito', 'tempo': 'tempo_oficial'})
    juntos = pd.concat([t['resultados'], posto]).drop_duplicates()
    base = t['inscricoes'].drop_duplicates().merge(juntos, on=['edicao', 'numero_peito'], how='left')
    concluiu = base[(base['edicao'] == 2025) & (base['status'] == 'concluiu')]
    print(f'linhas da base: {len(base)}')
    print(f'concluíram em 2025: {len(concluiu)}')
    print(f'mulheres que concluíram em 2025: {int(concluiu["categoria"].str.startswith("F").sum())}')


def passo_copias(t):
    copias(t['inscricoes'], CHAVE, 'inscricoes')
    copias(t['resultados'], CHAVE, 'api')
    _, conflitos = copias(ler_posto(2025), ['edicao', 'peito'], 'posto 2025')
    return conflitos


def passo_peito(t):
    inscricoes, _ = copias(t['inscricoes'], CHAVE, 'inscricoes')
    posto, _ = copias(ler_posto(2025), ['edicao', 'peito'], 'posto 2025')
    print()
    com, sem = achar_inscricao(posto, inscricoes)
    print(f'com inscrição: {len(com)} | sem inscrição: {len(sem)}')
    print('\nsem inscrição:')
    print(sem.to_string(index=False))
    peitos = inscricoes[inscricoes['edicao'] == 2025]['numero_peito']
    print(f'\npeitos de 2025 nas inscrições: de {peitos.min()} a {peitos.max()}')


def preparar(t, edicao=2025):
    """Cópias de cada fonte e o id_inscricao no posto, sem imprimir. Para se a API tiver versões diferentes."""
    with contextlib.redirect_stdout(io.StringIO()):
        inscricoes, conf_ins = copias(t['inscricoes'], CHAVE, 'inscricoes')
        api, conf_api = copias(t['resultados'], CHAVE, 'api')
        posto, conflitos = copias(ler_posto(edicao), ['edicao', 'peito'], f'posto {edicao}')
        com, sem = achar_inscricao(posto, inscricoes)
    for nome, conf in (('inscrições', conf_ins), ('api', conf_api)):
        if len(conf):
            ids = ', '.join(conf['id_inscricao'].drop_duplicates())
            raise ReconciliacaoNaoFecha(f'{nome} com versões diferentes da mesma chave: {ids}')
    return inscricoes, api, posto, conflitos, com, sem


def tempo(valor):
    return '' if pd.isna(valor) else f' {valor}'


def passo_empilhar(t):
    _, api, posto, _, com, _ = preparar(t)
    print('O posto como chegou, empilhado embaixo da API:')
    crua = pd.concat([api, posto])
    print(f'  {len(crua)} linhas | colunas: {list(crua.columns)}')
    print(f'  numero_peito vazio: {int(crua["numero_peito"].isna().sum())} | peito vazio: {int(crua["peito"].isna().sum())}')
    print('\nO posto com o id_inscricao e as colunas da API, com a coluna fonte:')
    empilhada = empilhar(api, com)
    print(f'  {len(empilhada)} linhas | colunas: {list(empilhada.columns)}')
    print('  linhas por fonte:', empilhada['fonte'].value_counts().to_dict())
    print(f'  chaves que aparecem mais de uma vez: {int(empilhada.duplicated(CHAVE, keep=False).sum())} linhas')


def passo_sobreposicao(t):
    _, api, _, _, com, _ = preparar(t)
    iguais, diferentes = sobreposicao(empilhar(api, com))
    print(f'chaves nas duas fontes: {len(iguais) + len(diferentes)} | iguais: {len(iguais)} | diferentes: {len(diferentes)}')
    print('\ndiferentes:')
    print(diferentes.to_string(index=False))


def passo_base(t, edicao=2025):
    inscricoes, api, posto, conflitos, com, sem = preparar(t, edicao)
    empilhada = empilhar(api, com)
    iguais, diferentes = sobreposicao(empilhada)
    nas_duas = empilhada.groupby(CHAVE)['fonte'].transform('nunique') > 1
    resultados = empilhada[~nas_duas | (empilhada['fonte'] == 'api')]
    novos = resultados[resultados['fonte'] == 'posto']
    base = montar_base(inscricoes, resultados.drop(columns='fonte'))
    print('_merge da base:', base['_merge'].value_counts().to_dict())

    print('\nlinhas')
    n_ins, n_api, n_posto = len(t['inscricoes']), len(t['resultados']), len(ler_posto(edicao))
    c_ins, c_api = n_ins - len(t['inscricoes'].drop_duplicates()), n_api - len(t['resultados'].drop_duplicates())
    c_posto = n_posto - len(ler_posto(edicao).drop_duplicates())
    sob = len(iguais) + len(diferentes)
    com_res = int((base['_merge'] == 'both').sum())
    sem_res = int((base['_merge'] == 'left_only').sum())
    fechar(f'inscrições: {n_ins} - {c_ins} cópias', n_ins - c_ins, len(inscricoes))
    fechar(f'api: {n_api} - {c_api} cópias', n_api - c_api, len(api))
    fechar(f'posto: {n_posto} - {c_posto} cópia - {len(conflitos)} em conflito - {len(sem)} sem inscrição - {sob} já na api',
           n_posto - c_posto - len(conflitos) - len(sem) - sob, len(novos))
    fechar(f'resultados: {len(api)} da api + {len(novos)} do posto', len(api) + len(novos), len(resultados))
    fechar(f'base: {com_res} com resultado + {sem_res} sem resultado', com_res + sem_res, len(inscricoes))
    fechar('base com resultado igual aos resultados', com_res, len(resultados))

    print('\nvalores, por edição')
    antes = valores(api).add(valores(novos), fill_value=0).astype('int64')
    depois = valores(base[base['_merge'] == 'both'])
    print('api + novos do posto:')
    print(antes.to_string())
    print('base:')
    print(depois.to_string())
    igual = antes.equals(depois)
    print(f'  api + novos do posto igual à base: {"fecha" if igual else "NÃO FECHA"}')
    if not igual:
        raise ReconciliacaoNaoFecha('a conta dos valores por edição não fechou')

    print(f'\nnovos do posto: {len(novos)} | {", ".join(novos["id_inscricao"])}')
    print(f'sem resultado na base: {sem_res}')
    concluiu = base[(base['edicao'] == 2025) & (base['status'] == 'concluiu')]
    print(f'mulheres que concluíram em 2025: {int(concluiu["categoria"].str.startswith("F").sum())} '
          f'de {len(concluiu)} que concluíram')
    print('\npara a Lívia:')
    for peito in conflitos['peito'].drop_duplicates():
        print(f'  peito {peito} de {edicao}: anotado com versões diferentes no posto: ficou fora')
    for _, r in sem.iterrows():
        print(f'  peito {r["numero_peito"]} de {r["edicao"]}: não existe nas inscrições: ficou fora')
    for _, r in diferentes.iterrows():
        print(f'  {r["id_inscricao"]}: api {r["status_api"]}{tempo(r["tempo_oficial_api"])} | '
              f'posto {r["status_posto"]}{tempo(r["tempo_oficial_posto"])}: ficou o da api')
    return base


PASSOS = {'caio': passo_caio, 'copias': passo_copias, 'peito': passo_peito, 'empilhar': passo_empilhar,
          'sobreposicao': passo_sobreposicao, 'base': passo_base}

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Junta o posto de chegada aos resultados do triatlo e reconcilia.')
    ap.add_argument('--passo', required=True, choices=list(PASSOS))
    escolha = ap.parse_args().passo
    try:
        PASSOS[escolha](carregar())
    except (ReconciliacaoNaoFecha, ValueError) as erro:
        print(f'parei: {erro}')
        sys.exit(1)
