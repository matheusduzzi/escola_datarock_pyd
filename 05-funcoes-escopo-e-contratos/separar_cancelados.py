"""Pedido 2 da prática guiada: escreva o contrato da função separar_cancelados antes de rodar."""
import csv
from pathlib import Path

PEDIDOS = Path(__file__).resolve().parent.parent / "dados" / "loja" / "pedidos.csv"


def separar_cancelados(pedidos):
    cancelados = []
    for pedido in list(pedidos):
        if pedido["status"] == "cancelado":
            pedidos.remove(pedido)
            cancelados.append(pedido)
    return cancelados


with open(PEDIDOS, encoding="utf-8", newline="") as arquivo:
    junho = [p for p in csv.DictReader(arquivo) if p["data_pedido"].startswith("2026-06")]

print("Pedidos de junho antes:", len(junho))
cancelados = separar_cancelados(junho)
print("Cancelados:", len(cancelados))
print("Pedidos de junho depois:", len(junho))
print("Primeiro cancelado:", cancelados[0]["id_pedido"], cancelados[0]["data_pedido"])
