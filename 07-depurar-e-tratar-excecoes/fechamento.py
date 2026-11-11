"""Fechamento do mês: faturamento dos pedidos entregues, por categoria.

Versão do Caio, como estava na pasta do financeiro.
"""
import argparse
import csv
from pathlib import Path

PRODUTOS = Path(__file__).resolve().parent.parent / "dados" / "loja" / "produtos.csv"


def ler_categorias(caminho):
    """Dicionário id_produto -> categoria, lido do cadastro de produtos."""
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return {linha["id_produto"]: linha["categoria"] for linha in csv.DictReader(arquivo)}


def ler_valor(texto):
    """Valor do pedido em reais. Vazio quer dizer que o caixa não anotou."""
    if texto == "":
        return None
    return float(texto)


def somar_por_categoria(caminho_pedidos, categorias):
    totais = {}
    with open(caminho_pedidos, encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            if linha["status"] != "entregue":
                continue
            try:
                valor = ler_valor(linha["valor"])
                categoria = categorias[linha["id_produto"]]
                totais[categoria] = totais.get(categoria, 0) + valor
            except Exception:
                continue  # uma linha dava erro, pulei
    return totais


def main():
    parser = argparse.ArgumentParser(description="Faturamento entregue por categoria.")
    parser.add_argument("--arquivo", default="pedidos-julho.csv", help="CSV de pedidos do mês")
    args = parser.parse_args()

    totais = somar_por_categoria(args.arquivo, ler_categorias(PRODUTOS))
    print(f"Faturamento entregue de {args.arquivo}, em R$")
    for categoria in sorted(totais):
        print(f"{categoria:<10} {totais[categoria]:>10.2f}")
    print(f"Total: {sum(totais.values()):.2f}")


if __name__ == "__main__":
    main()
