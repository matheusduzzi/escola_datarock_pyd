# Entregas por cidade no 2º trimestre, para a reunião da gerente.
# Caio, financeiro. Rodo no meu computador toda segunda.
import pandas as pd

pedidos = pd.read_csv("C:/Users/caio/Documents/loja/pedidos.csv")
clientes = pd.read_csv("C:/Users/caio/Documents/loja/clientes.csv")

pedidos = pedidos[pedidos["status"] == "entregue"]
pedidos = pedidos[(pedidos["data_pedido"] >= "2026-04-01") & (pedidos["data_pedido"] <= "2026-06-30")]

base = pedidos.merge(clientes[["id_cliente", "cidade"]], on="id_cliente")
resumo = base.groupby("cidade").agg(pedidos=("id_pedido", "count"), faturamento=("valor", "sum"))
resumo = resumo.sort_values("faturamento", ascending=False).round(2)

print(resumo)
print("Total:", round(resumo["faturamento"].sum(), 2))
resumo.to_csv("resumo.csv")
