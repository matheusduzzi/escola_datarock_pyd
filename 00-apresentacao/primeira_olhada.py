"""A primeira olhada nos resultados do triatlo: a conta que eu mandaria para a Bia e o que ela não viu.

Rode de dentro da pasta 00-apresentacao:  python3 primeira_olhada.py
Lê ../dados/triatlo/api_resultados.json (a mesma resposta que a API local serve) e ../dados/triatlo/edicoes.csv.
"""
import json
from pathlib import Path

import pandas as pd

PASTA = Path(__file__).resolve().parent.parent / "dados" / "triatlo"


def hms(t):
    s = int(t.total_seconds())
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


def minutos(t):
    return f"{abs(t.total_seconds()) / 60:.1f}".replace(".", ",")


def medianas(tabela, coluna):
    concluiu = tabela[tabela["status"] == "concluiu"]
    return pd.to_timedelta(concluiu[coluna]).groupby(concluiu["edicao"]).median()


def linha(m):
    dif = m[2024] - m[2025]
    lado = "2025 mais rápida" if dif.total_seconds() > 0 else "2025 mais lenta"
    return f"   2024 {hms(m[2024])}   2025 {hms(m[2025])}   {lado} em {minutos(dif)} min"


resultados = pd.json_normalize(json.loads((PASTA / "api_resultados.json").read_text(encoding="utf-8")))
edicoes = pd.read_csv(PASTA / "edicoes.csv", index_col="edicao")

print("1. A conta direta: mediana do tempo oficial de quem concluiu")
print(linha(medianas(resultados, "tempo_oficial")))

print("2. O que essa conta não olhou")
repetidos = resultados.duplicated("id_inscricao").groupby(resultados["edicao"]).sum()
print(f"   resultados repetidos na API: 2024 {repetidos[2024]}, 2025 {repetidos[2025]}")
km = edicoes["natacao_km"].map(lambda x: f"{x:g}".replace(".", ","))
print(f"   natação: 2024 {km[2024]} km, 2025 {km[2025]} km"
      f" ({edicoes.loc[2025, 'observacao']})")

print("3. A mesma conta, com cada inscrição uma vez só")
unicos = resultados.drop_duplicates("id_inscricao").copy()
print(linha(medianas(unicos, "tempo_oficial")))

print("4. Sem a natação, que teve distância diferente")
unicos["sem_natacao"] = pd.to_timedelta(unicos["tempo_oficial"]) - pd.to_timedelta(unicos["parciais.natacao"])
print(linha(medianas(unicos, "sem_natacao")))
