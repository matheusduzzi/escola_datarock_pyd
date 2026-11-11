"""Achar o primeiro atleta com parcial vazia em 1 milhão de linhas, com loop e com array.

    python3 primeiro_vazio.py --onde inicio   # a parcial vazia está na primeira linha
    python3 primeiro_vazio.py --onde fim      # está na última linha
"""
import argparse
import math

import numpy as np

import cronometro
import volume


def com_loop(lista):
    for i, linha in enumerate(lista):
        for parcial in linha:
            if math.isnan(parcial):
                return i
    return None


def com_array(tempos):
    vazia = np.isnan(tempos).any(axis=1)
    return int(vazia.argmax()) if vazia.any() else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--onde", choices=["inicio", "fim"], required=True)
    p.add_argument("--n", type=int, default=1_000_000)
    args = p.parse_args()
    tempos = volume.gerar(args.n)
    linha = 0 if args.onde == "inicio" else args.n - 1
    tempos[linha, 1] = np.nan
    lista = tempos.tolist()
    achou_loop, achou_array = com_loop(lista), com_array(tempos)
    print(f"atletas: {args.n:,}".replace(",", ".") + f" | parcial vazia na linha {linha:,}".replace(",", "."))
    print(f"loop achou a linha {achou_loop:,}".replace(",", ".") + f" | array achou a linha {achou_array:,}".replace(",", "."))
    print(f"loop:  {cronometro.texto(cronometro.medir(lambda: com_loop(lista)))}")
    print(f"array: {cronometro.texto(cronometro.medir(lambda: com_array(tempos)))}")


if __name__ == "__main__":
    main()
