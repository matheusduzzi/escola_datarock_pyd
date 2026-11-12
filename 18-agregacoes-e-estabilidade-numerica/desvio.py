"""Pedido 3 da prática guiada: o desvio da natação de 2025 no NumPy e no pandas."""
import numpy as np
import pandas as pd

import parciais

r = parciais.carregar()
linhas = ((r["edicao"] == 2025) & (r["status"] == "concluiu")
          & ~np.isnan(r["tempos"]).any(axis=1))
natacao = r["tempos"][linhas, 0]

a = np.std(natacao)
b = np.std(natacao, ddof=1)
c = pd.Series(natacao).std()
print(f"{len(natacao)} tempos de natação")
print(f"A  np.std(natacao)          -> {a:.4f} s")
print(f"B  np.std(natacao, ddof=1)  -> {b:.4f} s")
print(f"C  pd.Series(natacao).std() -> {c:.4f} s")
for nome, x, y in (("A e C", a, c), ("B e C", b, c)):
    print(f"{nome}: diferença {x - y:+.2e} s | np.isclose(rtol=0, atol=0.001): {np.isclose(x, y, rtol=0, atol=0.001)}")
