"""A média de cada etapa de 2025 de três jeitos. Seção 3 da aula.

    python3 media.py              # todas as inscrições de 2025
    python3 media.py --concluiu   # só quem concluiu
"""
import sys

import numpy as np

import parciais

r = parciais.carregar()
linhas = r["edicao"] == 2025
if "--concluiu" in sys.argv:
    linhas &= r["status"] == "concluiu"
tempos = r["tempos"][linhas]


def linha(nome, valores):
    print(f"{nome:<20}" + "".join(f"{parciais.hms(v) if not np.isnan(v) else 'nan':>10}" for v in valores))


print(f"{len(tempos)} linhas de 2025")
print(f"{'conta':<20}" + "".join(f"{e:>10}" for e in parciais.ETAPAS))
linha("np.mean", np.mean(tempos, axis=0))
linha("np.nanmean", np.nanmean(tempos, axis=0))
print(f"{'  linhas usadas':<20}" + "".join(f"{n:>10}" for n in (~np.isnan(tempos)).sum(axis=0)))
linha("nan_to_num + mean", np.nan_to_num(tempos).mean(axis=0))
print(f"{'  linhas usadas':<20}" + "".join(f"{len(tempos):>10}" for _ in parciais.ETAPAS))
