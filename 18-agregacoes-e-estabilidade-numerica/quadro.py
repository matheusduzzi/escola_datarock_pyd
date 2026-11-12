"""O quadro de estatísticas de 2025 do boletim. Seção 4 da aula.

Entram os atletas que concluíram 2025 com as cinco parciais: as mesmas linhas em todas as colunas.
O desvio usa ddof=0 (divide por n), o padrão do NumPy.
"""
import numpy as np

import parciais

r = parciais.carregar()
concluiu = (r["edicao"] == 2025) & (r["status"] == "concluiu")
completo = ~np.isnan(r["tempos"]).any(axis=1)
linhas = concluiu & completo
tempos = r["tempos"][linhas]
total = tempos.sum(axis=1)

print(f"2025: {linhas.sum()} concluíram com as 5 parciais, de {concluiu.sum()} que concluíram")
print("desvio com ddof=0 (divide por n)")
print()
print(f"{'etapa':<10}{'n':>5}" + "".join(f"{c:>10}" for c in ("média", "mediana", "desvio", "mínimo", "máximo")))
for nome, col in list(zip(parciais.ETAPAS, tempos.T)) + [("total", total)]:
    stats = (col.mean(), np.median(col), col.std(), col.min(), col.max())
    print(f"{nome:<10}{len(col):>5}" + "".join(f"{parciais.hms(v):>10}" for v in stats))
print()
print(f"média do tempo oficial, as mesmas {linhas.sum()} linhas: {parciais.hms(r['oficial'][linhas].mean())}")
print(f"média do tempo oficial, os {concluiu.sum()} que concluíram:  {parciais.hms(r['oficial'][concluiu].mean())}")
