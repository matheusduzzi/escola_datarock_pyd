"""O que um array guarda: forma, número de dimensões, tamanho e tipo.

    python3 explorar.py
"""
import numpy as np

import parciais

r = parciais.carregar()
tempos = r["tempos"]

print("tempos.shape:", tempos.shape, "| ndim:", tempos.ndim, "| size:", tempos.size, "| dtype:", tempos.dtype)
print("peito:", r["peito"].dtype, "| edicao:", r["edicao"].dtype, "| status:", r["status"].dtype)
print("status == 'concluiu':", (r["status"] == "concluiu").dtype)

print("\nAs parciais do peito 102 em 2024, como vieram no arquivo:")
linha102 = np.array(r["texto"][1])
print(" ", linha102, linha102.dtype)
print("As do peito 101 em 2024, com a T1 vazia:")
linha101 = np.array(r["texto"][0])
print(" ", linha101, linha101.dtype)

print("\nUm número inteiro, um decimal e um vazio juntos:")
misto = np.array([4459, 310.5, np.nan])
print(" ", misto, misto.dtype)
print("Um número e um texto juntos:")
texto = np.array([4459, "0:05:10"])
print(" ", texto, texto.dtype)
