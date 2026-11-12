"""Somas de decimais que não dão o número que a gente escreve. Seção 7 da aula."""
import math

import numpy as np

print(f"0.1 + 0.2 = {0.1 + 0.2!r}")
print(f"0.1 + 0.2 == 0.3: {0.1 + 0.2 == 0.3}")
print()
print("Os km de quem concluiu 2025 (edicoes.csv: 1.9, 180 e 42.2)")
print(f"1.9 + 180.0 + 42.2 = {1.9 + 180.0 + 42.2!r}")
print(f"42.2 + 180.0 + 1.9 = {42.2 + 180.0 + 1.9!r}")
print()
km = [224.1] * 393
soma = 0.0
for x in km:
    soma += x
print("Os km dos 393 que concluíram 2025")
print(f"loop, um por um: {soma!r}")
print(f"np.sum:          {float(np.sum(km))!r}")
print(f"math.fsum:       {math.fsum(km)!r}")
print(f"224.1 * 393:     {224.1 * 393!r}")
