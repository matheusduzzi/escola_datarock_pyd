"""Pedidos entregues e ticket médio por cidade, no mês do arquivo."""
import argparse
import csv
from pathlib import Path

CLIENTES = Path(__file__).resolve().parent.parent / "dados" / "loja" / "clientes.csv"


def ler_cidades(caminho):
    """Dicionário id_cliente -> cidade, lido do cadastro de clientes."""
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return {linha["id_cliente"]: linha["cidade"] for linha in csv.DictReader(arquivo)}


def valores_por_cidade(caminho_pedidos, cidades):
    """Para cada cidade, a lista de valores dos pedidos entregues (None quando o caixa não anotou)."""
    por_cidade = {}
    with open(caminho_pedidos, encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            if linha["status"] != "entregue":
                continue
            cidade = cidades[linha["id_cliente"]]
            valor = float(linha["valor"]) if linha["valor"] else None
            por_cidade.setdefault(cidade, []).append(valor)
    return por_cidade


def resumo(por_cidade):
    """Uma linha por cidade: pedidos, pedidos com valor, ticket médio."""
    linhas = []
    for cidade in sorted(por_cidade):
        valores = por_cidade[cidade]
        com_valor = [v for v in valores if v is not None]
        ticket = sum(com_valor) / len(com_valor)
        linhas.append((cidade, len(valores), len(com_valor), round(ticket, 2)))
    return linhas


def main():
    parser = argparse.ArgumentParser(description="Pedidos entregues e ticket médio por cidade.")
    parser.add_argument("--arquivo", default="pedidos-julho-v2.csv", help="CSV de pedidos do mês")
    parser.add_argument("--clientes", default=str(CLIENTES), help="CSV do cadastro de clientes")
    args = parser.parse_args()

    linhas = resumo(valores_por_cidade(args.arquivo, ler_cidades(args.clientes)))
    print(f"{'cidade':<16} {'pedidos':>7} {'com valor':>9} {'ticket':>8}")
    for cidade, pedidos, com_valor, ticket in linhas:
        print(f"{cidade:<16} {pedidos:>7} {com_valor:>9} {ticket:>8.2f}")
    print(f"Pedidos entregues no resumo: {sum(l[1] for l in linhas)}")


if __name__ == "__main__":
    main()
