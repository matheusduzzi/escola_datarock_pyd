"""Antes do tempo, o resultado: cada versão dá o mesmo quadro que a de hoje?

    python3 equivalencia.py                  # 1 milhão de linhas
    python3 equivalencia.py --linhas 10000

Para cada versão: o tipo do resultado, a maior diferença para o quadro de hoje e onde ela está,
se os números são iguais com ==, se a versão passa na regra do versoes.py e a nota do boletim
(soma das médias das etapas menos a média do total).
"""
import argparse

import numpy as np

import versoes
import volume

LINHAS = ("natação", "t1", "ciclismo", "t2", "corrida", "total")
COLUNAS = ("média", "mediana", "desvio", "mínimo", "máximo")

ap = argparse.ArgumentParser()
ap.add_argument("--linhas", type=int, default=1_000_000)
n = ap.parse_args().linhas

tempos = volume.gerar(n)
hoje = versoes.quadro(tempos)
print(f"{n} linhas | regra: cada número a até {versoes.ATOL} s do quadro de hoje, "
      f"e a nota do boletim a até {versoes.ATOL} s")
print()
print(f"{'versão':<18}{'tipo':<9}{'maior diferença':>17}  {'onde':<20}{'==':<7}{'equivale':<10}nota do boletim")
for v in versoes.VERSOES:
    q = v["conta"](v["guardar"](tempos))
    dif = np.abs(q.astype(np.float64) - hoje)
    i, j = np.unravel_index(dif.argmax(), dif.shape)
    onde = f"{COLUNAS[j]} do {LINHAS[i]}" if dif.max() > 0 else "-"
    print(f"{v['nome']:<18}{str(q.dtype):<9}{dif.max():>15.3e} s  {onde:<20}"
          f"{str(np.array_equal(q, hoje)):<7}{str(versoes.equivale(q, hoje)):<10}{versoes.conferencia(q):.1e} s")
