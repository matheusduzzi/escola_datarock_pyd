"""A forma de cada pedaço dos tempos, e de cada resultado.

    python3 dimensoes.py
"""
import numpy as np

import parciais

tempos = parciais.carregar()["tempos"]

PEDACOS = [
    "tempos",
    "tempos[1]",
    "tempos[:, 0]",
    "tempos.T",
    "tempos.reshape(-1)",
    "tempos.reshape(5, 873)",
    "np.nansum(tempos)",
    "tempos.reshape(2, -1)",
]

for pedaco in PEDACOS:
    try:
        v = eval(pedaco)
        print(f"{pedaco:<24} -> shape {np.shape(v)} | ndim {np.ndim(v)}")
    except ValueError as erro:
        print(f"{pedaco:<24} -> ValueError: {erro}")
