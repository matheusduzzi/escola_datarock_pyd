"""Atualiza a base do triatlo com a coleta do dia, sem duplicar, e retoma uma rodada que parou no meio.

    python3 atualizar.py --edicao 2025
    python3 atualizar.py --edicao 2025 --base outra.sqlite --por-pagina 50
    python3 atualizar.py --edicao 2025 --do-zero

A base é um arquivo SQLite (base-triatlo.sqlite, padrão) com uma linha por resultado.
O que identifica um resultado é a edição e o id_inscricao: a mesma inscrição que volta
amanhã atualiza a linha de hoje, e não vira uma linha nova.

Cada página que chega e passa na conferência vai para o checkpoint, dentro da mesma base.
Se a rodada desiste no meio, a próxima retoma dali, desde que seja a mesma rodada (rota,
filtros e por_pagina), que o total da API não tenha mudado e que o checkpoint tenha menos de
VALIDADE_CHECKPOINT. A base só muda quando a rodada veio inteira, numa transação só.

Usa a política de falhas do coletar.py da aula 13 (tempo limite, tentativas, Retry-After).
O token vem da variável API_TRIATLO_TOKEN; o endereço, de API_TRIATLO_URL ou --endereco.

Código de saída:
  0  base atualizada
  1  a coleta não bateu, ou a API respondeu um erro que não passa tentando de novo;
     a base não mudou e o checkpoint foi descartado
  2  falta a variável API_TRIATLO_TOKEN; nenhuma chamada foi feita
  3  desisti depois das tentativas; a base não mudou e as páginas que vieram ficaram no checkpoint
"""
import argparse
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone

from coletar import ENDERECO_PADRAO, ROTA, ColetaIncompleta, Desisti, mostrar_falhas, pedir_pagina

BASE_PADRAO = "base-triatlo.sqlite"
VALIDADE_CHECKPOINT = timedelta(hours=1)

ESQUEMA = """
CREATE TABLE IF NOT EXISTS resultados (
    edicao INTEGER NOT NULL,
    id_inscricao TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    entrou_em TEXT NOT NULL,
    mudou_em TEXT,
    PRIMARY KEY (edicao, id_inscricao)
);
CREATE TABLE IF NOT EXISTS checkpoint (
    rodada TEXT NOT NULL,
    total INTEGER NOT NULL,
    total_paginas INTEGER NOT NULL,
    comecou_em TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS checkpoint_paginas (
    pagina INTEGER PRIMARY KEY,
    chamada TEXT NOT NULL,
    itens TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS rodadas (
    terminou_em TEXT NOT NULL,
    edicao INTEGER NOT NULL,
    novos INTEGER NOT NULL,
    mudaram INTEGER NOT NULL,
    iguais INTEGER NOT NULL,
    nao_vieram INTEGER NOT NULL,
    paginas_do_checkpoint INTEGER NOT NULL,
    falhas TEXT NOT NULL
);
"""


def agora_utc():
    return datetime.now(timezone.utc)


def abrir(caminho):
    con = sqlite3.connect(caminho)
    con.executescript(ESQUEMA)
    return con


def conteudo(item):
    """O resultado como texto, para comparar: o item da API sem a origem, com as chaves em ordem."""
    return json.dumps({k: v for k, v in item.items() if k != "origem"}, ensure_ascii=False, sort_keys=True)


def chave(item):
    """O que identifica um resultado: a edição e a inscrição."""
    return int(item["edicao"]), item["id_inscricao"]


def ler_checkpoint(con):
    linha = con.execute("SELECT rodada, total, total_paginas, comecou_em FROM checkpoint").fetchone()
    if linha is None:
        return None
    paginas = {p: (c, json.loads(i)) for p, c, i in con.execute("SELECT pagina, chamada, itens FROM checkpoint_paginas")}
    return {"rodada": linha[0], "total": linha[1], "total_paginas": linha[2],
            "comecou_em": datetime.fromisoformat(linha[3]), "paginas": paginas}


def descartar_checkpoint(con):
    con.execute("DELETE FROM checkpoint_paginas")
    con.execute("DELETE FROM checkpoint")


def problema_do_checkpoint(cp, rodada, total, total_paginas, agora):
    """Por que o checkpoint não serve para esta rodada. None quando serve."""
    if cp["rodada"] != rodada:
        antes, agora_ = json.loads(cp["rodada"]), json.loads(rodada)
        diferente = [f"{k} {antes.get(k)} e agora {agora_.get(k)}" for k in sorted(agora_) if antes.get(k) != agora_.get(k)]
        return "era de outra rodada: " + "; ".join(diferente)
    if (cp["total"], cp["total_paginas"]) != (total, total_paginas):
        return f"o total mudou de {cp['total']} para {total}"
    idade = agora - cp["comecou_em"]
    if idade > VALIDADE_CHECKPOINT:
        return (f"ele é de {int(idade.total_seconds() // 60)} min atrás, "
                f"e o limite é {int(VALIDADE_CHECKPOINT.total_seconds() // 60)}")
    return None


def conferir_pagina(corpo, pagina, por_pagina, total, total_paginas):
    """As conferências da aula 12 para uma página."""
    esperado = por_pagina if pagina < total_paginas else total - por_pagina * (total_paginas - 1)
    if corpo["pagina"] != pagina or corpo["por_pagina"] != por_pagina:
        raise ColetaIncompleta(f"pedi a página {pagina} com {por_pagina} por página e veio a página "
                               f"{corpo['pagina']} com {corpo['por_pagina']}")
    if corpo["total"] != total:
        raise ColetaIncompleta(f"o total mudou no meio da coleta: {total} no começo, {corpo['total']} na página {pagina}")
    if len(corpo["itens"]) != esperado:
        raise ColetaIncompleta(f"a página {pagina} trouxe {len(corpo['itens'])} itens; pela conta do envelope, "
                               f"deviam ser {esperado}")


def juntar(linhas):
    """Uma entrada por chave. Repetidos com o mesmo conteúdo viram um; com conteúdo diferente, a coleta para."""
    por_chave, repetidos = {}, {}
    for linha in linhas:
        k, c = chave(linha), conteudo(linha)
        if k not in por_chave:
            por_chave[k] = c
            continue
        if por_chave[k] != c:
            raise ColetaIncompleta(f"a inscrição {k[1]} veio mais de uma vez com conteúdos diferentes "
                                   f"(uma delas na página {linha['origem']['pagina']}); não escolhi uma")
        repetidos[k] = repetidos.get(k, 1) + 1
    return por_chave, repetidos


def comparar(con, edicao, por_chave):
    """O que a rodada muda na base: novos, mudaram (com antes e depois), iguais e os que não vieram."""
    na_base = dict(((e, i), c) for e, i, c in con.execute(
        "SELECT edicao, id_inscricao, conteudo FROM resultados WHERE edicao = ?", (edicao,)))
    novos = [(k, c) for k, c in sorted(por_chave.items()) if k not in na_base]
    mudaram = [(k, na_base[k], c) for k, c in sorted(por_chave.items()) if k in na_base and na_base[k] != c]
    iguais = sum(1 for k, c in por_chave.items() if na_base.get(k) == c)
    nao_vieram = [(k, c) for k, c in sorted(na_base.items()) if k not in por_chave]
    return {"novos": novos, "mudaram": mudaram, "iguais": iguais, "nao_vieram": nao_vieram}


def aplicar(con, diferencas, quando):
    """Grava novos e mudados. Os iguais e os que não vieram ficam como estão."""
    con.executemany("INSERT INTO resultados (edicao, id_inscricao, conteudo, entrou_em) VALUES (?, ?, ?, ?)",
                    [(e, i, c, quando) for (e, i), c in diferencas["novos"]])
    con.executemany("UPDATE resultados SET conteudo = ?, mudou_em = ? WHERE edicao = ? AND id_inscricao = ?",
                    [(depois, quando, e, i) for (e, i), _antes, depois in diferencas["mudaram"]])


def atualizar(con, endereco, token, edicao, por_pagina=100, espera=10, mostrar=print, falhas=None,
              dormir=time.sleep, relogio=agora_utc, do_zero=False, ao_aplicar=None):
    """Uma rodada completa. Retorna o resumo; levanta ColetaIncompleta ou Desisti sem mudar a base.

    ao_aplicar(con, diferencas, quando), se você passar, roda dentro da mesma transação que grava
    a base: se ela levantar uma exceção, nada da rodada fica gravado.
    """
    falhas = [] if falhas is None else falhas
    edicao = int(edicao)
    rodada = json.dumps({"rota": ROTA, "filtros": {"edicao": edicao}, "por_pagina": por_pagina}, sort_keys=True)
    pedir = lambda n: pedir_pagina(endereco, token, {"edicao": edicao}, n, por_pagina, espera, falhas, dormir, mostrar)
    try:
        primeira, chamada1 = pedir(1)
        total, total_paginas = primeira["total"], primeira["total_paginas"]
        conferir_pagina(primeira, 1, por_pagina, total, total_paginas)
        cp = ler_checkpoint(con)
        guardadas = {}
        if cp and do_zero:
            mostrar("descartei o checkpoint, como você pediu (--do-zero)")
        elif cp:
            motivo = problema_do_checkpoint(cp, rodada, total, total_paginas, relogio())
            if motivo:
                mostrar(f"descartei o checkpoint: {motivo}; comecei do zero")
            else:
                guardadas = {p: v for p, v in cp["paginas"].items() if p != 1}
                mostrar(f"retomei o checkpoint: {len(cp['paginas'])} páginas já tinham vindo; o total continua {total}")
        with con:
            if not guardadas:
                descartar_checkpoint(con)
                con.execute("INSERT INTO checkpoint VALUES (?, ?, ?, ?)",
                            (rodada, total, total_paginas, relogio().isoformat(timespec="seconds")))
            con.execute("INSERT OR REPLACE INTO checkpoint_paginas VALUES (1, ?, ?)",
                        (chamada1, json.dumps(primeira["itens"], ensure_ascii=False)))
        mostrar(f"página 1 de {total_paginas}: {len(primeira['itens'])} itens, guardada no checkpoint")

        linhas = []
        for posicao, item in enumerate(primeira["itens"], start=1):
            linhas.append(dict(item, origem={"pagina": 1, "posicao": posicao}))
        for pagina in range(2, total_paginas + 1):
            if pagina in guardadas:
                itens = guardadas[pagina][1]
                mostrar(f"página {pagina} de {total_paginas}: {len(itens)} itens, do checkpoint")
            else:
                corpo, chamada = pedir(pagina)
                conferir_pagina(corpo, pagina, por_pagina, total, total_paginas)
                itens = corpo["itens"]
                with con:
                    con.execute("INSERT OR REPLACE INTO checkpoint_paginas VALUES (?, ?, ?)",
                                (pagina, chamada, json.dumps(itens, ensure_ascii=False)))
                mostrar(f"página {pagina} de {total_paginas}: {len(itens)} itens, guardada no checkpoint")
            for posicao, item in enumerate(itens, start=1):
                linhas.append(dict(item, origem={"pagina": pagina, "posicao": posicao}))
        if len(linhas) != total:
            raise ColetaIncompleta(f"a soma das páginas deu {len(linhas)} linhas e o total da API é {total}")
        mostrar(f"total da API: {total}; linhas recebidas: {len(linhas)}. Bateu.")
        por_chave, repetidos = juntar(linhas)
    except ColetaIncompleta:
        with con:
            descartar_checkpoint(con)
        raise

    diferencas = comparar(con, edicao, por_chave)
    quando = relogio().isoformat(timespec="seconds")
    with con:
        aplicar(con, diferencas, quando)
        con.execute("INSERT INTO rodadas VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (quando, edicao, len(diferencas["novos"]), len(diferencas["mudaram"]), diferencas["iguais"],
                     len(diferencas["nao_vieram"]), len(guardadas), json.dumps(falhas, ensure_ascii=False)))
        if ao_aplicar:
            ao_aplicar(con, diferencas, quando)
        descartar_checkpoint(con)
    return {"edicao": edicao, "total_api": total, "linhas": len(linhas), "inscricoes": len(por_chave),
            "repetidos": repetidos, "paginas_do_checkpoint": sorted(guardadas), "falhas": falhas,
            "diferencas": diferencas}


def mostrar_resumo(base, r, mostrar=print):
    d = r["diferencas"]
    if r["repetidos"]:
        vezes = sorted(set(r["repetidos"].values()))
        mostrar(f"{len(r['repetidos'])} inscrições vieram {' ou '.join(map(str, vezes))} vezes com o mesmo conteúdo; "
                f"entrou uma de cada")
    nv = len(d["nao_vieram"])
    mostrar(f"{base}, edição {r['edicao']}: {len(d['novos'])} novos, {len(d['mudaram'])} mudaram, "
            f"{d['iguais']} iguais, {nv} {'não veio' if nv == 1 else 'não vieram'}")
    if d["mudaram"]:
        mostrar("  mudaram: " + ", ".join(k[1] for k, _a, _d in d["mudaram"]))
    if d["nao_vieram"]:
        ids = ", ".join(k[1] for k, _c in d["nao_vieram"])
        mostrar(f"  não veio dessa vez: {ids} (ficou na base como estava)" if nv == 1 else
                f"  não vieram dessa vez: {ids} (ficaram na base como estavam)")


def main():
    ap = argparse.ArgumentParser(description="Atualiza a base do triatlo sem duplicar, com checkpoint")
    ap.add_argument("--edicao", required=True, type=int)
    ap.add_argument("--base", default=BASE_PADRAO)
    ap.add_argument("--por-pagina", type=int, default=100)
    ap.add_argument("--endereco", default=os.environ.get("API_TRIATLO_URL", ENDERECO_PADRAO))
    ap.add_argument("--espera", type=float, default=10, help="tempo limite de cada chamada, em segundos (padrão 10)")
    ap.add_argument("--do-zero", action="store_true", help="descarta o checkpoint e começa a rodada do zero")
    a = ap.parse_args()

    token = os.environ.get("API_TRIATLO_TOKEN")
    if not token:
        print("ERROR falta a variável de ambiente API_TRIATLO_TOKEN. "
              "Defina no terminal antes de coletar (veja o README). Nenhuma chamada foi feita.", file=sys.stderr)
        return 2
    con = abrir(a.base)
    falhas = []
    try:
        r = atualizar(con, a.endereco, token, a.edicao, a.por_pagina, a.espera, falhas=falhas, do_zero=a.do_zero)
    except ColetaIncompleta as erro:
        if falhas:
            mostrar_falhas(falhas)
        print(f"ERROR coleta incompleta: {erro}. A base não mudou e o checkpoint foi descartado.", file=sys.stderr)
        return 1
    except Desisti as erro:
        mostrar_falhas(falhas)
        n = con.execute("SELECT count(*) FROM checkpoint_paginas").fetchone()[0]
        print(f"ERROR desisti: {erro}. A base não mudou; {n} páginas ficaram no checkpoint para a próxima rodada.",
              file=sys.stderr)
        return 3
    mostrar_falhas(falhas)
    mostrar_resumo(a.base, r)
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
