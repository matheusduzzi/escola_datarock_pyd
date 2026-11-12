"""Lê os resultados do triatlo numa tabela do pandas, como eles chegam da API.

Uso, de outro programa desta pasta:
    from resultados import ler

Lê ../dados/triatlo/api_resultados.json e junta o id_atleta pelas inscrições das duas edições.
Uma linha por resultado do arquivo, com as cópias que a API repete. As parciais ficam em
segundos; a parcial que não existe fica vazia, do jeito que o pandas escolher.
"""
import json
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
DADOS = AQUI.parent / 'dados' / 'triatlo'
ETAPAS = ['natacao', 't1', 'ciclismo', 't2', 'corrida']


def segundos(texto):
    """'6:02:35' vira 21755. Parcial vazia (None) continua None."""
    if texto is None:
        return None
    h, m, s = (int(x) for x in texto.split(':'))
    return h * 3600 + m * 60 + s


def inscricoes():
    """id_inscricao e id_atleta das duas edições, sem as linhas repetidas do arquivo de 2025."""
    i24 = pd.read_csv(DADOS / 'inscricoes_2024.csv', dtype={'id_inscricao': str})
    i25 = pd.read_csv(DADOS / 'inscricoes_2025.csv', sep=';', dtype={'id_inscricao': str})
    return pd.concat([i24, i25], ignore_index=True).drop_duplicates()[['id_inscricao', 'id_atleta']]


def ler():
    """Uma linha por resultado do arquivo da API, com as cópias, e o id_atleta de cada um."""
    linhas = []
    for r in json.loads((DADOS / 'api_resultados.json').read_text(encoding='utf-8')):
        linha = {c: r[c] for c in ['edicao', 'id_inscricao', 'numero_peito', 'status']}
        for etapa in ETAPAS:
            linha[etapa] = segundos(r['parciais'][etapa])
        linhas.append(linha)
    tabela = pd.DataFrame(linhas)
    return tabela.merge(inscricoes(), on='id_inscricao', how='left', validate='many_to_one')
