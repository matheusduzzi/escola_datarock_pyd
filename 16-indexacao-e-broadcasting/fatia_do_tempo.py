"""Que fatia do tempo de cada atleta foi cada etapa (a linha soma 1).

    python3 fatia_do_tempo.py                     # todos que concluíram 2024 com as 5 parciais
    python3 fatia_do_tempo.py --amostra 5         # só as 5 primeiras linhas
    python3 fatia_do_tempo.py --errado            # a primeira versão, sem o np.newaxis
    python3 fatia_do_tempo.py --errado --amostra 5
"""
import argparse

import numpy as np

import parciais


def main(argumentos=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--amostra", type=int, help="usar só as N primeiras linhas")
    p.add_argument("--errado", action="store_true", help="dividir pela soma sem o np.newaxis")
    args = p.parse_args(argumentos)

    r = parciais.carregar()
    linhas = ((r["edicao"] == 2024) & (r["status"] == "concluiu")
              & ~np.isnan(r["tempos"]).any(axis=1))
    tempos = r["tempos"][linhas]
    peito = r["peito"][linhas]
    if args.amostra:
        tempos, peito = tempos[:args.amostra], peito[:args.amostra]

    total = tempos.sum(axis=1)
    print("tempos:", tempos.shape, "| total:", total.shape)
    if args.errado:
        fatia = tempos / total
    else:
        fatia = tempos / total[:, np.newaxis]
    print("fatia:", fatia.shape)

    print("\npeito " + "".join(f"{e:>10}" for e in parciais.ETAPAS) + "      soma")
    for n, f in list(zip(peito, fatia))[:5]:
        print(f"{n:>5} " + "".join(f"{x:>10.3f}" for x in f) + f"{f.sum():>10.3f}")
    print("\nLinhas que não somam 1:", int((~np.isclose(fatia.sum(axis=1), 1)).sum()), "de", len(fatia))


if __name__ == "__main__":
    main()
