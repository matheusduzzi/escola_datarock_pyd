"""Ticket médio do mês, como o Caio deixou."""
import csv
from pathlib import Path

PEDIDOS = Path(__file__).resolve().parent.parent / "dados" / "loja" / "pedidos.csv"
MES = "2026-05"


def ler_pedidos(caminho):
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def ticket_medio(pedidos, sem_valor=[]):
    total = 0
    contados = 0
    for pedido in pedidos:
        if pedido["status"] != "entregue" or not pedido["data_pedido"].startswith(MES):
            continue
        if pedido["valor"] == "":
            sem_valor.append(pedido["id_pedido"])
            pedido["valor"] = "0"
        total += float(pedido["valor"])
        contados += 1
    print(f"Ticket médio de {MES}: R$ {total / contados:.2f} em {contados} pedidos")
    return sem_valor


def main():
    pedidos = ler_pedidos(PEDIDOS)
    faltando = ticket_medio(pedidos)
    print("Pedidos sem valor:", faltando)
    MES = "2026-06"
    faltando = ticket_medio(pedidos)
    print("Pedidos sem valor:", faltando)


if __name__ == "__main__":
    main()
