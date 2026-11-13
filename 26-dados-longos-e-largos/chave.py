"""Diz se um conjunto de colunas é chave de uma tabela: uma linha para cada combinação.

Uso, de dentro da pasta da aula:
    python3 chave.py ARQUIVO COLUNA [COLUNA ...]

Exemplos:
    python3 chave.py parciais_largo.csv edicao id_inscricao
    python3 chave.py parciais_longo.csv edicao id_inscricao etapa
    python3 chave.py ../dados/triatlo/inscricoes_2025.csv id_inscricao

O separador (vírgula ou ponto e vírgula) é descoberto pelo pandas. Arquivo que não existe, ou
coluna que não existe no arquivo, para com o código 2 e diz o que faltou.
"""
import sys
from pathlib import Path

import pandas as pd


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    arquivo, colunas = argv[0], argv[1:]
    if not Path(arquivo).is_file():
        print(f'arquivo não encontrado: {arquivo}')
        print('as duas tabelas da aula saem do python3 tabelas.py, rodado nesta pasta')
        return 2
    tabela = pd.read_csv(arquivo, sep=None, engine='python', dtype=str)
    faltando = [c for c in colunas if c not in tabela.columns]
    if faltando:
        print(f'coluna que não existe em {arquivo}: {", ".join(faltando)}')
        print(f'colunas do arquivo: {", ".join(tabela.columns)}')
        return 2

    repetida = tabela.duplicated(subset=colunas, keep=False)
    combinacoes = len(tabela.drop_duplicates(subset=colunas))
    print(f'arquivo: {arquivo} | linhas: {len(tabela)}')
    print(f'chave testada: {" + ".join(colunas)}')
    print(f'combinações diferentes: {combinacoes}')
    if not repetida.any():
        print('é chave: cada combinação aparece em uma linha só')
        return 0

    grupos = tabela[repetida].groupby(colunas, dropna=False)
    iguais = all(len(g.drop_duplicates()) == 1 for _, g in grupos)
    print(f'não é chave: {int(repetida.sum())} linhas dividem {grupos.ngroups} combinações')
    print('as linhas de cada combinação repetida são iguais em todas as colunas: '
          + ('sim' if iguais else 'não, há valores diferentes'))
    print('primeiras combinações repetidas:')
    print(tabela[repetida].sort_values(colunas, kind='stable').head(6).fillna('').to_string(index=False))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
