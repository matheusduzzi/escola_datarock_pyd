"""A coleta de todo dia do jeito que a IA escreveu: acrescenta cada página ao arquivo assim que ela chega.

    python3 acumular_ia.py --edicao 2025

Usa a política de falhas do coletar.py da aula 13. Cada rodada acrescenta as linhas no fim de
acumulado-<edicao>.jsonl, uma linha por resultado, "para não perder o que já veio".
A seção 1 da aula mostra o que acontece com o arquivo depois de três rodadas.
"""
import argparse
import json
import os
import sys

from coletar import ENDERECO_PADRAO, pedir_pagina


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edicao", required=True)
    a = ap.parse_args()
    token = os.environ.get("API_TRIATLO_TOKEN", "")
    endereco = os.environ.get("API_TRIATLO_URL", ENDERECO_PADRAO)
    arquivo = f"acumulado-{a.edicao}.jsonl"
    falhas = []
    try:
        primeira, _ = pedir_pagina(endereco, token, {"edicao": a.edicao}, 1, 100, 10, falhas)
        with open(arquivo, "a", encoding="utf-8") as saida:
            for pagina in range(1, primeira["total_paginas"] + 1):
                corpo = primeira if pagina == 1 else pedir_pagina(endereco, token, {"edicao": a.edicao},
                                                                  pagina, 100, 10, falhas)[0]
                for item in corpo["itens"]:
                    saida.write(json.dumps(item, ensure_ascii=False) + "\n")
                saida.flush()
                print(f"página {pagina}: acrescentei {len(corpo['itens'])} linhas")
    except Exception as erro:
        print(f"parou: {erro}")
        return 1
    finally:
        if os.path.exists(arquivo):
            with open(arquivo, encoding="utf-8") as lido:
                print(f"{arquivo} tem {sum(1 for _ in lido)} linhas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
