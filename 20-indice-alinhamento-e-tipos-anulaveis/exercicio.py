"""Os cinco casos do exercício. Escreva a sua previsão na folha antes de rodar cada um.

Uso, de dentro da pasta da aula:
    python3 exercicio.py A
    (e B, C, D, E)

Cada caso imprime o código e o que o pandas retorna. Tempos de corrida em minutos, com o índice
no id_atleta. O atleta 47 aparece duas vezes em 2024, como a cópia que a API repete.
"""
import sys

import pandas as pd

r24 = pd.Series([281, 283, 302], index=[47, 47, 52])
r25 = pd.Series([290, 296, 315], index=[47, 52, 60])


def caso_a():
    print('r25 - r24')
    print(r25 - r24)


def caso_b():
    print('r25.to_numpy() - r24.to_numpy()')
    print(r25.to_numpy() - r24.to_numpy())
    print('r25.to_numpy() - r24[~r24.index.duplicated()].to_numpy()')
    try:
        print(r25.to_numpy() - r24[~r24.index.duplicated()].to_numpy())
    except ValueError as erro:
        print(f'ValueError: {erro}')


def caso_c():
    tabela = pd.DataFrame({'corrida_2025': r25})
    tabela['corrida_2024'] = r24[~r24.index.duplicated()]
    print("tabela = pd.DataFrame({'corrida_2025': r25})")
    print("tabela['corrida_2024'] = r24[~r24.index.duplicated()]")
    print(tabela)
    print(tabela.dtypes.to_string())


def caso_d():
    unico = r24[~r24.index.duplicated()]
    dif = r25 - unico
    print('unico = r24[~r24.index.duplicated()]')
    print('dif = r25 - unico')
    print(f'len(dif) -> {len(dif)}')
    print(f'dif.sum() -> {dif.sum()}')
    print(f'dif.sum(min_count=3) -> {dif.sum(min_count=3)}')
    print(f'(dif == dif).sum() -> {(dif == dif).sum()}')


def caso_e():
    unico = r24[~r24.index.duplicated()].astype('Int64')
    dif = r25.astype('Int64') - unico
    print("unico = r24[~r24.index.duplicated()].astype('Int64')")
    print("dif = r25.astype('Int64') - unico")
    print(dif)
    pioraram = dif > 0
    print(f'(dif > 0).sum() -> {pioraram.sum()}')
    print(f'r25[dif > 0] ->\n{r25[pioraram]}')


CASOS = {'A': caso_a, 'B': caso_b, 'C': caso_c, 'D': caso_d, 'E': caso_e}

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1].upper() not in CASOS:
        sys.exit('uso: python3 exercicio.py A (ou B, C, D, E)')
    CASOS[sys.argv[1].upper()]()
