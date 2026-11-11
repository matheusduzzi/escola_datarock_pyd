"""Puxa todas as páginas de uma edição da API de resultados, com a origem de cada linha.

    python3 coletar.py --edicao 2025
    python3 coletar.py --edicao 2025 --por-pagina 50 --saida resultados-2025-50.json

O token vem da variável de ambiente API_TRIATLO_TOKEN, como no chamar.py da aula 11.
O endereço padrão é o da API do kit, http://127.0.0.1:8765 (ou --endereco, ou API_TRIATLO_URL).

O programa só grava o arquivo depois de ver que a coleta bateu com o envelope da API:
cada página veio com o número e o tamanho pedidos, o total não mudou no meio e a soma
das linhas é igual ao total. Se não bateu, ele para, diz o que aconteceu e não grava nada.

Código de saída:
  0  coleta completa, arquivo gravado
  1  a coleta não bateu ou a API respondeu com erro; nada foi gravado
  2  falta a variável API_TRIATLO_TOKEN; nenhuma chamada foi feita
  3  a API não respondeu (fora do ar ou passou do tempo de espera); nada foi gravado
"""
import argparse
import json
import os
import socket
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ENDERECO_PADRAO = "http://127.0.0.1:8765"
ROTA = "/v1/resultados"


class ColetaIncompleta(Exception):
    """A coleta parou antes do fim ou não bateu com o envelope. A mensagem diz onde."""


class ApiForaDoAr(Exception):
    """A API não respondeu: não está rodando ou passou do tempo de espera."""


def chamar(endereco, token, rota, parametros, espera):
    """Uma chamada GET. Retorna o código e o corpo já lido como JSON."""
    caminho = rota + "?" + urllib.parse.urlencode(parametros)
    pedido = urllib.request.Request(endereco.rstrip("/") + caminho,
                                    headers={"Authorization": f"Bearer {token}"})
    try:
        resposta = urllib.request.urlopen(pedido, timeout=espera)
    except urllib.error.HTTPError as erro:
        resposta = erro  # 4xx e 5xx: o código e o corpo vêm na exceção
    except (urllib.error.URLError, socket.timeout, TimeoutError) as erro:
        raise ApiForaDoAr(f"a API não respondeu em {endereco}: {getattr(erro, 'reason', erro)}")
    with resposta:
        corpo = json.loads(resposta.read().decode("utf-8"))
        return resposta.getcode(), corpo, caminho


def pedir_pagina(endereco, token, filtros, pagina, por_pagina, espera):
    parametros = dict(filtros, pagina=pagina, por_pagina=por_pagina)
    codigo, corpo, caminho = chamar(endereco, token, ROTA, parametros, espera)
    if codigo != 200:
        raise ColetaIncompleta(f"a página {pagina} respondeu {codigo}: {json.dumps(corpo, ensure_ascii=False)}")
    return corpo, caminho


def coletar(endereco, token, filtros, por_pagina=100, espera=10, mostrar=print):
    """Pede da página 1 até a total_paginas da primeira resposta e confere cada página.

    Retorna (linhas, resumo). Cada linha é o item como a API mandou, mais a chave "origem"
    com a página e a posição dentro dela. O resumo tem a chamada de cada página.
    """
    primeira, caminho = pedir_pagina(endereco, token, filtros, 1, por_pagina, espera)
    total, total_paginas = primeira["total"], primeira["total_paginas"]
    linhas, paginas = [], []
    for pagina in range(1, total_paginas + 1):
        if pagina == 1:
            corpo = primeira
        else:
            corpo, caminho = pedir_pagina(endereco, token, filtros, pagina, por_pagina, espera)
        # O que esta página deveria ter: cheia, menos a última, que leva o resto.
        esperado = por_pagina if pagina < total_paginas else total - por_pagina * (total_paginas - 1)
        itens = corpo["itens"]
        if corpo["pagina"] != pagina or corpo["por_pagina"] != por_pagina:
            raise ColetaIncompleta(f"pedi a página {pagina} com {por_pagina} por página e veio a página "
                                   f"{corpo['pagina']} com {corpo['por_pagina']}")
        if corpo["total"] != total:
            raise ColetaIncompleta(f"o total mudou no meio da coleta: {total} na página 1, "
                                   f"{corpo['total']} na página {pagina}")
        if len(itens) != esperado:
            raise ColetaIncompleta(f"a página {pagina} trouxe {len(itens)} itens; pela conta do envelope, "
                                   f"deviam ser {esperado}")
        for posicao, item in enumerate(itens, start=1):
            linhas.append(dict(item, origem={"pagina": pagina, "posicao": posicao}))
        paginas.append({"pagina": pagina, "chamada": caminho, "itens": len(itens)})
        mostrar(f"página {pagina} de {total_paginas}: {len(itens)} itens")
    if len(linhas) != total:
        raise ColetaIncompleta(f"a soma das páginas deu {len(linhas)} linhas e o total da API é {total}")
    resumo = {
        "rota": ROTA,
        "filtros": filtros,
        "por_pagina": por_pagina,
        "total_api": total,
        "total_paginas": total_paginas,
        "linhas": len(linhas),
        "inscricoes": len({l["id_inscricao"] for l in linhas}),
        "repetidos": repetidos(linhas),
        "paginas": paginas,
        "coletado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    return linhas, resumo


def repetidos(linhas):
    """Inscrições que vieram mais de uma vez, com a origem de cada vez."""
    vezes = {}
    for linha in linhas:
        vezes.setdefault(linha["id_inscricao"], []).append(linha["origem"])
    return {chave: origens for chave, origens in vezes.items() if len(origens) > 1}


def gravar(caminho, dados):
    """Grava num arquivo temporário da mesma pasta e só então troca pelo nome final."""
    caminho = Path(caminho)
    fd, temporario = tempfile.mkstemp(dir=caminho.parent or ".", prefix=caminho.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=1)
        os.replace(temporario, caminho)
    except BaseException:
        os.unlink(temporario)
        raise


def mostrar_repetidos(resumo, mostrar=print):
    rep = resumo["repetidos"]
    if not rep:
        mostrar("nenhuma inscrição veio duas vezes")
        return
    mostrar(f"{len(rep)} inscrições vieram mais de uma vez:")
    for chave, origens in rep.items():
        onde = "; ".join(f"página {o['pagina']} posição {o['posicao']}" for o in origens)
        mostrar(f"  {chave}: {onde}")


def main():
    ap = argparse.ArgumentParser(description="Coleta completa de uma edição pela API paginada")
    ap.add_argument("--edicao", required=True)
    ap.add_argument("--por-pagina", type=int, default=100)
    ap.add_argument("--saida", help="arquivo de saída (padrão resultados-<edicao>.json)")
    ap.add_argument("--endereco", default=os.environ.get("API_TRIATLO_URL", ENDERECO_PADRAO))
    ap.add_argument("--espera", type=float, default=10, help="segundos de espera por resposta (padrão 10)")
    a = ap.parse_args()

    token = os.environ.get("API_TRIATLO_TOKEN")
    if not token:
        print("ERROR falta a variável de ambiente API_TRIATLO_TOKEN. "
              "Defina no terminal antes de coletar (veja o README). Nenhuma chamada foi feita.", file=sys.stderr)
        return 2
    saida = a.saida or f"resultados-{a.edicao}.json"
    try:
        linhas, resumo = coletar(a.endereco, token, {"edicao": a.edicao}, a.por_pagina, a.espera)
    except ColetaIncompleta as erro:
        print(f"ERROR coleta incompleta: {erro}. Nada foi gravado em {saida}.", file=sys.stderr)
        return 1
    except ApiForaDoAr as erro:
        print(f"ERROR {erro}. Nada foi gravado em {saida}.", file=sys.stderr)
        return 3
    print(f"total da API: {resumo['total_api']}; linhas recebidas: {resumo['linhas']}. Bateu.")
    mostrar_repetidos(resumo)
    gravar(saida, {"coleta": resumo, "linhas": linhas})
    print(f"gravei {saida}: {resumo['linhas']} linhas, {resumo['inscricoes']} inscrições")
    return 0


if __name__ == "__main__":
    sys.exit(main())
