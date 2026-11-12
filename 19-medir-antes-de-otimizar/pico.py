"""Pedido 1 da prática guiada: quanto de memória cada conta pede, com 1 milhão de linhas.

    python3 pico.py
"""
import numpy as np

import medir
import volume

tempos = volume.gerar(1_000_000)
print(f"tempos: {tempos.shape} {tempos.dtype} | nbytes {medir.mb(tempos.nbytes)}")
print()


def centrar_e_dividir():
    return (tempos - tempos.mean(axis=0)) / 60


def centrar_e_dividir_no_lugar():
    x = tempos - tempos.mean(axis=0)
    x /= 60
    return x


contas = [
    ("A  tempos.sum(axis=1)", lambda: tempos.sum(axis=1)),
    ("B  tempos.astype(np.float32)", lambda: tempos.astype(np.float32)),
    ("C  np.median(tempos[:, 2])", lambda: np.median(tempos[:, 2])),
    ("D  (tempos - tempos.mean(axis=0)) / 60", centrar_e_dividir),
    ("E  x = tempos - tempos.mean(axis=0); x /= 60", centrar_e_dividir_no_lugar),
]
print(f"{'conta':<46}{'pico':>9}{'resultado':>11}")
for nome, f in contas:
    r, p = medir.pico(f)
    tamanho = medir.mb(r.nbytes) if isinstance(r, np.ndarray) and r.ndim else "1 número"
    print(f"{nome:<46}{medir.mb(p):>9}{tamanho:>11}")
