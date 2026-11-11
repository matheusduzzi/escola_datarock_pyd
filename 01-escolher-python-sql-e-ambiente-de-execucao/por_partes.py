"""Lê os pedidos em pedaços e mostra qual conta dá para fazer por partes.

    python3 por_partes.py
    python3 por_partes.py --linhas 1000

Cada pedaço é um DataFrame pequeno. O programa soma o faturamento pedaço por
pedaço, conta clientes diferentes do jeito errado e do jeito certo, e compara
a mediana dos pedaços com a mediana de verdade.
"""
import argparse
from pathlib import Path

import pandas as pd

PEDIDOS = Path(__file__).resolve().parent.parent / "dados" / "loja" / "pedidos.csv"
COLUNAS = ["id_cliente", "data_pedido", "valor", "status"]


def pedacos(linhas):
    """Entrega os pedidos entregues, um pedaço por vez, só com as colunas da conta."""
    for pedaco in pd.read_csv(PEDIDOS, usecols=COLUNAS, chunksize=linhas):
        pedaco = pedaco[pedaco["status"] == "entregue"]
        yield pedaco.assign(mes=pedaco["data_pedido"].str[:7])


def main():
    args = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    args.add_argument("--linhas", type=int, default=500, help="linhas por pedaço (padrão 500)")
    linhas = args.parse_args().linhas
    if linhas < 1:
        raise SystemExit("--linhas precisa ser 1 ou mais")

    inteiro = pd.read_csv(PEDIDOS, usecols=COLUNAS)
    inteiro = inteiro[inteiro["status"] == "entregue"].assign(mes=lambda d: d["data_pedido"].str[:7])

    soma = pd.Series(dtype="float64")
    clientes_somados = pd.Series(dtype="int64")
    clientes_por_mes = {}
    medianas = []
    maior_pedaco = 0
    n = 0
    for pedaco in pedacos(linhas):
        n += 1
        maior_pedaco = max(maior_pedaco, int(pedaco.memory_usage(deep=True).sum()))
        soma = soma.add(pedaco.groupby("mes")["valor"].sum(), fill_value=0)
        clientes_somados = clientes_somados.add(pedaco.groupby("mes")["id_cliente"].nunique(), fill_value=0)
        for mes, ids in pedaco.groupby("mes")["id_cliente"]:
            clientes_por_mes.setdefault(mes, set()).update(ids)
        medianas.append(pedaco["valor"].median())

    print(f"Li {n} {'pedaço' if n == 1 else 'pedaços'} de até {linhas} linhas.")
    print("memória do maior pedaço:", maior_pedaco, "bytes")
    print("memória da tabela inteira, mesmas colunas:", int(inteiro.memory_usage(deep=True).sum()), "bytes")

    print("\n== 1. Faturamento por mês: soma dos pedaços x tabela inteira")
    certo = inteiro.groupby("mes")["valor"].sum()
    tabela = pd.DataFrame({"por partes": soma.round(2), "inteiro": certo.round(2)})
    print(tabela.to_string())
    print("bate:", bool((tabela["por partes"] == tabela["inteiro"]).all()))

    print("\n== 2. Clientes diferentes por mês")
    real = inteiro.groupby("mes")["id_cliente"].nunique()
    conjunto = pd.Series({mes: len(ids) for mes, ids in sorted(clientes_por_mes.items())})
    tabela = pd.DataFrame({"soma dos pedaços": clientes_somados.astype(int),
                           "conjunto de ids": conjunto, "inteiro": real})
    print(tabela.to_string())
    print("soma dos pedaços bate:", bool((tabela["soma dos pedaços"] == tabela["inteiro"]).all()))
    print("conjunto de ids bate:", bool((tabela["conjunto de ids"] == tabela["inteiro"]).all()))

    print("\n== 3. Mediana do valor dos pedidos")
    print("mediana das medianas dos pedaços:", round(pd.Series(medianas).median(), 2))
    print("mediana da tabela inteira:", round(inteiro["valor"].median(), 2))


if __name__ == "__main__":
    main()
