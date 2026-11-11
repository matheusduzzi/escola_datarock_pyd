"""A primeira versão do resumo do balanço, do jeito que a IA escreveu para o Caio.

Roda sem erro, e cada frase tem uma conta por trás. A aula mostra o que cada frase compara.
De dentro da pasta da aula:  python3 primeira_analise.py
"""
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
base = pd.read_csv(AQUI / "dados_da_aula" / "base_triatlo.csv")
edicoes = pd.read_csv(AQUI.parent / "dados" / "triatlo" / "edicoes.csv").set_index("edicao")
conc = base[base["status"] == "concluiu"]

oficial = conc.groupby("edicao")["oficial_s"].median() / 60
print(f"1. A edição de 2025 foi {oficial[2024] - oficial[2025]:.1f} minutos mais rápida que a de 2024.")

ritmo = conc.groupby("edicao")["natacao_s"].median() / 60 / (edicoes["natacao_km"] * 10)
print(f"2. Os atletas nadaram mais rápido em 2025: {ritmo[2025]:.2f} min por 100 m, contra {ritmo[2024]:.2f}.")

corrida = conc.groupby("edicao")["corrida_s"].median() / 60
print(f"3. O calor deixou a corrida {corrida[2025] - corrida[2024]:.0f} minutos mais lenta em todas as categorias.")

dnf = base[base["edicao"] == 2025].groupby("categoria")["status"].apply(lambda s: (s == "DNF").mean() * 100)
print(f"4. {dnf.idxmax()} é a categoria que mais desiste: {dnf.max():.1f}% em 2025.")

taxa = base.groupby("edicao")["status"].apply(lambda s: (s == "DNF").mean() * 100)
print(f"5. A desistência subiu de {taxa[2024]:.1f}% para {taxa[2025]:.1f}%.")
