"""Exercício: converter a planilha da cronometragem de 2025.

Escreva a função converter_cronometragem abaixo. Depois rode, de dentro desta pasta:

    python3 gerar.py
    python3 exercicio.py

Enquanto a função não estiver escrita, o programa para com o código 1.
Com a função escrita, ele grava conversoes_cronometragem.csv e rejeicoes_cronometragem.csv,
roda o checar_conversao e sai com 0 se a conversão passar.
"""
import sys

import pandas as pd

import checar_conversao
import conversao

# A largada foi às 6h30 de 25/05/2025. Ninguém chega antes da largada nem 24 horas depois dela.
LARGADA = '2025-05-25 06:30'
LIMITE = '2025-05-26 06:30'
STATUS = ['concluiu', 'DNF', 'DNS', 'DSQ']
TIPOS = {'numero_peito': 'Int64', 'status': 'category', 'tempo_oficial': 'timedelta64[ns]',
         'chegada': 'datetime64[ns]'}


def ler():
    """A planilha como veio, tudo texto, com a coluna linha (1 é a primeira linha de dados)."""
    tabela = pd.read_csv('cronometragem_2025.csv', dtype=str, keep_default_na=False)
    tabela.insert(0, 'linha', [str(i) for i in range(1, len(tabela) + 1)])
    return tabela


def converter_cronometragem(tabela):
    """Recebe a tabela de ler() e retorna duas tabelas: (convertida, rejeicoes).

    convertida: as mesmas linhas, na mesma ordem, com a coluna linha e as quatro colunas
    nos tipos de TIPOS. Valor que não converte fica vazio.
    rejeicoes: uma linha por valor rejeitado, com as colunas linha, coluna, valor_original e motivo.
    Célula vazia no arquivo não é rejeição.
    """
    raise NotImplementedError('falta escrever converter_cronometragem')


def main():
    tabela = ler()
    try:
        convertida, rejeicoes = converter_cronometragem(tabela)
    except NotImplementedError as e:
        print(e)
        sys.exit(1)
    rel = conversao.relatorio(tabela, convertida, rejeicoes, list(TIPOS))
    rel.to_csv('conversoes_cronometragem.csv', index=False)
    rejeicoes.to_csv('rejeicoes_cronometragem.csv', index=False)
    print(f'cronometragem_2025.csv: {len(tabela)} linhas | rejeicoes_cronometragem.csv: {len(rejeicoes)} linhas')
    print(rel.drop(columns='ajustadas').to_string(index=False))
    print('\nrejeições por motivo:')
    print(rejeicoes.groupby(['coluna', 'motivo']).size().to_string() if len(rejeicoes) else '(nenhuma)')
    problemas = checar_conversao.checar(tabela, convertida, rejeicoes, 'linha', TIPOS)
    print('\nchecar_conversao:', 'ok' if not problemas else '; '.join(problemas))
    sys.exit(1 if problemas else 0)


if __name__ == '__main__':
    main()
