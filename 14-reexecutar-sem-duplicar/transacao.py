"""O que a transação faz quando um comando dá erro no meio. Só biblioteca padrão; não usa a API.

    python3 transacao.py
"""
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE resultados (edicao INTEGER, id_inscricao TEXT, PRIMARY KEY (edicao, id_inscricao))")

try:
    with con:
        con.execute("INSERT INTO resultados VALUES (2025, '2025-0007')")
        con.execute("INSERT INTO resultados VALUES (2025, '2025-0008')")
        con.execute("INSERT INTO resultados VALUES (2025, '2025-0007')")
except sqlite3.IntegrityError as erro:
    print(f"erro: {erro}")

print("linhas na tabela:", con.execute("SELECT count(*) FROM resultados").fetchone()[0])
