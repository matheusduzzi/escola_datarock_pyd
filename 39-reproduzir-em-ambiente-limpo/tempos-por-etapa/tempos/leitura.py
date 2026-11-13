"""Leitura: os resultados da prova e a lista de categorias, na ordem do relatório."""
from pathlib import Path

import pandas as pd

PASTA_DADOS = Path(__file__).resolve().parent.parent / "dados"
ETAPAS = ["natacao_s", "t1_s", "ciclismo_s", "t2_s", "corrida_s"]
COLUNAS = ["id_atleta", "categoria", "status"] + ETAPAS


def ler_resultados(pasta=PASTA_DADOS):
    arquivo = Path(pasta) / "resultados.csv"
    if not arquivo.is_file():
        raise FileNotFoundError(f"não achei resultados.csv em {pasta}")
    tabela = pd.read_csv(arquivo)
    faltam = [c for c in COLUNAS if c not in tabela.columns]
    if faltam:
        raise ValueError(f"resultados.csv está sem as colunas {faltam}")
    return tabela


def ler_categorias(pasta=PASTA_DADOS):
    """Uma categoria por linha, na ordem em que o relatório mostra. Linha com # é comentário."""
    with open(Path(pasta) / "categorias.txt") as arquivo:
        linhas = [linha.strip() for linha in arquivo]
    return [linha for linha in linhas if linha and not linha.startswith("#")]
