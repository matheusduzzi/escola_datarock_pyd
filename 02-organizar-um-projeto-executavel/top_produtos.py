# Os produtos mais vendidos do 1º trimestre, para a compra do próximo pedido ao fornecedor.
# Caio, financeiro. Para mudar o trimestre ou a quantidade, eu troco aqui embaixo.
import pandas as pd

pedidos = pd.read_csv("C:/Users/caio/Documents/loja/pedidos.csv")
produtos = pd.read_csv("C:/Users/caio/Documents/loja/produtos.csv")

inicio = "2026-01"
fim = "2026-03"
quantos = 5

pedidos["mes"] = pedidos["data_pedido"].str[:7]
pedidos = pedidos[(pedidos["status"] == "entregue") & (pedidos["mes"] >= inicio) & (pedidos["mes"] <= fim)]
base = pedidos.merge(produtos[["id_produto", "nome", "categoria"]], on="id_produto")
ranking = base.groupby(["id_produto", "nome", "categoria"]).agg(
    unidades=("quantidade", "sum"), pedidos=("id_pedido", "count"), faturamento=("valor", "sum"))
ranking = ranking.sort_values(["unidades", "faturamento"], ascending=False).round(2)
top = ranking.head(quantos)

print(top)
top.to_csv("top.csv")
