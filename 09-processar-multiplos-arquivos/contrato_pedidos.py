"""O contrato de entrada dos pedidos da loja online, da aula «Formatos e contratos de entrada».

É o mesmo código do ler_pedidos_online.py daquela aula, sem o comando: só o contrato e a leitura.
O consolidar_pedidos.py usa a função ler_pedidos(caminho) para ler cada arquivo da pasta.
Se o arquivo não segue o contrato, ler_pedidos levanta ForaDoContrato com a lista de problemas.
"""
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

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
