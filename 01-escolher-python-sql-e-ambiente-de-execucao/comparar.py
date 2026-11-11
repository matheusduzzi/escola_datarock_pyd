"""A mesma conta duas vezes: em SQL, dentro do banco, e em pandas, no Python.

Monta um banco SQLite na memória com os pedidos e os produtos da Loja Exemplo
(../dados/loja), faz o faturamento entregue por mês dos dois jeitos e mostra
quantas linhas saíram do banco, quanta memória a tabela ocupa no pandas e se
os dois resultados batem.

    python3 comparar.py
"""
import sqlite3
from pathlib import Path

import pandas as pd

LOJA = Path(__file__).resolve().parent.parent / "dados" / "loja"

CONSULTA = """
SELECT substr(data_pedido, 1, 7) AS mes,
       round(sum(valor), 2)      AS faturamento
FROM pedidos
WHERE status = 'entregue'
GROUP BY mes
ORDER BY mes
"""


def montar_banco():
    """Cria o banco na memória com as tabelas pedidos e produtos."""
    banco = sqlite3.connect(":memory:")
    for tabela in ("pedidos", "produtos"):
        pd.read_csv(LOJA / f"{tabela}.csv").to_sql(tabela, banco, index=False)
    return banco


def em_sql(banco):
    """A conta roda no banco. Só o resultado sai de lá."""
    linhas = banco.execute(CONSULTA).fetchall()
    return pd.DataFrame(linhas, columns=["mes", "faturamento"]), len(linhas)


def em_pandas(banco):
    """O banco manda a tabela inteira. A conta roda no Python."""
    pedidos = pd.read_sql("SELECT * FROM pedidos", banco)
    entregues = pedidos[pedidos["status"] == "entregue"]
    resultado = (entregues.groupby(entregues["data_pedido"].str[:7])["valor"]
                 .sum().round(2).rename_axis("mes").reset_index(name="faturamento"))
    return resultado, pedidos


def main():
    banco = montar_banco()

    print("== 1. SQL, dentro do banco")
    sql, linhas_sql = em_sql(banco)
    print(sql.to_string(index=False))
    print("linhas que saíram do banco:", linhas_sql)

    print("\n== 2. pandas, no Python")
    pdas, pedidos = em_pandas(banco)
    print(pdas.to_string(index=False))
    print("linhas que saíram do banco:", len(pedidos))

    print("\n== 3. Os dois batem?")
    print("mesmo resultado:", sql.equals(pdas))

    print("\n== 4. Memória da tabela de pedidos no pandas")
    arquivo = (LOJA / "pedidos.csv").stat().st_size
    memoria = int(pedidos.memory_usage(deep=True).sum())
    print("pedidos.csv no disco:", arquivo, "bytes")
    print("a mesma tabela no pandas:", memoria, "bytes")
    print("por coluna:")
    print(pedidos.memory_usage(deep=True).drop("Index").to_string())
    menor = pedidos.astype({"status": "category"}).assign(data_pedido=pd.to_datetime(pedidos["data_pedido"]))
    print("com status como category e data como data:", int(menor.memory_usage(deep=True).sum()), "bytes")

    print("\n== 5. Python manda a consulta, o banco faz a conta")
    junto = pd.read_sql(CONSULTA, banco)
    print("linhas que saíram do banco:", len(junto))
    print("mesmo resultado:", junto.equals(sql))


if __name__ == "__main__":
    main()
