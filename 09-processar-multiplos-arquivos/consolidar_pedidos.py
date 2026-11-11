"""Junta os pedidos da loja online de vários meses numa tabela só, com a origem de cada pedido.

    python3 consolidar_pedidos.py
    python3 consolidar_pedidos.py --ignorar "pedidos-online-setembro (1).json"
    python3 consolidar_pedidos.py --meses julho agosto setembro outubro novembro

1. Acha a pasta exportacoes/ a partir do lugar do programa, e não do terminal.
2. Olha a pasta inteira antes de ler: nome de cada arquivo, mês que falta, arquivo vazio.
3. Lê cada arquivo pelo contrato da aula 08 e olha se os pedidos são do mês do nome.
4. Olha se algum id_pedido aparece em mais de um arquivo.
Se aparece algum problema, mostra todos e termina com o código 1, sem gravar nada.
Se não, junta os arquivos na ordem dos meses, com as colunas arquivo e registro, e grava saida/.
"""
import argparse
import logging
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

from contrato_pedidos import ForaDoContrato, ler_pedidos

log = logging.getLogger("consolidar")

AQUI = Path(__file__).resolve().parent
ENTRADA = AQUI / "exportacoes"
SAIDA = AQUI / "saida" / "pedidos-consolidados.csv"
ANO = 2026
MESES = {"janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7,
         "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}
PADRAO = re.compile(r"pedidos-online-([a-zç]+)\.json")


class PastaComProblema(Exception):
    def __init__(self, problemas):
        super().__init__(f"a pasta tem {len(problemas)} problema(s). Nada foi gravado.")
        self.problemas = problemas


def mes_do_nome(nome):
    """O número do mês, se o nome segue o padrão; None se não segue."""
    achou = PADRAO.fullmatch(unicodedata.normalize("NFC", nome))  # o macOS pode gravar o "ç" decomposto
    return MESES.get(achou.group(1)) if achou else None


def olhar_pasta(pasta, meses, ignorar):
    """Escolhe os arquivos, um por mês pedido, e lista o que está fora do lugar."""
    problemas, por_mes = [], {}
    itens = sorted(pasta.iterdir())  # sorted só para as mensagens saírem sempre na mesma ordem
    nomes = {p.name for p in itens}
    problemas += [f"--ignorar: não achei {nome!r} na pasta" for nome in ignorar if nome not in nomes]
    for item in itens:
        if item.name.startswith("."):
            log.info("arquivo oculto, fora da conta: %s", item.name)
            continue
        if item.name in ignorar:
            log.info("fora da conta por decisão de quem rodou: %s", item.name)
            continue
        mes = mes_do_nome(item.name) if item.is_file() else None
        if mes is None:
            igual = [p.name for p in itens if p != item and p.is_file() and item.is_file()
                     and mes_do_nome(p.name) and p.read_bytes() == item.read_bytes()]
            extra = f" (os bytes são iguais aos de {igual[0]})" if igual else ""
            problemas.append(f"nome fora do padrão pedidos-online-<mês>.json: {item.name}{extra}")
        elif mes not in meses:
            log.info("mês fora do pedido, não entra: %s", item.name)
        else:
            por_mes[mes] = item
    nome_do_mes = {n: nome for nome, n in MESES.items()}
    problemas += [f"falta o arquivo de {nome_do_mes[m]}" for m in sorted(meses) if m not in por_mes]
    for mes, arquivo in por_mes.items():
        if arquivo.stat().st_size == 0:
            problemas.append(f"{arquivo.name}: arquivo vazio")
    return [por_mes[m] for m in sorted(por_mes)], problemas


def ler_arquivo(arquivo, mes):
    """Lê um arquivo pelo contrato, olha o mês dos pedidos e põe a origem de cada pedido."""
    problemas = []
    try:
        pedidos = ler_pedidos(arquivo)
    except ForaDoContrato as erro:
        return None, [f"{arquivo.name}: {p}" for p in erro.problemas]
    data = pedidos["data_pedido"]
    fora = pedidos[(data.dt.year != ANO) | (data.dt.month != mes)]
    if len(fora):
        primeiro = fora.index[0]
        problemas.append(f"{arquivo.name}: {len(fora)} pedido(s) que não são de {mes:02d}/{ANO}, o primeiro é o "
                         f"registro {primeiro + 1}, de {data[primeiro]:%d/%m/%Y}")
    pedidos.insert(0, "registro", range(1, len(pedidos) + 1))
    pedidos.insert(0, "arquivo", arquivo.name)
    return pedidos, problemas


def consolidar(pasta, meses, ignorar=()):
    arquivos, problemas = olhar_pasta(pasta, set(meses), set(ignorar))
    partes = []
    for arquivo in arquivos:
        if arquivo.stat().st_size == 0:
            continue
        pedidos, achados = ler_arquivo(arquivo, mes_do_nome(arquivo.name))
        problemas += achados
        if pedidos is not None:
            partes.append(pedidos)
    if partes:
        juntos = pd.concat(partes, ignore_index=True)
        repetidos = juntos[juntos["id_pedido"].duplicated(keep=False)]
        if len(repetidos):
            id_pedido = repetidos["id_pedido"].iloc[0]
            onde = repetidos[repetidos["id_pedido"] == id_pedido]
            lugares = " e em ".join(f"{a} (registro {r})" for a, r in zip(onde["arquivo"], onde["registro"]))
            problemas.append(f"id_pedido em mais de um arquivo: {repetidos['id_pedido'].nunique()} pedido(s); "
                             f"o primeiro é {id_pedido}, em {lugares}")
    if problemas:
        raise PastaComProblema(problemas)
    return juntos


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description="Junta os pedidos de vários meses, com a origem de cada pedido.")
    ap.add_argument("--pasta", type=Path, default=ENTRADA, help="pasta com as exportações (padrão: exportacoes/)")
    ap.add_argument("--meses", nargs="+", default=["julho", "agosto", "setembro", "outubro"], choices=list(MESES))
    ap.add_argument("--ignorar", action="append", default=[], help="nome de arquivo que fica fora, por decisão sua")
    args = ap.parse_args()
    try:
        pedidos = consolidar(args.pasta, [MESES[m] for m in args.meses], args.ignorar)
    except PastaComProblema as erro:
        log.error("%s", erro)
        for problema in erro.problemas:
            log.error("  %s", problema)
        return 1
    resumo = pedidos.groupby("arquivo", sort=False).agg(pedidos=("id_pedido", "size"), valor=("valor", "sum"))
    print(f"{len(resumo)} arquivos, na ordem dos meses:")
    print(resumo.round(2).to_string())
    print("total:", len(pedidos), "pedidos")
    print("a soma dos arquivos bate com a tabela:", int(resumo["pedidos"].sum()) == len(pedidos))
    SAIDA.parent.mkdir(exist_ok=True)
    pedidos.to_csv(SAIDA, index=False)
    print(f"gravei {SAIDA.relative_to(AQUI)}, com o arquivo e o registro de cada pedido")
    return 0


if __name__ == "__main__":
    sys.exit(main())
