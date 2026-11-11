"""Campanha de julho: pedidos entregues e clientes diferentes por cidade, em maio e em junho."""
import argparse
import csv
from pathlib import Path

LOJA = Path(__file__).resolve().parent.parent / "dados" / "loja"

MODELO = {"pedidos": 0, "clientes": []}


def ler_cidades(caminho):
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return {linha["id_cliente"]: linha["cidade"] for linha in csv.DictReader(arquivo)}


def ler_pedidos(caminho):
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def resumo_do_mes(pedidos, cidades, mes, incluir_cancelados):
    por_cidade = {}
    for pedido in pedidos:
        if not pedido["data_pedido"].startswith(mes):
            continue
        if pedido["status"] == "cancelado" and not incluir_cancelados:
            continue
        cidade = cidades[pedido["id_cliente"]]
        if cidade not in por_cidade:
            por_cidade[cidade] = MODELO.copy()
        resumo = por_cidade[cidade]
        resumo["pedidos"] += 1
        if pedido["id_cliente"] not in resumo["clientes"]:
            resumo["clientes"].append(pedido["id_cliente"])
    return por_cidade


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pedidos", default=LOJA / "pedidos.csv")
    parser.add_argument("--incluir-cancelados", type=bool, default=False)
    args = parser.parse_args()

    pedidos = ler_pedidos(args.pedidos)
    cidades = ler_cidades(LOJA / "clientes.csv")
    print(f"Pedidos de {Path(args.pedidos).name}, cancelados incluídos: {args.incluir_cancelados}")
    for mes in ("2026-05", "2026-06"):
        print()
        print(f"{mes}  {'cidade':<16}{'pedidos':>8}{'clientes':>9}")
        for cidade, resumo in sorted(resumo_do_mes(pedidos, cidades, mes, args.incluir_cancelados).items()):
            print(f"{'':9}{cidade:<16}{resumo['pedidos']:>8}{len(resumo['clientes']):>9}")


if __name__ == "__main__":
    main()
