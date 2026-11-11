"""Responde a gerente com as duas tabelas do separar_pedidos.py.

    python3 resumo_semana.py

Lê saida/pedidos.csv e saida/itens.csv e o cadastro de produtos da loja em ../dados/loja.
"""
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "saida"
PRODUTOS = AQUI.parent / "dados" / "loja" / "produtos.csv"

pedidos = pd.read_csv(SAIDA / "pedidos.csv", dtype={"id_pedido": str})
itens = pd.read_csv(SAIDA / "itens.csv", dtype={"id_pedido": str})
produtos = pd.read_csv(PRODUTOS)

vendidos = pedidos[pedidos["status"] != "cancelado"]
print("pedidos da semana:", len(pedidos), "| cancelados:", (pedidos["status"] == "cancelado").sum())
print("faturamento da semana:", round(vendidos["valor_total"].sum(), 2))

com_pedido = itens.merge(pedidos[["id_pedido", "status", "cidade"]], on="id_pedido",
                         how="left", validate="many_to_one")
print("itens antes e depois de juntar com os pedidos:", len(itens), len(com_pedido))

por_produto = (com_pedido[com_pedido["status"] != "cancelado"]
               .groupby("id_produto")
               .agg(unidades=("quantidade", "sum"), valor_itens=("valor_item", "sum"))
               .reset_index()
               .merge(produtos[["id_produto", "nome"]], on="id_produto", validate="one_to_one")
               .sort_values(["valor_itens", "id_produto"], ascending=[False, True]))
print("os 5 produtos que mais venderam, em valor dos itens (antes do cupom e do frete):")
print(por_produto.head(5)[["nome", "unidades", "valor_itens"]].round(2).to_string(index=False))

print("pedidos com cupom:", vendidos["cupom"].notna().sum(), "de", len(vendidos))
print(vendidos["cupom"].value_counts().to_string())
