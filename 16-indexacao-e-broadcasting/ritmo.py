"""Velocidade mediana em km/h na natação, no ciclismo e na corrida, por edição.

    python3 ritmo.py                # cada atleta com a distância da edição dele
    python3 ritmo.py --sem-indexar  # todo mundo com a distância de 2024
"""
import argparse

import numpy as np

import parciais

# edicoes.csv: natacao_km, ciclismo_km, corrida_km. Linha 0 é 2024, linha 1 é 2025.
DISTANCIAS = np.array([[3.8, 180.0, 42.2],
                       [1.9, 180.0, 42.2]])


def main(argumentos=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sem-indexar", action="store_true", help="usar a distância de 2024 para todos")
    args = p.parse_args(argumentos)

    r = parciais.carregar()
    linhas = (r["status"] == "concluiu") & ~np.isnan(r["tempos"]).any(axis=1)
    horas = r["tempos"][linhas][:, [0, 2, 4]] / 3600
    edicao = r["edicao"][linhas]

    if args.sem_indexar:
        km = DISTANCIAS[0]
    else:
        km = DISTANCIAS[edicao - 2024]
    velocidade = km / horas
    print("horas:", horas.shape, "| km:", km.shape, "| velocidade:", velocidade.shape)

    print("\nedição   natação  ciclismo   corrida   (km/h, mediana)")
    for ano in (2024, 2025):
        v = np.median(velocidade[edicao == ano], axis=0)
        print(f"{ano}  " + "".join(f"{x:>10.2f}" for x in v))


if __name__ == "__main__":
    main()
