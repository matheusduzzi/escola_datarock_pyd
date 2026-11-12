"""A impressão digital do que a base diz, sem as datas de quando cada linha entrou ou mudou.

    python3 impressao.py base-triatlo.sqlite
    python3 impressao.py base-triatlo.sqlite --edicao 2025

Duas bases com os mesmos resultados têm a mesma impressão, mesmo que os arquivos sejam
diferentes byte a byte (as datas, as rodadas e a organização interna do SQLite mudam).
"""
import argparse
import hashlib
import sqlite3


def impressao(caminho, edicao=None):
    """Retorna (quantos resultados, sha256 das linhas edicao|id_inscricao|conteudo em ordem)."""
    con = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True)
    filtro, parametros = ("WHERE edicao = ?", (edicao,)) if edicao is not None else ("", ())
    linhas = con.execute(f"SELECT edicao, id_inscricao, conteudo FROM resultados {filtro} "
                         "ORDER BY edicao, id_inscricao", parametros).fetchall()
    con.close()
    soma = hashlib.sha256()
    for e, i, c in linhas:
        soma.update(f"{e}|{i}|{c}\n".encode("utf-8"))
    return len(linhas), soma.hexdigest()


def main():
    ap = argparse.ArgumentParser(description="Impressão digital dos resultados de uma base")
    ap.add_argument("base")
    ap.add_argument("--edicao", type=int)
    a = ap.parse_args()
    n, sha = impressao(a.base, a.edicao)
    print(f"{a.base}: {n} resultados; impressão {sha[:16]}")


if __name__ == "__main__":
    main()
