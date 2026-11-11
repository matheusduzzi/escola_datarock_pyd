"""Roda cada conta do pedido 1 da prática guiada e mostra a forma do resultado ou o erro.

    python3 formas.py

Os valores são zeros e uns: aqui só a forma importa.
"""
import numpy as np

tempos = np.zeros((366, 5))     # 366 atletas, 5 etapas
mediana = np.ones(5)            # uma por etapa
total = np.ones(366)            # um por atleta
distancias = np.ones((2, 3))    # 2 edições, 3 modalidades
edicao = np.zeros(366, dtype=int)  # 0 ou 1 para cada atleta

CONTAS = [
    "tempos - mediana",
    "tempos / total",
    "tempos / total[:, np.newaxis]",
    "tempos[:, 0] - total",
    "tempos[:, [0, 2, 4]] / distancias",
    "tempos[:, [0, 2, 4]] / distancias[edicao]",
]

for conta in CONTAS:
    try:
        print(f"{conta:<42} -> {eval(conta).shape}")
    except ValueError as erro:
        print(f"{conta:<42} -> ValueError: {erro}")
