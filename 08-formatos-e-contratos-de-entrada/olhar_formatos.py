"""Abre os pedidos da loja online de julho do jeito mais direto e mostra o que o pandas entendeu.

    python3 olhar_formatos.py

Cada parte repete um passo da aula. Nenhuma delas usa o contrato: é o pandas adivinhando.
"""
import pandas as pd

CSV = "pedidos-online-julho.csv"
JSON = "pedidos-online-julho.json"
OLHAR = ["id_pedido", "data_pedido", "valor", "cupom"]


def parte(titulo):
    print(f"\n== {titulo}")


parte("1. read_csv sem dizer nada")
try:
    pd.read_csv(CSV)
except UnicodeDecodeError as erro:
    print(f"UnicodeDecodeError: {erro}")

parte("2. read_csv com encoding='cp1252'")
pedidos = pd.read_csv(CSV, encoding="cp1252")
print(pedidos.shape)
print(pedidos.columns[0])

parte("3. read_csv com encoding='cp1252' e sep=';'")
pedidos = pd.read_csv(CSV, encoding="cp1252", sep=";")
print(pedidos.dtypes)
print(pedidos.loc[0, OLHAR].to_dict())

parte("4. read_json sem dizer nada")
pedidos = pd.read_json(JSON)
print(pedidos.dtypes)
print(pedidos.loc[0, OLHAR].to_dict())

parte("5. read_json com dtype=False")
pedidos = pd.read_json(JSON, dtype=False)
print(pedidos.dtypes)
print(pedidos.loc[0, OLHAR].to_dict())

parte("6. o JSON, que é UTF-8, aberto como Windows-1252")
with open(JSON, encoding="cp1252") as arquivo:
    texto = arquivo.read()
inicio = texto.index('"cidade_entrega": "S')
print(texto[inicio:inicio + 31])
