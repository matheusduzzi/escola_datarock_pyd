"""Cálculo: tempo total e medianas por categoria. Recebe tabelas e retorna tabelas."""
import pandas as pd

from tempos.leitura import ETAPAS


def com_total(resultados):
    """Acrescenta total_s, a soma das três etapas e das duas transições.

    Parcial vazia não é zero: se faltar uma, o total fica vazio também.
    """
    tabela = resultados.copy()
    tabela["total_s"] = tabela[ETAPAS].sum(axis=1, min_count=len(ETAPAS))
    return tabela


def com_transicoes(resultados):
    """Acrescenta transicoes_s, a soma de T1 e T2."""
    tabela = resultados.copy()
    tabela["transicoes_s"] = tabela["t1_s"] + tabela["t2_s"]
    return tabela


def por_categoria(resultados, categorias):
    """Uma linha por categoria, na ordem da lista.

    Medianas, em segundos, de quem terminou a prova, e quantos não terminaram.
    """
    terminou = com_transicoes(com_total(resultados[resultados["status"] == "terminou"]))
    terminou["categoria"] = pd.Categorical(terminou["categoria"], categories=categorias, ordered=True)
    tabela = terminou.groupby("categoria", observed=True).agg(
        atletas=("id_atleta", "count"),
        natacao=("natacao_s", "median"),
        ciclismo=("ciclismo_s", "median"),
        corrida=("corrida_s", "median"),
        transicoes=("transicoes_s", "median"),
        total=("total_s", "median"),
    )
    tabela["nao_terminaram"] = len(resultados) - tabela["atletas"]
    tabela.index = tabela.index.astype(str)
    return tabela


def relogio(segundos):
    """3725 vira 1:02:05."""
    segundos = int(round(segundos))
    return f"{segundos // 3600}:{segundos % 3600 // 60:02d}:{segundos % 60:02d}"
