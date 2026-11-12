"""A soma das médias das etapas contra a média do tempo oficial de 2025. Seções 4 e 6 da aula.

    python3 conferir.py --nanmean    # os 393 que concluíram, np.nanmean em cada etapa
    python3 conferir.py              # os 387 que concluíram com as 5 parciais, as mesmas linhas nas etapas
    python3 conferir.py --sem 109    # os 387, mas sem o atleta de peito 109 nas etapas
"""
import sys

import numpy as np

import parciais

r = parciais.carregar()
concluiu = (r["edicao"] == 2025) & (r["status"] == "concluiu")
if "--nanmean" in sys.argv:
    linhas = concluiu
    medias = np.nanmean(r["tempos"][linhas], axis=0)
    print(f"{linhas.sum()} que concluíram, np.nanmean em cada etapa")
    print("linhas usadas por etapa: " + " ".join(str(n) for n in (~np.isnan(r["tempos"][linhas])).sum(axis=0)))
else:
    linhas = concluiu & ~np.isnan(r["tempos"]).any(axis=1)
    etapas = linhas.copy()
    if "--sem" in sys.argv:
        peito = int(sys.argv[sys.argv.index("--sem") + 1])
        etapas &= r["peito"] != peito
        print(f"Sem o peito {peito} nas etapas: {etapas.sum()} linhas; a média oficial fica com as {linhas.sum()}")
    else:
        print(f"{linhas.sum()} que concluíram com as 5 parciais, as mesmas linhas em todas as etapas")
    medias = r["tempos"][etapas].mean(axis=0)
oficial = r["oficial"][linhas].mean()
soma = medias.sum()

print(f"soma das médias das etapas: {float(soma)!r}")
print(f"média do tempo oficial:     {float(oficial)!r}")
print(f"diferença:                  {float(soma - oficial)!r} s")
print(f"iguais com ==:              {soma == oficial}")
print(f"np.isclose padrão:          {np.isclose(soma, oficial)}"
      f"   (rtol=1e-05, atol=1e-08: aceita até {1e-08 + 1e-05 * abs(oficial):.3f} s aqui)")
print(f"np.isclose(rtol=0, atol=0.001): {np.isclose(soma, oficial, rtol=0, atol=0.001)}")
