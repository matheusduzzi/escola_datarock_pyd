"""O pico do programa inteiro: montar o array, guardar e fazer o quadro, com 1 milhão de linhas.

    python3 programa.py

Três caminhos com o mesmo quadro no fim:
  hoje: monta em float64 e faz o quadro de hoje;
  converte depois: monta em float64, converte para float32, joga fora o float64 e faz o quadro
  com soma em float64;
  já em float32: monta o array direto em float32 (o sorteio do volume.py sobre os tempos de 2024
  já convertidos) e faz o mesmo quadro.
"""
import numpy as np

import medir
import versoes
import volume

N = 1_000_000


def gerar32(n):
    """O mesmo sorteio do volume.gerar, mas sobre a base já em float32."""
    base = volume.base().astype(np.float32)
    sorteio = np.random.default_rng(17).integers(0, len(base), size=n)
    return base[sorteio]


def hoje():
    tempos = volume.gerar(N)
    return versoes.quadro(tempos)


def converte_depois():
    tempos = volume.gerar(N)
    tempos32 = tempos.astype(np.float32)
    del tempos
    return versoes.quadro_soma64(tempos32)


def ja_em_float32():
    return versoes.quadro_soma64(gerar32(N))


print(f"gerar32 dá o mesmo array que volume.gerar convertido: "
      f"{np.array_equal(gerar32(N), volume.gerar(N).astype(np.float32))}")
referencia = None
print()
print(f"{'caminho':<18}{'pico do programa':>18}  mesmo quadro")
for nome, f in (("hoje", hoje), ("converte depois", converte_depois), ("já em float32", ja_em_float32)):
    q, p = medir.pico(f)
    referencia = q if referencia is None else referencia
    print(f"{nome:<18}{medir.mb(p):>18}  {np.array_equal(q, referencia)}")
