"""A coleta da aula 12, agora com tempo limite, tentativas limitadas e cada falha anotada.

    python3 coletar.py --edicao 2025
    python3 coletar.py --edicao 2025 --espera 2 --saida resultados-2025-espera.json

O token vem da variável de ambiente API_TRIATLO_TOKEN, como nas aulas 11 e 12.
O endereço padrão é o da API do kit, http://127.0.0.1:8765 (ou --endereco, ou API_TRIATLO_URL).

Cada chamada tem um tempo limite (--espera). Quando a falha costuma passar sozinha (429, 502,
503, 504, tempo esgotado ou API sem conexão), o programa espera e tenta de novo, no máximo
TENTATIVAS vezes por página. Quando a API manda Retry-After, ele espera o que ela pediu, até
TETO_ESPERA segundos. Os outros erros param a coleta na hora, sem nova tentativa.
Toda falha, inclusive a que passou, vai para a tela e para o resumo do arquivo gravado.
O arquivo só é gravado quando a coleta bateu com o envelope da API, como na aula 12.

Código de saída:
  0  coleta completa, arquivo gravado
  1  a coleta não bateu ou a API respondeu um erro que não passa tentando de novo; nada foi gravado
  2  falta a variável API_TRIATLO_TOKEN; nenhuma chamada foi feita
  3  a falha podia passar e não passou: desisti depois das tentativas ou da espera pedida; nada foi gravado
"""
import argparse
import http.client
import json
import os
import socket
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ENDERECO_PADRAO = "http://127.0.0.1:8765"
ROTA = "/v1/resultados"

# A política de falhas, num lugar só.
TENTATIVAS = 3                      # chamadas por página, contando a primeira
ESPERAS = (1, 2)                    # segundos antes da 2ª e da 3ª chamada, quando a API não diz
TETO_ESPERA = 30                    # nunca espero mais que isso antes de uma tentativa
PASSAM_SOZINHOS = {429, 502, 503, 504}


class ColetaIncompleta(Exception):
    """A coleta não bateu com o envelope, ou a API respondeu um erro que não passa tentando de novo."""


class Desisti(Exception):
    """A falha podia passar sozinha, mas não passou dentro das tentativas ou da espera máxima."""


class SemResposta(Exception):
    """A chamada não teve resposta: passou do tempo limite ou não conectou."""


def chamar(endereco, token, rota, parametros, espera):
    """Uma chamada GET com tempo limite. Retorna o código, o corpo, o caminho e os cabeçalhos."""
    caminho = rota + "?" + urllib.parse.urlencode(parametros)
    pedido = urllib.request.Request(endereco.rstrip("/") + caminho,
                                    headers={"Authorization": f"Bearer {token}"})
    try:
        try:
            resposta = urllib.request.urlopen(pedido, timeout=espera)
        except urllib.error.HTTPError as erro:
            resposta = erro  # 4xx e 5xx: o código, o corpo e os cabeçalhos vêm na exceção
        with resposta:
            texto = resposta.read().decode("utf-8", "replace")
            codigo, cabecalhos = resposta.getcode(), resposta.headers
    except (urllib.error.URLError, OSError, http.client.HTTPException) as erro:
        motivo = getattr(erro, "reason", erro)
        if isinstance(motivo, (socket.timeout, TimeoutError)):
            raise SemResposta(f"passou de {espera:g} s sem resposta")
        raise SemResposta(f"não conectou em {endereco}: {motivo}")
    try:
        corpo = json.loads(texto)
    except ValueError:
        corpo = {"resposta_que_nao_e_json": texto[:200]}
    return codigo, corpo, caminho, cabecalhos


def segundos_pedidos(valor, agora=None):
    """Lê o Retry-After: um número de segundos ou uma data HTTP. Retorna None se não veio ou não deu para ler."""
    if not valor:
        return None
    valor = valor.strip()
    if valor.isdigit():
        return int(valor)
    try:
        quando = parsedate_to_datetime(valor)
    except (TypeError, ValueError):
        return None
    if quando.tzinfo is None:
        return None
    agora = agora or datetime.now(timezone.utc)
    return max(0, int((quando - agora).total_seconds() + 0.999))


def pedir_pagina(endereco, token, filtros, pagina, por_pagina, espera, falhas, dormir=time.sleep, mostrar=print):
    """Pede uma página com até TENTATIVAS chamadas. Cada falha entra na lista falhas, inclusive a que passou."""
    parametros = dict(filtros, pagina=pagina, por_pagina=por_pagina)
    for tentativa in range(1, TENTATIVAS + 1):
        pedido = None
        try:
            codigo, corpo, caminho, cabecalhos = chamar(endereco, token, ROTA, parametros, espera)
        except SemResposta as erro:
            o_que = str(erro)
        else:
            if codigo == 200 and "resposta_que_nao_e_json" not in corpo:
                return corpo, caminho
            if codigo not in PASSAM_SOZINHOS:
                raise ColetaIncompleta(f"a página {pagina} respondeu {codigo}: {json.dumps(corpo, ensure_ascii=False)}. "
                                       "Esse erro não passa tentando de novo; não repeti a chamada")
            o_que = f"respondeu {codigo}"
            pedido = segundos_pedidos(cabecalhos.get("Retry-After"))
            if pedido is not None:
                o_que += f", a API pediu {pedido} s"
        falha = {"pagina": pagina, "tentativa": tentativa, "o_que": o_que}
        if tentativa == TENTATIVAS:
            falhas.append(dict(falha, depois="desisti"))
            raise Desisti(f"a página {pagina} falhou nas {TENTATIVAS} tentativas; a última: {o_que}")
        segundos = pedido if pedido is not None else ESPERAS[tentativa - 1]
        if segundos > TETO_ESPERA:
            falhas.append(dict(falha, depois="desisti"))
            raise Desisti(f"a página {pagina} {o_que}, mais que o teto de {TETO_ESPERA} s; não esperei")
        falha["depois"] = f"esperei {segundos} s"
        falhas.append(falha)
        try:
            dormir(segundos)
        except Desisti:
            falha["depois"] = "desisti"
            raise
        mostrar(f"página {pagina}: {o_que}; esperei {segundos} s e tento de novo ({tentativa + 1}ª de {TENTATIVAS})")


def coletar(endereco, token, filtros, por_pagina=100, espera=10, mostrar=print, falhas=None, dormir=time.sleep):
    """Pede da página 1 até a total_paginas da primeira resposta e confere cada página.

    Retorna (linhas, resumo). Cada linha é o item como a API mandou, mais a chave "origem"
    com a página e a posição dentro dela. O resumo tem a chamada de cada página e as falhas.
    Se você passar uma lista em falhas, ela recebe cada falha, mesmo quando a coleta para no meio.
    A função dormir(segundos) faz cada espera; o padrão é time.sleep. Se ela levantar Desisti,
    a coleta para ali e a falha fica anotada como "desisti".
    """
    falhas = [] if falhas is None else falhas
    pedir = lambda n: pedir_pagina(endereco, token, filtros, n, por_pagina, espera, falhas, dormir, mostrar)
    primeira, caminho = pedir(1)
    total, total_paginas = primeira["total"], primeira["total_paginas"]
    linhas, paginas = [], []
    for pagina in range(1, total_paginas + 1):
        if pagina == 1:
            corpo = primeira
        else:
            corpo, caminho = pedir(pagina)
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
        "paginas": paginas,
        "falhas": falhas,
        "politica": {"espera": espera, "tentativas": TENTATIVAS, "esperas": list(ESPERAS),
                     "teto_espera": TETO_ESPERA, "passam_sozinhos": sorted(PASSAM_SOZINHOS)},
        "coletado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    return linhas, resumo


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


def mostrar_falhas(falhas, mostrar=print):
    if not falhas:
        mostrar("nenhuma falha no caminho")
        return
    mostrar(f"falhas no caminho: {len(falhas)}")
    for f in falhas:
        mostrar(f"  página {f['pagina']}, tentativa {f['tentativa']}: {f['o_que']}; {f['depois']}")


def main():
    ap = argparse.ArgumentParser(description="Coleta completa de uma edição, com tempo limite e tentativas limitadas")
    ap.add_argument("--edicao", required=True)
    ap.add_argument("--por-pagina", type=int, default=100)
    ap.add_argument("--saida", help="arquivo de saída (padrão resultados-<edicao>.json)")
    ap.add_argument("--endereco", default=os.environ.get("API_TRIATLO_URL", ENDERECO_PADRAO))
    ap.add_argument("--espera", type=float, default=10, help="tempo limite de cada chamada, em segundos (padrão 10)")
    a = ap.parse_args()

    token = os.environ.get("API_TRIATLO_TOKEN")
    if not token:
        print("ERROR falta a variável de ambiente API_TRIATLO_TOKEN. "
              "Defina no terminal antes de coletar (veja o README). Nenhuma chamada foi feita.", file=sys.stderr)
        return 2
    saida = a.saida or f"resultados-{a.edicao}.json"
    falhas = []
    try:
        linhas, resumo = coletar(a.endereco, token, {"edicao": a.edicao}, a.por_pagina, a.espera, falhas=falhas)
    except ColetaIncompleta as erro:
        if falhas:
            mostrar_falhas(falhas)
        print(f"ERROR coleta incompleta: {erro}. Nada foi gravado em {saida}.", file=sys.stderr)
        return 1
    except Desisti as erro:
        mostrar_falhas(falhas)
        print(f"ERROR desisti: {erro}. Nada foi gravado em {saida}.", file=sys.stderr)
        return 3
    print(f"total da API: {resumo['total_api']}; linhas recebidas: {resumo['linhas']}. Bateu.")
    mostrar_falhas(falhas)
    gravar(saida, {"coleta": resumo, "linhas": linhas})
    print(f"gravei {saida}: {resumo['linhas']} linhas, {resumo['inscricoes']} inscrições, "
          f"{len(falhas)} falhas anotadas no resumo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
