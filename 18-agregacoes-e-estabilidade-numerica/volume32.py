"""A soma das horas de prova de 1 milhão de linhas, em float64 e em float32. Seção 8 da aula.

Usa o volume.py da aula «Vetorização e custo»: as linhas de quem concluiu 2024, repetidas até o volume pedido.
"""
import math

import numpy as np

import volume

horas = volume.gerar(1_000_000).sum(axis=1) / 3600
horas32 = horas.astype(np.float32)
certo = math.fsum(horas)

print(f"linhas: {len(horas)} | float64: {horas.nbytes / 1e6:.0f} MB | float32: {horas32.nbytes / 1e6:.0f} MB")
print()
print(f"{'conta':<26}{'soma das horas':>18}{'diferença':>14}")
for nome, valor in [("math.fsum (referência)", certo),
                    ("float64, np.sum", horas.sum()),
                    ("float64, np.cumsum", np.cumsum(horas)[-1]),
                    ("float32, np.sum", horas32.sum()),
                    ("float32, np.cumsum", np.cumsum(horas32)[-1]),
                    ("float32, soma em float64", np.sum(horas32, dtype=np.float64))]:
    print(f"{nome:<26}{float(valor):>18.3f}{float(valor) - certo:>14.6f}")
print()
print(f"média em float64: {horas.mean():.6f} h | em float32: {float(horas32.mean()):.6f} h")
