"""Os três pedidos da prática guiada. Escreva a sua previsão antes de rodar cada um.

Uso, de dentro da pasta da aula:
    python3 prever.py 1
    python3 prever.py 2
    python3 prever.py 3

Cada pedido imprime o código e o que o pandas retorna. Tempos de ciclismo em minutos, com o
índice no número de peito.
"""
import sys

import pandas as pd

c24 = pd.Series([362, 405, 390], index=[101, 102, 103])
c25 = pd.Series([371, 398, 410], index=[103, 101, 105])


def pedido_1():
    print('c25 - c24')
    print(c25 - c24)


def pedido_2():
    print('c25.sub(c24, fill_value=0)')
    print(c25.sub(c24, fill_value=0))


def pedido_3():
    dif = c25 - c24
    print('dif = c25 - c24')
    print(f'(dif < 0).sum()    -> {(dif < 0).sum()}')
    print(f'(~(dif < 0)).sum() -> {(~(dif < 0)).sum()}')
    dif = c25.astype('Int64') - c24.astype('Int64')
    print("com astype('Int64'):")
    print(f'(dif < 0).sum()    -> {(dif < 0).sum()}')
    print(f'(~(dif < 0)).sum() -> {(~(dif < 0)).sum()}')
    print(f'(dif < 0).isna().sum() -> {(dif < 0).isna().sum()}')


PEDIDOS = {'1': pedido_1, '2': pedido_2, '3': pedido_3}

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in PEDIDOS:
        sys.exit('uso: python3 prever.py 1 (ou 2, ou 3)')
    PEDIDOS[sys.argv[1]]()
