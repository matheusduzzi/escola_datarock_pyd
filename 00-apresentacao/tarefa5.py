# Tarefa 5. O Caio rodou este programa e ele parou com erro.
import csv

total = 0
with open("dados/pedidos.csv", encoding="utf-8") as arquivo:
    for linha in csv.DictReader(arquivo):
        if linha["status"] == "entregue":
            total = total + linha["valor"]

print("Total entregue:", total)
