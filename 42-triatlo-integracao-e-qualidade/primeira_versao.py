"""A primeira versão da base, do jeito que a IA escreveu quando eu pedi "junta tudo numa tabela".

    python3 primeira_versao.py

Roda sem erro e não grava nada. A seção 1 da aula mostra o que ela conta errado.
Ela lê os resultados direto do arquivo que a API serve, como a aula 41 fazia.
"""
import json
from pathlib import Path

import pandas as pd

DADOS = Path(__file__).resolve().parent.parent / "dados" / "triatlo"
ETAPAS = ["natacao", "t1", "ciclismo", "t2", "corrida"]

i24 = pd.read_csv(DADOS / "inscricoes_2024.csv")
i25 = pd.read_csv(DADOS / "inscricoes_2025.csv", sep=";")
inscricoes = pd.concat([i24, i25])

with open(DADOS / "api_resultados.json", encoding="utf-8") as f:
    resultados = pd.json_normalize(json.load(f))

base = inscricoes.merge(resultados, on="id_inscricao")
for etapa in ETAPAS:
    base[etapa] = pd.to_timedelta(base[f"parciais.{etapa}"]).fillna(pd.Timedelta(0))
base["tempo_total"] = base[ETAPAS].sum(axis=1)

print("linhas da base:", len(base))
print(base.groupby("edicao")["status"].value_counts().unstack().to_string())
concluiu = base[base["status"] == "concluiu"]
print("mediana da T1 de quem concluiu em 2024:", concluiu[concluiu["edicao"] == 2024]["t1"].median())
uma = base[base["id_inscricao"] == "2024-0001"].iloc[0]
print("2024-0001: tempo_total", str(uma["tempo_total"])[7:], "| tempo_oficial", uma["tempo_oficial"])
