"""Clientes que compraram num mês e voltaram no outro, como o Caio deixou."""
import csv
from pathlib import Path

PEDIDOS = Path(__file__).resolve().parent.parent / "dados" / "loja" / "pedidos.csv"
VISTOS = set()


def ler_pedidos(caminho):
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def clientes_que_voltaram(pedidos, mes_antes, mes_depois):
    for pedido in pedidos:
        if pedido["data_pedido"][:7] == mes_antes:
            VISTOS.add(pedido["id_cliente"])
    voltaram = []
    for pedido in pedidos:
        if pedido["data_pedido"][:7] == mes_depois and pedido["id_cliente"] in VISTOS:
            voltaram.append(pedido["id_cliente"])
    return sorted(voltaram)


def main():
    pedidos = ler_pedidos(PEDIDOS)
    abril_maio = clientes_que_voltaram(pedidos, "2026-04", "2026-05")
    print("Compraram em abril e voltaram em maio:", len(abril_maio))
    maio_junho = clientes_que_voltaram(pedidos, "2026-05", "2026-06")
    print("Compraram em maio e voltaram em junho:", len(maio_junho))
    print("Os 8 primeiros da lista de junho:", maio_junho[:8])


if __name__ == "__main__":
    main()
