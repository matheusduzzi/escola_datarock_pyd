"""A coleta com tentativas, do jeito que a IA escreveu: tenta de novo até dar certo.

    python3 coletar_insistente.py

Com a API em --falhas, ela passa e grava 2025 inteiro. Com o token errado ou a API parada,
ela nunca termina: aperte Ctrl+C para parar. A seção 1 da aula mostra por quê.
"""
import json
import os
import time
import urllib.request

ENDERECO = os.environ.get("API_TRIATLO_URL", "http://127.0.0.1:8765")


def pedir(token, pagina):
    while True:
        try:
            url = f"{ENDERECO}/v1/resultados?edicao=2025&pagina={pagina}&por_pagina=100"
            pedido = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
            with urllib.request.urlopen(pedido) as resposta:
                return json.load(resposta)
        except Exception:
            print(f"página {pagina}: deu erro, tentando de novo", flush=True)
            time.sleep(1)


def main():
    token = os.environ.get("API_TRIATLO_TOKEN", "")
    primeira = pedir(token, 1)
    linhas = list(primeira["itens"])
    for pagina in range(2, primeira["total_paginas"] + 1):
        linhas += pedir(token, pagina)["itens"]
    with open("resultados-2025.json", "w", encoding="utf-8") as arquivo:
        json.dump(linhas, arquivo, ensure_ascii=False)
    print(f"Salvei {len(linhas)} resultados em resultados-2025.json")


if __name__ == "__main__":
    main()
