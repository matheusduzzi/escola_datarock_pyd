"""Testa o conferir.py: ele acusa o que deveria e aceita o que deveria?

Uso, de dentro da pasta da aula:
    python3 testar_conferir.py

Cada caso estraga uma cópia da tabela larga de um jeito (são nove) e diz o que o conferir.py deveria
responder. Sai com código 1 se algum caso der diferente do esperado.
"""
import sys

import pandas as pd

from conferir import ida_e_volta
from tabelas import CHAVE, ETAPAS, ler_largo


def casos(largo):
    yield 'linhas embaralhadas e colunas em outra ordem', True, \
        largo.sample(frac=1, random_state=1)[list(reversed(largo.columns))]
    yield 'uma linha a menos', False, largo.iloc[:-1]
    yield 'uma linha repetida', False, pd.concat([largo, largo.iloc[[0]]])
    zero = largo.copy()
    zero.loc[zero['id_inscricao'] == '2025-0016', 'corrida'] = 0
    yield 'o vazio da corrida do DNF virou 0', False, zero
    um_seg = largo.copy()
    um_seg.loc[um_seg['id_inscricao'] == '2025-0001', 'natacao'] += 1
    yield 'um segundo a mais numa natação', False, um_seg
    yield 'tempos com casa decimal (float)', False, largo.astype({e: 'float64' for e in ETAPAS})
    yield 'sem a coluna status', False, largo.drop(columns='status')
    yield 'uma coluna a mais', False, largo.assign(etapa='natacao')
    dois_niveis = largo.copy()
    dois_niveis.columns = pd.MultiIndex.from_tuples([(c, '') for c in largo.columns])
    yield 'cabeçalho em dois níveis, como sai de um pivot com duas colunas', False, dois_niveis


def main():
    largo = ler_largo()
    erros = 0
    for nome, esperado, volta in casos(largo):
        igual = ida_e_volta(largo, volta, CHAVE, mostrar=False)
        certo = igual == esperado
        erros += not certo
        print(f'{"ok   " if certo else "FALHA"} {nome}: esperado {"igual" if esperado else "diferente"}, '
              f'conferir disse {"igual" if igual else "diferente"}')
    print(f'{erros} caso(s) com resposta errada')
    return 1 if erros else 0


if __name__ == '__main__':
    sys.exit(main())
