"""Leva a tabela longa de 2025 para a larga de cinco jeitos e mostra o que cada um faz.

Uso, de dentro da pasta da aula:
    python3 pivotar.py --jeito pivot           # pivot direto: para com erro (código 1)
    python3 pivotar.py --jeito media           # pivot_table com o padrão, a média
    python3 pivotar.py --jeito soma            # pivot_table com aggfunc='sum'
    python3 pivotar.py --jeito sem-repetidos   # tira as linhas repetidas e usa pivot
    python3 pivotar.py --jeito peito           # as duas edições, com o número de peito como chave

Em todos, a pergunta é a mesma: uma linha por inscrição, uma coluna por etapa, o tempo em segundos.
Olhe três inscrições: 2025-0079 (resultado repetido no arquivo), 2025-0016 (DNF, sem corrida)
e 2025-0052 (DNS, não largou).
"""
import argparse
import sys

import pandas as pd

from tabelas import ETAPAS, ler_longo

OLHAR = {'2025-0079': 'repetido', '2025-0016': 'DNF', '2025-0052': 'DNS'}


def mostrar(largo, longo):
    dns = longo.loc[longo['status'] == 'DNS', 'id_inscricao'].unique()
    print(f'linhas: {len(largo)} | inscrições no longo: {longo["id_inscricao"].nunique()} '
          f'| DNS na tabela: {sum(i in largo.index for i in dns)} de {len(dns)}')
    olhar = [i for i in OLHAR if i in largo.index]
    tabela = largo.loc[olhar, ETAPAS].copy()
    tabela.index = [f'{i} ({OLHAR[i]})' for i in olhar]
    print(tabela.to_string())
    fora = [f'{i} ({OLHAR[i]})' for i in OLHAR if i not in largo.index]
    if fora:
        print('fora da tabela: ' + ', '.join(fora))


def main():
    p = argparse.ArgumentParser(description='Leva a tabela longa para a larga de cinco jeitos.')
    p.add_argument('--jeito', required=True, choices=['pivot', 'media', 'soma', 'sem-repetidos', 'peito'])
    jeito = p.parse_args().jeito

    longo = ler_longo()
    if jeito == 'peito':
        sem_rep = longo.drop_duplicates()
        largo = sem_rep.pivot_table(index='numero_peito', columns='etapa', values='segundos')[ETAPAS]
        por_edicao = sem_rep.groupby('edicao')['numero_peito'].nunique()
        print(f'números de peito em 2024: {por_edicao[2024]} | em 2025: {por_edicao[2025]} '
              f'| linhas na tabela: {len(largo)}')
        nat = sem_rep[(sem_rep['numero_peito'] == 101) & (sem_rep['etapa'] == 'natacao')]
        print('\nnatação do peito 101 no longo:')
        print(nat[['edicao', 'id_inscricao', 'numero_peito', 'segundos']].to_string(index=False))
        print('\nnatação do peito 101 na tabela larga:', largo.loc[101, 'natacao'])
        return 0

    longo = longo[longo['edicao'] == 2025]
    print(f'longo de 2025: {len(longo)} linhas')
    if jeito == 'pivot':
        try:
            longo.pivot(index='id_inscricao', columns='etapa', values='segundos')
        except ValueError as erro:
            print(f'ValueError: {erro}')
            return 1
    elif jeito == 'media':
        largo = longo.pivot_table(index='id_inscricao', columns='etapa', values='segundos')[ETAPAS]
        mostrar(largo, longo)
    elif jeito == 'soma':
        largo = longo.pivot_table(index='id_inscricao', columns='etapa', values='segundos', aggfunc='sum')[ETAPAS]
        mostrar(largo, longo)
    else:
        sem_rep = longo.drop_duplicates()
        print(f'linhas repetidas tiradas: {len(longo) - len(sem_rep)}')
        largo = sem_rep.pivot(index='id_inscricao', columns='etapa', values='segundos')[ETAPAS]
        mostrar(largo, longo)
        print('parciais vazias por etapa: '
              + ', '.join(f'{e} {n}' for e, n in largo.isna().sum().items()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
