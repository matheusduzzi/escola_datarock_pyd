"""Exercício: a série diária de entregas da transportadora.

Escreva as duas funções abaixo. Depois rode, de dentro desta pasta:

    python3 gerar.py
    python3 exercicio.py

Enquanto as funções não estiverem escritas, o programa para com o código 1.
Com as funções escritas, ele grava serie_entregas.csv, roda o checar_serie e sai com 0 se a série passar.
"""
import sys

import pandas as pd

import checar_serie

FUSO = 'America/Sao_Paulo'
INICIO, FIM = '2026-01-01', '2026-06-30'


def ler_entregas():
    """Lê entregas.csv e retorna a tabela com uma coluna nova, entregue_sp:
    o instante de cada entrega no fuso de São Paulo."""
    entregas = pd.read_csv('entregas.csv')
    raise NotImplementedError('falta escrever ler_entregas')


def serie_entregas(entregas):
    """Recebe a tabela de ler_entregas e retorna a série diária: uma linha por dia de INICIO a FIM,
    com as colunas dia (AAAA-MM-DD, no relógio de São Paulo), entregas e cobertura
    ('com dado' ou 'sem dado'). Nos dias sem dado, entregas fica vazio."""
    raise NotImplementedError('falta escrever serie_entregas')


def main():
    try:
        entregas = ler_entregas()
        serie = serie_entregas(entregas)
    except NotImplementedError as e:
        print(e)
        sys.exit(1)
    print(f'entregas lidas: {len(entregas)} | tipo de entregue_sp: {entregas["entregue_sp"].dtype}')
    dia = entregas['entregue_sp'].dt.strftime('%Y-%m-%d')
    no_semestre = dia.between(INICIO, FIM).sum()
    print(f'entregas com dia de {INICIO} a {FIM}: {no_semestre} | depois de {FIM}: {(dia > FIM).sum()}')
    serie.to_csv('serie_entregas.csv', index=False)
    print(f'serie_entregas.csv: {len(serie)} linhas | colunas: {", ".join(serie.columns)}')
    print('cobertura:', ', '.join(f'{k} {v}' for k, v in serie['cobertura'].value_counts().items()))
    print(f'soma de entregas na série: {int(pd.to_numeric(serie["entregas"]).sum())}')
    problemas = checar_serie.checar(serie, INICIO, FIM, medidas=['entregas'], cobertura='cobertura',
                                    sem_dado={'sem dado'})
    print('checar_serie:', 'ok' if not problemas else '; '.join(problemas))
    sys.exit(1 if problemas else 0)


if __name__ == '__main__':
    main()
