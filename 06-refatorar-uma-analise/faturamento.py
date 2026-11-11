"""Faturamento dos pedidos entregues da Loja Exemplo, por mês e categoria.

Cada função recebe tudo o que usa pelos parâmetros e retorna um resultado novo.
Nenhuma lê variável solta nem altera a tabela que recebeu.
"""
import pandas as pd


def ler_base(pasta_dados):
    """Lê pedidos e produtos da pasta da Loja Exemplo."""
    pedidos = pd.read_csv(pasta_dados / "pedidos.csv")
    produtos = pd.read_csv(pasta_dados / "produtos.csv")
    return pedidos, produtos


def entregues_com_categoria(pedidos, produtos):
    """Pedidos entregues, com a categoria do produto e o mês no formato AAAA-MM."""
    entregues = pedidos[pedidos["status"] == "entregue"]
    base = entregues.merge(produtos[["id_produto", "categoria"]], on="id_produto")
    return base.assign(mes=base["data_pedido"].str[:7])


def no_periodo(base, inicio, fim):
    """Só os meses de inicio a fim, os dois incluídos (AAAA-MM)."""
    return base[(base["mes"] >= inicio) & (base["mes"] <= fim)]


def por_mes_e_categoria(base):
    """Soma do valor por mês (linhas) e categoria (colunas)."""
    tabela = base.pivot_table(index="mes", columns="categoria", values="valor", aggfunc="sum")
    return tabela.round(2)
