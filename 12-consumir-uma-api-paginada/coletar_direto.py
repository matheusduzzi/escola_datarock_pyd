"""O primeiro programa de coleta, do jeito que a IA escreveu. Roda sem erro.

    python3 coletar_direto.py

A aula mostra o que falta nele. Não use como modelo: o programa da aula é o coletar.py.
"""
import json
import os
import urllib.request

URL = "http://127.0.0.1:8765/v1/resultados"
TOKEN = os.environ.get("API_TRIATLO_TOKEN", "")


def pegar(pagina):
    pedido = urllib.request.Request(f"{URL}?edicao=2025&pagina={pagina}&por_pagina=100",
                                    headers={"Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(pedido) as resposta:
        return json.load(resposta)


primeira = pegar(1)
resultados = primeira["itens"]
for pagina in range(2, primeira["total_paginas"]):
    resultados += pegar(pagina)["itens"]

with open("resultados-2025.json", "w", encoding="utf-8") as arquivo:
    json.dump(resultados, arquivo, ensure_ascii=False)
print(f"Salvei {len(resultados)} resultados em resultados-2025.json")
