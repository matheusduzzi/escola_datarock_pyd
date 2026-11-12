"""O pedido 2 da prática guiada: o que acontece quando o número não cabe no tipo.

    python3 limites.py
"""
import numpy as np

print("int8:", np.iinfo(np.int8).min, "a", np.iinfo(np.int8).max,
      "| int16:", np.iinfo(np.int16).min, "a", np.iinfo(np.int16).max)

ciclismo = np.array([21755], dtype=np.int16)   # ciclismo do peito 102 em 2024
corrida = np.array([17144], dtype=np.int16)    # corrida do mesmo atleta

CONTAS = [
    "np.array([2024, 2025], dtype=np.int8)",
    "np.array([2024, 2025]).astype(np.int8)",
    "ciclismo + corrida",
    "ciclismo.astype(np.int32) + corrida",
    "np.array([21755, 17144], dtype=np.int16).sum()",
    "ciclismo + 40000",
]

for conta in CONTAS:
    try:
        v = eval(conta)
        print(f"{conta:<48} -> {v} | {v.dtype}")
    except OverflowError as erro:
        print(f"{conta:<48} -> OverflowError: {erro}")
