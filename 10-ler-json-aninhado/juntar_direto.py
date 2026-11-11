"""O jeito direto: abre a lista de itens e leva junto os campos do pedido.

    python3 juntar_direto.py

Roda sem erro. A aula mostra por que o faturamento sai errado.
"""
import json
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
ARQUIVO = AQUI / "pedidos-online-novembro-semana-1.json"

pedidos = json.loads(ARQUIVO.read_text(encoding="utf-8"))
itens = pd.json_normalize(pedidos, record_path="itens", meta=["id_pedido", "status", "valor_total"])
vendidos = itens[itens["status"] != "cancelado"]

print(len(pedidos), "pedidos no arquivo")
print(len(itens), "linhas na tabela")
print(itens["id_pedido"].nunique(), "pedidos na tabela")
print("faturamento da semana:", round(vendidos["valor_total"].sum(), 2))
