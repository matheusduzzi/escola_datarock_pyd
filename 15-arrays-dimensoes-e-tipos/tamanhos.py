"""O pedido 3 da prática guiada: quantos bytes cada array ocupa.

    python3 tamanhos.py
"""
import numpy as np

import parciais

r = parciais.carregar()
tempos = r["tempos"]

ARRAYS = [
    'r["peito"]',
    'r["status"]',
    'r["status"] == "concluiu"',
    "tempos.T",
]

for nome in ARRAYS:
    v = eval(nome)
    print(f"{nome:<26} -> {str(v.shape):<9} {str(v.dtype):<7} itemsize {v.itemsize:>2} | nbytes {v.nbytes:>6}"
          f" | usa os números de outro array: {v.base is not None}")
