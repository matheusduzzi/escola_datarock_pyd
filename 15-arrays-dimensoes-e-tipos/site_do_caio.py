"""A versão do Caio: os tempos guardados em int16 para o arquivo do site ficar menor.

    python3 site_do_caio.py

Mostra o que o int16 fez com a parcial vazia do peito 101 e com o tempo de chegada do peito 102,
os dois de 2024, e quantos tempos de chegada ficaram negativos.
"""
import warnings

import numpy as np

import parciais

r = parciais.carregar()
tempos = r["tempos"]
de_2024 = r["edicao"] == 2024
concluiu = r["status"] == "concluiu"

with warnings.catch_warnings(record=True) as avisos:
    warnings.simplefilter("always")
    tempos16 = tempos.astype(np.int16)
for aviso in avisos:
    print("Aviso do NumPy na conversão:", aviso.message)

print("tempos:  ", tempos.dtype, "|", tempos.nbytes, "bytes")
print("tempos16:", tempos16.dtype, "|", tempos16.nbytes, "bytes")

for peito in (101, 102):
    linha = (r["peito"] == peito) & de_2024
    print(f"\nPeito {peito} em 2024")
    print("  float64:", tempos[linha][0])
    print("  int16:  ", tempos16[linha][0])

# A chegada como o site calculava: uma etapa mais a outra
chegada16 = tempos16[:, 0] + tempos16[:, 1] + tempos16[:, 2] + tempos16[:, 3] + tempos16[:, 4]
linha102 = (r["peito"] == 102) & de_2024
print("\nChegada do peito 102, somando as colunas com +:", chegada16[linha102][0], chegada16.dtype)
print("Chegada do peito 102, com tempos16.sum(axis=1):", tempos16.sum(axis=1)[linha102][0], tempos16.sum(axis=1).dtype)
print("Chegada do peito 102, em float64:", tempos.sum(axis=1)[linha102][0])
print("\nConcluíram:", concluiu.sum(), "| com chegada negativa no site:", (concluiu & (chegada16 < 0)).sum())
