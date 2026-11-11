"""Quantos minutos cada atleta ficou acima ou abaixo da mediana de cada etapa.

    python3 acima_da_mediana.py                 # 2024, peitos 102, 103 e 104
    python3 acima_da_mediana.py --edicao 2025 --peito 102 361
"""
import argparse

import numpy as np

import parciais


def main(argumentos=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--edicao", type=int, default=2024, choices=(2024, 2025))
    p.add_argument("--peito", type=int, nargs="+", default=[102, 103, 104])
    args = p.parse_args(argumentos)

    r = parciais.carregar()
    linhas = ((r["edicao"] == args.edicao) & (r["status"] == "concluiu")
              & ~np.isnan(r["tempos"]).any(axis=1))
    tempos = r["tempos"][linhas]
    peito = r["peito"][linhas]

    mediana = np.median(tempos, axis=0)
    diferenca = (tempos - mediana) / 60

    print(f"Concluíram {args.edicao} com as 5 parciais: {len(tempos)} atletas")
    print("tempos:", tempos.shape, "| mediana:", mediana.shape, "| diferenca:", diferenca.shape)
    print("\nMediana de cada etapa:")
    print(" | ".join(f"{e} {parciais.hms(m)}" for e, m in zip(parciais.ETAPAS, mediana)))
    print("\nMinutos acima (+) ou abaixo (-) da mediana:")
    print("peito " + "".join(f"{e:>10}" for e in parciais.ETAPAS))
    for n in args.peito:
        achou = np.flatnonzero(peito == n)
        if achou.size == 0:
            print(f"{n:>5}   não concluiu {args.edicao} com as 5 parciais")
            continue
        print(f"{n:>5} " + "".join(f"{d:>+10.1f}" for d in diferenca[achou[0]]))


if __name__ == "__main__":
    main()
