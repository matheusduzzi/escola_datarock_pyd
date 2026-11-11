"""A mesma conta com loop e com array, em volumes diferentes.

A conta: o tempo total de cada atleta, em horas, somando as cinco parciais.
    python3 comparar.py            # 5, 100, 10 mil e 1 milhão de atletas
    python3 comparar.py --n 5      # um volume só
"""
import argparse

import numpy as np

import cronometro
import volume


def com_loop(lista):
    total = []
    for linha in lista:
        soma = 0.0
        for parcial in linha:
            soma += parcial
        total.append(soma / 3600)
    return total


def com_array(tempos):
    return tempos.sum(axis=1) / 3600


def comparar(n):
    tempos = volume.gerar(n)
    lista = tempos.tolist()
    iguais = np.array_equal(np.array(com_loop(lista)), com_array(tempos))
    loop = cronometro.medir(lambda: com_loop(lista))
    array = cronometro.medir(lambda: com_array(tempos))
    convertendo = cronometro.medir(lambda: com_array(np.array(lista)))
    return {"n": n, "iguais": iguais, "loop": loop, "array": array,
            "convertendo": convertendo, "mb": tempos.nbytes / 1e6}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int)
    args = p.parse_args()
    volumes = [args.n] if args.n else [5, 100, 10_000, 1_000_000]
    print(f"{'atletas':>9}  {'loop':>9}  {'array':>9}  {'array + conversão':>17}  {'loop / array':>12}  {'tempos':>9}  iguais")
    for n in volumes:
        c = comparar(n)
        vezes = c["loop"] / c["array"]
        print(f"{n:>9,}".replace(",", ".") + f"  {cronometro.texto(c['loop']):>9}  {cronometro.texto(c['array']):>9}"
              f"  {cronometro.texto(c['convertendo']):>17}  {vezes:>11.1f}x  {c['mb']:>6.2f} MB  {c['iguais']}")


if __name__ == "__main__":
    main()
