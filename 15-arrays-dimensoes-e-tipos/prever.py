"""O pedido 1 da prática guiada: a forma e o tipo de cada conta.

    python3 prever.py
"""
import numpy as np

import parciais

r = parciais.carregar()
tempos, peito = r["tempos"], r["peito"]

CONTAS = [
    "tempos[0]",
    "tempos[:, 2] / 60",
    "tempos > 3600",
    "(tempos > 3600).sum()",
    "peito // 100",
    "peito / 100",
    "tempos.T.reshape(-1)",
    'np.array(r["texto"])',
]

for conta in CONTAS:
    v = eval(conta)
    print(f"{conta:<24} -> shape {np.shape(v)} | dtype {v.dtype}")
