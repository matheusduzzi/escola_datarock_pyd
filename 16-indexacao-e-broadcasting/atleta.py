"""Mostra as parciais de um atleta como estão no arquivo e em segundos, para fazer a conta à mão.

    python3 atleta.py --edicao 2024 --peito 102
"""
import argparse

import numpy as np

import parciais


def main(argumentos=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--edicao", type=int, required=True, choices=(2024, 2025))
    p.add_argument("--peito", type=int, required=True)
    args = p.parse_args(argumentos)

    r = parciais.carregar()
    achou = np.flatnonzero((r["edicao"] == args.edicao) & (r["peito"] == args.peito))
    if achou.size == 0:
        p.error(f"peito {args.peito} não aparece em {args.edicao}")
    i = achou[0]
    print(f"Peito {args.peito} em {args.edicao}: {r['status'][i]}")
    print("etapa        no arquivo   segundos")
    for etapa, texto, seg in zip(parciais.ETAPAS, r["texto"][i], r["tempos"][i]):
        print(f"{etapa:<12} {texto or 'vazio':>10} {seg:>10.0f}")
    soma = r["tempos"][i].sum()
    if np.isnan(soma):
        print("soma         não dá para somar: tem parcial vazia")
    else:
        print(f"{'soma':<12} {parciais.hms(soma):>10} {soma:>10.0f}")


if __name__ == "__main__":
    main()
