"""Lê os pedidos da loja online pelo contrato de entrada (contrato-pedidos-online.md).

    python3 ler_pedidos_online.py                                    # o JSON de julho
    python3 ler_pedidos_online.py --arquivo pedidos-online-julho.csv
    python3 ler_pedidos_online.py --arquivo pedidos-online-agosto.json
    python3 ler_pedidos_online.py --comparar                         # CSV e JSON de julho

Primeiro lê tudo sem deixar o pandas adivinhar nada. Depois olha cada campo contra o contrato.
Se algum campo não segue, mostra todos os problemas e termina com o código 1, sem tabela.
Se tudo segue, converte cada campo para o tipo do contrato.
"""
import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

log = logging.getLogger("pedidos")

# O contrato, campo por campo: tipo, se pode vir vazio e, quando há, o formato ou os valores aceitos.
CAMPOS = {
    "id_pedido":      {"tipo": "texto",       "vazio": False, "formato": r"\d{6}",
                       "como": "texto com 6 dígitos"},
    "id_cliente":     {"tipo": "inteiro",     "vazio": False},
    "id_produto":     {"tipo": "inteiro",     "vazio": False},
    "data_pedido":    {"tipo": "data e hora", "vazio": False},
    "cidade_entrega": {"tipo": "texto",       "vazio": False},
    "quantidade":     {"tipo": "inteiro",     "vazio": False, "minimo": 1, "como": "inteiro, 1 ou mais"},
    "valor":          {"tipo": "decimal",     "vazio": False},
    "cupom":          {"tipo": "texto",       "vazio": True},
    "status":         {"tipo": "texto",       "vazio": False, "valores": {"pago", "enviado", "entregue", "cancelado"},
                       "como": "pago, enviado, entregue ou cancelado"},
}
FUSO = "America/Sao_Paulo"

# O contrato do arquivo. Os campos são os mesmos; muda como cada formato escreve o valor.
ARQUIVO = {
    ".csv": {"codificacao": "cp1252", "separador": ";", "decimal": ",", "data": "%d/%m/%Y %H:%M"},
    ".json": {"codificacao": "utf-8", "data": "ISO8601"},
}
PANDAS = {"texto": "string", "inteiro": "int64", "decimal": "float64"}


class ForaDoContrato(Exception):
    def __init__(self, arquivo, problemas):
        super().__init__(f"{arquivo} não segue o contrato. Nada foi lido.")
        self.problemas = problemas


def ler_cru(caminho):
    """O arquivo como veio, sem conversão: no CSV tudo é texto; no JSON, o tipo que o JSON escreveu."""
    regra = ARQUIVO[caminho.suffix]
    if caminho.suffix == ".csv":
        return pd.read_csv(caminho, encoding=regra["codificacao"], sep=regra["separador"],
                           dtype=str, keep_default_na=False)
    return pd.read_json(caminho, encoding=regra["codificacao"], dtype=False)


def vazio(valor):
    return valor is None or valor == "" or (isinstance(valor, float) and pd.isna(valor))


def data_valida(texto, formato):
    try:
        datetime.strptime(texto, formato)
    except ValueError:
        return False
    return True


def segue(valor, campo, formato):
    """O valor segue o tipo do campo? No CSV, olha o texto; no JSON, o tipo que veio."""
    tipo = CAMPOS[campo]["tipo"]
    if formato == ".csv":
        if tipo == "data e hora":
            return data_valida(valor, ARQUIVO[".csv"]["data"])
        decimal = re.escape(ARQUIVO[".csv"]["decimal"])
        padroes = {"texto": r".+", "inteiro": r"\d+", "decimal": rf"\d+({decimal}\d{{1,2}})?"}
        return re.fullmatch(padroes[tipo], valor) is not None
    if tipo == "data e hora":
        return isinstance(valor, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", valor) is not None
    if tipo == "texto":
        return isinstance(valor, str)
    if tipo == "inteiro":
        return isinstance(valor, int) and not isinstance(valor, bool)
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def conferir(cru, nome, formato):
    problemas = []
    faltam = [c for c in CAMPOS if c not in cru.columns]
    sobram = [c for c in cru.columns if c not in CAMPOS]
    problemas += [f"campo que falta: {c}" for c in faltam] + [f"campo que não está no contrato: {c}" for c in sobram]
    for campo, regra in CAMPOS.items():
        if campo in faltam:
            continue
        erradas = []
        for posicao, valor in enumerate(cru[campo], start=1):
            if vazio(valor):
                ok = regra["vazio"]
            else:
                ok = segue(valor, campo, formato)
                if ok and "formato" in regra:
                    ok = re.fullmatch(regra["formato"], str(valor)) is not None
                if ok and "valores" in regra:
                    ok = valor in regra["valores"]
                if ok and "minimo" in regra:
                    ok = int(valor) >= regra["minimo"]
            if not ok:
                erradas.append((posicao, valor))
        if erradas:
            posicao, valor = erradas[0]
            problemas.append(f"{campo}: {len(erradas)} registro(s) fora do contrato ({regra.get('como', regra['tipo'])}), "
                             f"o primeiro é o registro {posicao}, com {valor!r}")
    if "id_pedido" in cru.columns:
        repetidos = cru["id_pedido"][cru["id_pedido"].duplicated()].tolist()
        if repetidos:
            problemas.append(f"id_pedido repetido: {repetidos}")
    if problemas:
        raise ForaDoContrato(nome, problemas)


def converter(cru, formato):
    regra = ARQUIVO[formato]
    pedidos = pd.DataFrame(index=cru.index)
    for campo, contrato in CAMPOS.items():
        coluna = cru[campo]
        if contrato["tipo"] == "data e hora":
            if formato == ".csv":
                pedidos[campo] = pd.to_datetime(coluna, format=regra["data"]).dt.tz_localize(FUSO)
            else:
                pedidos[campo] = pd.to_datetime(coluna, format=regra["data"], utc=True).dt.tz_convert(FUSO)
        elif contrato["tipo"] == "decimal" and formato == ".csv":
            pedidos[campo] = coluna.str.replace(regra["decimal"], ".", regex=False).astype("float64")
        elif contrato["vazio"]:
            pedidos[campo] = coluna.where(~coluna.map(vazio), None).astype(PANDAS[contrato["tipo"]])
        else:
            pedidos[campo] = coluna.astype(PANDAS[contrato["tipo"]])
    return pedidos


def ler_pedidos(caminho):
    caminho = Path(caminho)
    cru = ler_cru(caminho)
    conferir(cru, caminho.name, caminho.suffix)
    return converter(cru, caminho.suffix)


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description="Lê os pedidos da loja online pelo contrato de entrada.")
    ap.add_argument("--arquivo", default="pedidos-online-julho.json")
    ap.add_argument("--comparar", action="store_true", help="lê o CSV e o JSON de julho e compara")
    args = ap.parse_args()
    try:
        if args.comparar:
            do_csv = ler_pedidos("pedidos-online-julho.csv")
            do_json = ler_pedidos("pedidos-online-julho.json")
            print("CSV e JSON de julho, lidos pelo contrato, dão a mesma tabela:", do_csv.equals(do_json))
            return 0
        pedidos = ler_pedidos(args.arquivo)
    except ForaDoContrato as erro:
        log.error("%s", erro)
        for problema in erro.problemas:
            log.error("  %s", problema)
        return 1
    print(f"{Path(args.arquivo).name}: {len(pedidos)} pedidos, segue o contrato.")
    print(pedidos.dtypes)
    print(pedidos.loc[0, ["id_pedido", "data_pedido", "valor", "cupom"]].to_dict())
    return 0


if __name__ == "__main__":
    sys.exit(main())
