"""O programa do Caio: um pedido de avaliação para cada pedido entregue do export de junho."""
import json

with open("pedidos-junho.json", encoding="utf-8") as arquivo:
    registros = json.load(arquivo)

entregues = [r for r in registros if r["status"] == "entregue"]

print("Registros no export:", len(registros))
print("Pedidos de avaliação para mandar:", len(entregues))
