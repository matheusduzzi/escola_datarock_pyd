"""Os tempos do triatlo num array: forma, tipo e as primeiras seleções.

    python3 explorar.py
"""
import numpy as np

import parciais

r = parciais.carregar()
tempos = r["tempos"]

print("Resultados lidos:", len(tempos), "| repetidos que ficaram de fora:", r["repetidos"])
print("tempos.shape:", tempos.shape, "| tempos.dtype:", tempos.dtype)
print("Colunas:", ", ".join(parciais.ETAPAS))

print("\nLinha 1, tempos[1]:", tempos[1])
print("Natação das 3 primeiras linhas, tempos[:3, 0]:", tempos[:3, 0])
print("Natação, ciclismo e corrida das 2 primeiras, tempos[:2, [0, 2, 4]]:")
print(tempos[:2, [0, 2, 4]])

concluiu = r["status"] == "concluiu"
completo = ~np.isnan(tempos).any(axis=1)
de_2024 = r["edicao"] == 2024
print("\nconcluiu:", concluiu.shape, concluiu.dtype, "| True em", concluiu.sum(), "linhas")
print("Concluíram em 2024:", (concluiu & de_2024).sum())
print("Concluíram em 2024 com as 5 parciais:", (concluiu & de_2024 & completo).sum())
vazias = concluiu & ~completo
print("Concluíram com alguma parcial vazia:", vazias.sum(), "| peitos:", r["peito"][vazias & de_2024], "em 2024")
print("Linha do peito 101 em 2024:", tempos[(r["peito"] == 101) & de_2024])
