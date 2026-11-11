"""Olha a exportação nova da loja online antes de transformar em tabela.

    python3 olhar_json.py

Parte 1: o que o pd.read_json faz com o arquivo.
Parte 2: quais chaves aparecem em todos os pedidos e quais só em alguns.
Parte 3: o que o pd.json_normalize abre e o que ele deixa fechado.
Parte 4: pedir ao json_normalize um campo que nem todo pedido tem.
"""
import json
from collections import Counter
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
ARQUIVO = AQUI / "pedidos-online-novembro-semana-1.json"

pedidos = json.loads(ARQUIVO.read_text(encoding="utf-8"))

print("== parte 1: pd.read_json")
tabela = pd.read_json(ARQUIVO, dtype=False)
print(tabela.shape)
print("tipo de cada célula na primeira linha:")
for coluna in tabela.columns:
    print(f"  {coluna}: {type(tabela.loc[0, coluna]).__name__}")

print("== parte 2: as chaves de cada pedido")
print(len(pedidos), "pedidos")
chaves = Counter(chave for pedido in pedidos for chave in pedido)
for chave, quantos in chaves.items():
    print(f"  {chave}: em {quantos}")
print("cupom null:", sum(1 for p in pedidos if "cupom" in p and p["cupom"] is None))
print("tamanho da lista de itens:", sorted(Counter(len(p["itens"]) for p in pedidos).items()))
print("chaves da entrega:", sorted(Counter(tuple(p["entrega"]) for p in pedidos).items()))

print("== parte 3: pd.json_normalize")
aberta = pd.json_normalize(pedidos)
print(aberta.shape)
print(list(aberta.columns))
print("a coluna itens ainda tem listas:", type(aberta.loc[0, "itens"]).__name__)

print("== parte 4: meta com um campo opcional")
try:
    pd.json_normalize(pedidos, record_path="itens", meta=["id_pedido", ["cupom", "codigo"]])
except KeyError as erro:
    print("KeyError:", erro)
