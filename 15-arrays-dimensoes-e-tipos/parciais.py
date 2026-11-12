"""Lê os resultados do triatlo e monta os arrays da aula «Arrays, dimensões e tipos».

    import parciais
    r = parciais.carregar()
    r["tempos"]   # array (n, 5) em segundos: natação, t1, ciclismo, t2, corrida; nan quando a parcial está vazia
    r["peito"]    # número de peito de cada linha
    r["edicao"]   # 2024 ou 2025
    r["status"]   # concluiu, DNF, DNS ou DSQ
    r["texto"]    # as parciais como vieram no arquivo, uma lista por linha ('1:14:19' ou None)

O arquivo é o mesmo que a API local serve (../dados/triatlo/api_resultados.json).
Resultado repetido (mesma inscrição duas vezes) entra uma vez só.
"""
import json
from pathlib import Path

import numpy as np

ETAPAS = ("natacao", "t1", "ciclismo", "t2", "corrida")
ARQUIVO = Path(__file__).resolve().parent.parent / "dados" / "triatlo" / "api_resultados.json"


def segundos(texto):
    """'1:18:29' vira 4709.0; parcial vazia (None) vira nan, e não zero."""
    if texto is None:
        return np.nan
    h, m, s = (int(p) for p in texto.split(":"))
    return float(h * 3600 + m * 60 + s)


def hms(seg):
    """4709.0 vira '1:18:29'; nan vira '-'."""
    if np.isnan(seg):
        return "-"
    seg = int(round(seg))
    return f"{seg // 3600}:{seg % 3600 // 60:02d}:{seg % 60:02d}"


def carregar(arquivo=ARQUIVO):
    itens = json.loads(Path(arquivo).read_text(encoding="utf-8"))
    vistos, linhas = set(), []
    for item in itens:
        if item["id_inscricao"] in vistos:
            continue
        vistos.add(item["id_inscricao"])
        linhas.append(item)
    return {
        "peito": np.array([i["numero_peito"] for i in linhas]),
        "edicao": np.array([i["edicao"] for i in linhas]),
        "status": np.array([i["status"] for i in linhas]),
        "tempos": np.array([[segundos(i["parciais"][e]) for e in ETAPAS] for i in linhas]),
        "texto": [[i["parciais"][e] for e in ETAPAS] for i in linhas],
        "repetidos": len(itens) - len(linhas),
    }
