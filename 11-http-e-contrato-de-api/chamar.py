"""Faz uma chamada GET à API de resultados e mostra a requisição e a resposta.

    python3 chamar.py "/v1/resultados?edicao=2025&pagina=1&por_pagina=100"

O token vem da variável de ambiente API_TRIATLO_TOKEN. Ele não fica escrito no programa
e não aparece na tela: o programa mostra só "Bearer ***".

O endereço padrão é o da API do kit, http://127.0.0.1:8765. Para outro endereço,
use --endereco ou a variável API_TRIATLO_URL.

Código de saída:
  0  a API respondeu com um código 2xx
  1  a API respondeu com outro código (4xx, 5xx)
  2  falta a variável API_TRIATLO_TOKEN; nenhuma chamada foi feita
  3  a API não respondeu (fora do ar ou passou do tempo de espera)
"""
import argparse
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.request

ENDERECO_PADRAO = "http://127.0.0.1:8765"
# Date e Server mudam a cada chamada e não dizem nada sobre o contrato.
ESCONDIDOS = {"Date", "Server"}


def mostrar_corpo(corpo):
    try:
        dados = json.loads(corpo)
    except ValueError:
        print("<< corpo (não é JSON):", corpo[:300])
        return
    if isinstance(dados, dict) and isinstance(dados.get("itens"), list):
        itens = dados["itens"]
        envelope = {k: v for k, v in dados.items() if k != "itens"}
        print("<< corpo:", json.dumps(envelope, ensure_ascii=False), f"+ itens: {len(itens)}")
        if itens:
            print("<< primeiro item:", json.dumps(itens[0], ensure_ascii=False))
    else:
        print("<< corpo:", json.dumps(dados, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description="Uma chamada GET à API de resultados")
    ap.add_argument("caminho", help='rota e parâmetros, por exemplo "/v1/resultados?edicao=2025&pagina=1"')
    ap.add_argument("--endereco", default=os.environ.get("API_TRIATLO_URL", ENDERECO_PADRAO))
    ap.add_argument("--espera", type=float, default=10, help="segundos de espera pela resposta (padrão 10)")
    a = ap.parse_args()

    token = os.environ.get("API_TRIATLO_TOKEN")
    if not token:
        print("ERROR falta a variável de ambiente API_TRIATLO_TOKEN. "
              "Defina no terminal antes de chamar (veja o README). Nenhuma chamada foi feita.", file=sys.stderr)
        return 2

    url = a.endereco.rstrip("/") + a.caminho
    pedido = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    print(f">> GET {url}")
    print(">> Authorization: Bearer ***")

    inicio = time.monotonic()
    try:
        resposta = urllib.request.urlopen(pedido, timeout=a.espera)
    except urllib.error.HTTPError as erro:
        # 4xx e 5xx chegam como exceção, mas a exceção traz o código, os cabeçalhos e o corpo.
        resposta = erro
    except (urllib.error.URLError, socket.timeout, TimeoutError) as erro:
        motivo = getattr(erro, "reason", erro)
        print(f"ERROR a API não respondeu em {a.endereco}: {motivo}", file=sys.stderr)
        return 3

    with resposta:
        corpo = resposta.read().decode("utf-8")
        codigo = resposta.getcode()
        print(f"<< {codigo} {resposta.reason} ({round(time.monotonic() - inicio)} s)")
        for nome, valor in resposta.headers.items():
            if nome not in ESCONDIDOS:
                print(f"<< {nome}: {valor}")
    mostrar_corpo(corpo)
    return 0 if 200 <= codigo < 300 else 1


if __name__ == "__main__":
    sys.exit(main())
