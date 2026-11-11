"""Leva a tabela larga para a longa e volta, de cinco jeitos, e confere se a volta é igual.

Uso, de dentro da pasta da aula:
    python3 ida_e_volta.py --jeito certo               # melt com a chave e os atributos, pivot de volta
    python3 ida_e_volta.py --jeito sem-id              # melt só com id_inscricao, como a IA sugeriu
    python3 ida_e_volta.py --jeito sem-vazio           # tira as linhas sem tempo do longo antes de voltar
    python3 ida_e_volta.py --jeito reconstruir         # guarda duas tabelas e reconstrói a larga
    python3 ida_e_volta.py --jeito oficial-pela-soma   # joga fora o tempo oficial e recalcula pela soma

Em todos, a pergunta é a mesma: se eu guardar só o formato longo, a página do Caio sai igual?
"""
import argparse
import sys

from conferir import ida_e_volta
from tabelas import ATRIBUTOS, CHAVE, COLUNAS, ETAPAS, ler_largo

ID = CHAVE + ATRIBUTOS
OLHAR = '2025-0016'


def ida(largo):
    """Largo para longo: a etapa sai do nome da coluna e vira valor da coluna 'etapa'."""
    return largo.melt(id_vars=ID, value_vars=ETAPAS, var_name='etapa', value_name='segundos')


def volta(longo):
    """Longo para largo: cada etapa volta a ser coluna, na ordem da tabela original."""
    largo = longo.pivot(index=ID, columns='etapa', values='segundos').reset_index()
    largo.columns.name = None
    return largo[COLUNAS]


def main():
    p = argparse.ArgumentParser(description='Ida e volta entre o formato largo e o longo.')
    p.add_argument('--jeito', required=True,
                   choices=['certo', 'sem-id', 'sem-vazio', 'reconstruir', 'oficial-pela-soma'])
    jeito = p.parse_args().jeito
    largo = ler_largo()

    if jeito == 'certo':
        longo = ida(largo)
        print(f'largo: {len(largo)} linhas | longo: {len(longo)} linhas x {longo.shape[1]} colunas')
        print(f'\nA inscrição {OLHAR} no longo:')
        print(longo[longo['id_inscricao'] == OLHAR].to_string(index=False))
        print()
        ida_e_volta(largo, volta(longo), CHAVE)

    elif jeito == 'sem-id':
        longo = largo.melt(id_vars='id_inscricao')
        print(f'longo: {len(longo)} linhas | colunas: {", ".join(longo.columns)}')
        print('valores da coluna variable: ' + ', '.join(longo['variable'].unique()))
        print(f'tipo da coluna value: {longo["value"].dtype}')
        print(f'\nA inscrição {OLHAR} no longo:')
        print(longo[longo['id_inscricao'] == OLHAR].to_string(index=False))
        de_volta = longo.pivot(index='id_inscricao', columns='variable', values='value').reset_index()
        de_volta.columns.name = None
        print()
        ida_e_volta(largo, de_volta, CHAVE)

    elif jeito == 'sem-vazio':
        longo = ida(largo)
        cheio = longo.dropna(subset=['segundos'])
        print(f'longo: {len(longo)} linhas | sem as linhas vazias: {len(cheio)} linhas')
        de_volta = volta(cheio)
        sumiram = sorted(set(largo['id_inscricao']) - set(de_volta['id_inscricao']))
        status = largo[largo['id_inscricao'].isin(sumiram)]['status'].value_counts()
        print('status de quem sumiu: ' + ', '.join(f'{s} {n}' for s, n in status.items()))
        print(f'a {OLHAR} (DNF) na volta: corrida = {de_volta.loc[de_volta["id_inscricao"] == OLHAR, "corrida"].iloc[0]}')
        print()
        ida_e_volta(largo, de_volta, CHAVE)

    elif jeito == 'reconstruir':
        resultados = largo[ID]
        parciais = ida(largo)[CHAVE + ['etapa', 'segundos']].dropna(subset=['segundos'])
        print(f'resultados: {len(resultados)} linhas x {resultados.shape[1]} colunas ({", ".join(ID)})')
        print(f'parciais: {len(parciais)} linhas x {parciais.shape[1]} colunas ({", ".join(parciais.columns)})')
        etapas = parciais.pivot(index=CHAVE, columns='etapa', values='segundos').reset_index()
        etapas.columns.name = None
        de_volta = resultados.merge(etapas, on=CHAVE, how='left', validate='one_to_one')[COLUNAS]
        print(f'depois do merge com how="left": {len(de_volta)} linhas')
        print()
        ida_e_volta(largo, de_volta, CHAVE)

    else:
        longo = largo.drop(columns='tempo_oficial').melt(
            id_vars=CHAVE + ['numero_peito', 'status'], value_vars=ETAPAS, var_name='etapa', value_name='segundos')
        de_volta = longo.pivot(index=CHAVE + ['numero_peito', 'status'], columns='etapa', values='segundos').reset_index()
        de_volta.columns.name = None
        de_volta['tempo_oficial'] = de_volta[ETAPAS].sum(axis=1)
        ida_e_volta(largo, de_volta[COLUNAS], CHAVE)
        de_volta['tempo_oficial'] = de_volta[ETAPAS].sum(axis=1, min_count=5)
        juntos = largo.merge(de_volta[CHAVE + ['tempo_oficial']], on=CHAVE, suffixes=('', '_soma'))
        a, b = juntos['tempo_oficial'], juntos['tempo_oficial_soma']
        dif = (a.isna() != b.isna()) | (a.notna() & b.notna() & (a != b))
        print('\ncom sum(min_count=5), a soma só sai quando as cinco parciais existem')
        print(f'  células diferentes em tempo_oficial: {int(dif.sum())}')
        print('  por status: ' + ', '.join(f'{s} {n}' for s, n in juntos.loc[dif, 'status'].value_counts().items()))
        bate = juntos[a.notna() & b.notna()]
        print(f'  quem tem as duas coisas: {len(bate)} | soma igual ao tempo oficial: {int((bate["tempo_oficial"] == bate["tempo_oficial_soma"]).sum())}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
