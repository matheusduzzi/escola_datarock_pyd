"""Onde vai o tempo do quadro de hoje, com 1 milhão de linhas.

Mede cada pedaço da conta do versoes.quadro: a soma das parciais e cada estatística,
somada nas seis colunas (cinco etapas e o total).
    python3 etapas.py
"""
import numpy as np

import medir
import versoes
import volume

tempos = volume.gerar(1_000_000)
total = tempos.sum(axis=1)
colunas = list(tempos.T) + [total]

pedacos = [
    ("soma das parciais", lambda: tempos.sum(axis=1)),
    ("6 médias", lambda: [c.mean() for c in colunas]),
    ("6 medianas", lambda: [np.median(c) for c in colunas]),
    ("6 desvios", lambda: [c.std() for c in colunas]),
    ("6 mínimos e 6 máximos", lambda: [(c.min(), c.max()) for c in colunas]),
]
inteiro, _ = medir.tempo(lambda: versoes.quadro(tempos))
print(f"quadro de hoje, 1000000 linhas: {medir.texto(inteiro)}")
print()
print(f"{'pedaço':<24}{'tempo':>10}{'do quadro':>11}")
for nome, f in pedacos:
    t, _ = medir.tempo(f)
    print(f"{nome:<24}{medir.texto(t):>10}{t / inteiro:>10.0%}")
print()
o, _ = medir.tempo(lambda: np.sort(total))
m, _ = medir.tempo(lambda: np.median(total))
print(f"uma coluna: np.sort {medir.texto(o)} | np.median {medir.texto(m)}")
