"""Monta a base do projeto do triatlo: arquivos de inscrição, cadastro e resultados pela API.

Com a API do kit ligada em outro terminal (veja o README):

    python3 rodar.py
    python3 rodar.py --saida outra_pasta

O token vem da variável de ambiente API_TRIATLO_TOKEN, como nas aulas 11 a 13.
O endereço padrão é o da API do kit, porta 8765 (ou --endereco, ou API_TRIATLO_URL).

Passos, cada um com a contagem na tela:
  1. lê os dois arquivos de inscrição e o cadastro;
  2. coleta 2024 e 2025 pela API, com as tentativas da aula 13;
  3. junta as cópias repetidas dos resultados;
  4. monta a base, uma linha por inscrição;
  5. passa as regras do contrato.
Só grava saida/base_triatlo.csv e saida/conferencia.txt se tudo passou.

Código de saída:
  0  base gravada
  1  a coleta não bateu, os dados quebraram uma regra ou vieram duas versões da mesma coisa; nada foi gravado
  2  falta a variável API_TRIATLO_TOKEN; nenhuma chamada foi feita
  3  a API falhou e não voltou dentro das tentativas; nada foi gravado
"""
import argparse
import os
import sys
import tempfile
from pathlib import Path

import pandas as pd

import coletar
import integrar

EDICOES = ["2024", "2025"]


class Tela:
    """Mostra cada linha e guarda uma cópia para o conferencia.txt."""

    def __init__(self):
        self.linhas = []

    def __call__(self, texto=""):
        print(texto, flush=True)
        self.linhas.append(texto)


def coletar_edicoes(endereco, token, espera, tela):
    """Coleta 2024 e 2025. Cada falha do caminho vai para a tela, inclusive as que passaram."""
    linhas, falhas = [], []
    for edicao in EDICOES:
        desta = []
        try:
            recebidas, resumo = coletar.coletar(endereco, token, {"edicao": edicao}, por_pagina=100,
                                                espera=espera, mostrar=lambda texto: None, falhas=desta)
        except (coletar.Desisti, coletar.ColetaIncompleta):
            mostrar_falhas(falhas + [dict(f, edicao=edicao) for f in desta], tela)
            raise
        falhas += [dict(f, edicao=edicao) for f in desta]
        tela(f"{edicao}: {resumo['linhas']} resultados em {resumo['total_paginas']} páginas; "
             f"total da API {resumo['total_api']}")
        linhas += recebidas
    mostrar_falhas(falhas, tela)
    return linhas


def mostrar_falhas(falhas, tela):
    if not falhas:
        tela("nenhuma falha no caminho")
        return
    tela(f"falhas no caminho: {len(falhas)}")
    for f in falhas:
        tela(f"  {f['edicao']}, página {f['pagina']}, tentativa {f['tentativa']}: {f['o_que']}; {f['depois']}")


def gravar_csv(tabela, caminho):
    """Grava num temporário da mesma pasta e só então troca pelo nome final."""
    fd, temporario = tempfile.mkstemp(dir=caminho.parent, prefix=caminho.name + ".", suffix=".tmp")
    os.close(fd)
    try:
        tabela.to_csv(temporario, index=False)
        os.replace(temporario, caminho)
    except BaseException:
        os.unlink(temporario)
        raise


def montar(endereco, token, espera, tela):
    """Os passos 1 a 5. Retorna a base; para com exceção se alguma coisa não bate."""
    tela("== 1. Arquivos")
    inscricoes, contagem = integrar.ler_inscricoes(integrar.DADOS)
    for nome, c in contagem.items():
        tela(f"{nome}: {c['linhas']} linhas, {c['repetidas']} repetidas idênticas saem, {c['inscricoes']} inscrições")
    atletas = integrar.ler_atletas(integrar.DADOS)
    tela(f"atletas.csv: {len(atletas)} atletas")

    tela("\n== 2. Resultados pela API")
    linhas = coletar_edicoes(endereco, token, espera, tela)

    tela("\n== 3. Cópias repetidas dos resultados")
    resultados, repetidos = integrar.unificar_resultados(linhas)
    tela(f"{len(linhas)} linhas da coleta, {len(repetidos)} inscrições vieram duas vezes, "
         f"{len(resultados)} resultados")
    em_duas = [k for k, v in repetidos.items() if len({o["pagina"] for o in v}) > 1]
    tela(f"cópias em páginas diferentes: {len(em_duas)}")
    for chave in em_duas[:2]:
        tela(f"  {chave}: " + "; ".join(f"página {o['pagina']} posição {o['posicao']}" for o in repetidos[chave]))

    tela("\n== 4. Base, uma linha por inscrição")
    base = integrar.montar_base(inscricoes, atletas, resultados)
    tela(f"{len(base)} linhas, {base['id_inscricao'].nunique()} inscrições")
    tabela = pd.crosstab(base["edicao"], base["status"], margins=True, margins_name="total")
    tela(tabela.reindex(columns=integrar.STATUS + ["total"], fill_value=0).to_string())
    vazias = base[(base["status"] == "concluiu") & (base["parciais_vazias"] > 0)]
    etapas = {e: int(vazias[f"{e}_s"].isna().sum()) for e in integrar.ETAPAS}
    tela(f"concluiu com parcial vazia: {len(vazias)} | " + " ".join(f"{e}={n}" for e, n in etapas.items()))

    tela("\n== 5. Regras do contrato")
    problemas = integrar.conferir(base)
    tela(f"{integrar.QUANTAS_REGRAS} regras, {len(problemas)} problema(s)")
    for p in problemas:
        tela(f"  {p}")
    if problemas:
        raise integrar.RegraQuebrada(f"a base quebrou {len(problemas)} regra(s) do contrato")
    return base


def main(argv=None):
    ap = argparse.ArgumentParser(description="Monta e confere a base do triatlo")
    ap.add_argument("--saida", default="saida", help="pasta onde a base é gravada (padrão saida)")
    ap.add_argument("--endereco", default=os.environ.get("API_TRIATLO_URL", coletar.ENDERECO_PADRAO))
    ap.add_argument("--espera", type=float, default=10, help="tempo limite de cada chamada, em segundos")
    a = ap.parse_args(argv)

    token = os.environ.get("API_TRIATLO_TOKEN")
    if not token:
        print("ERROR falta a variável de ambiente API_TRIATLO_TOKEN. "
              "Defina no terminal antes de rodar (veja o README). Nenhuma chamada foi feita.", file=sys.stderr)
        return 2
    tela = Tela()
    try:
        base = montar(a.endereco, token, a.espera, tela)
    except (coletar.ColetaIncompleta, integrar.InscricaoConflitante, integrar.ResultadoConflitante,
            integrar.ResultadoSemInscricao, integrar.AtletaSemCadastro, integrar.RegraQuebrada) as erro:
        print(f"ERROR {erro}. Nada foi gravado em {a.saida}/.", file=sys.stderr)
        return 1
    except coletar.Desisti as erro:
        print(f"ERROR desisti: {erro}. Nada foi gravado em {a.saida}/.", file=sys.stderr)
        return 3
    pasta = Path(a.saida)
    pasta.mkdir(exist_ok=True)
    gravar_csv(base, pasta / "base_triatlo.csv")
    tela(f"\ngravei {pasta / 'base_triatlo.csv'}: {len(base)} linhas, {len(base.columns)} colunas")
    (pasta / "conferencia.txt").write_text("\n".join(tela.linhas) + "\n", encoding="utf-8")
    print(f"e a tela inteira em {pasta / 'conferencia.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
