"""Monta as parciais do triatlo nos dois formatos, largo e longo.

Uso, de dentro da pasta da aula:
    python3 tabelas.py

Lê ../dados/triatlo/api_resultados.json, escreve parciais_largo.csv e parciais_longo.csv
nesta pasta e mostra a mesma inscrição nas duas tabelas. Os resultados entram como chegam
no arquivo, com os repetidos. Parcial vazia fica vazia (<NA>), nunca zero.
"""
import json
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
DADOS = AQUI.parent / 'dados' / 'triatlo'
ETAPAS = ['natacao', 't1', 'ciclismo', 't2', 'corrida']
COLUNAS = ['edicao', 'id_inscricao', 'numero_peito', 'status']


def segundos(texto):
    """'1:14:19' vira 4459. Parcial vazia (None) continua vazia."""
    if texto is None:
        return None
    h, m, s = (int(x) for x in texto.split(':'))
    return h * 3600 + m * 60 + s


def resultados():
    return json.loads((DADOS / 'api_resultados.json').read_text(encoding='utf-8'))


def ler_largo():
    """Uma linha por resultado do arquivo, uma coluna por etapa."""
    linhas = []
    for r in resultados():
        linha = {c: r[c] for c in COLUNAS}
        for etapa in ETAPAS:
            linha[etapa] = segundos(r['parciais'][etapa])
        linhas.append(linha)
    largo = pd.DataFrame(linhas)
    largo[ETAPAS] = largo[ETAPAS].astype('Int64')
    return largo


def ler_longo():
    """Uma linha por resultado e etapa: a etapa vira valor da coluna 'etapa'."""
    linhas = []
    for r in resultados():
        for etapa in ETAPAS:
            linha = {c: r[c] for c in COLUNAS}
            linha['etapa'] = etapa
            linha['segundos'] = segundos(r['parciais'][etapa])
            linhas.append(linha)
    longo = pd.DataFrame(linhas)
    longo['segundos'] = longo['segundos'].astype('Int64')
    return longo


if __name__ == '__main__':
    largo, longo = ler_largo(), ler_longo()
    largo.to_csv(AQUI / 'parciais_largo.csv', index=False)
    longo.to_csv(AQUI / 'parciais_longo.csv', index=False)
    print(f'largo: {largo.shape[0]} linhas x {largo.shape[1]} colunas -> parciais_largo.csv')
    print(f'longo: {longo.shape[0]} linhas x {longo.shape[1]} colunas -> parciais_longo.csv')
    for inscricao in ['2025-0001', '2025-0016']:
        print(f'\nA inscrição {inscricao} no largo:')
        print(largo[largo['id_inscricao'] == inscricao].to_string(index=False))
        print(f'\nA inscrição {inscricao} no longo:')
        print(longo[longo['id_inscricao'] == inscricao].to_string(index=False))
