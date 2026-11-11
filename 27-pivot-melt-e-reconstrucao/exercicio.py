"""Exercício da aula «Pivot, melt e reconstrução»: o histórico dos atletas, ida e volta.

Uso, de dentro da pasta da aula:
    python3 exercicio.py

Escreva as duas funções abaixo. O programa lê historico_largo.csv, leva para o formato longo
com a sua para_longo, volta com a sua para_largo e roda a conferência de ida e volta.
Enquanto as funções não estiverem escritas, ele para com o código 1 e diz qual falta.
"""
import sys
from pathlib import Path

import pandas as pd

from conferir import ida_e_volta

AQUI = Path(__file__).resolve().parent


def ler():
    """A planilha da federação, com os tempos como números inteiros que aceitam vazio."""
    planilha = pd.read_csv(AQUI / 'historico_largo.csv')
    tempos = [c for c in planilha.columns if c != 'id_atleta']
    return planilha.astype({c: 'Int64' for c in tempos})


def para_longo(largo):
    """Retorna uma tabela com as colunas id_atleta, etapa, edicao e segundos.

    A etapa e a edição estão juntas no nome da coluna (natacao_2024). No longo, cada uma
    vai para a sua coluna, e a edição é um número.
    """
    raise NotImplementedError('falta escrever para_longo')


def para_largo(longo):
    """Retorna a planilha de volta: uma linha por atleta, as colunas com os mesmos nomes e na mesma ordem."""
    raise NotImplementedError('falta escrever para_largo')


def main():
    largo = ler()
    print(f'historico_largo.csv: {largo.shape[0]} linhas x {largo.shape[1]} colunas')
    try:
        longo = para_longo(largo)
        print(f'longo: {longo.shape[0]} linhas | colunas: {", ".join(longo.columns)}')
        print('tipos: ' + ', '.join(f'{c} {t}' for c, t in longo.dtypes.items()))
        volta = para_largo(longo)
    except NotImplementedError as erro:
        print(erro)
        return 1
    print()
    return 0 if ida_e_volta(largo, volta, ['id_atleta']) else 1


if __name__ == '__main__':
    sys.exit(main())
