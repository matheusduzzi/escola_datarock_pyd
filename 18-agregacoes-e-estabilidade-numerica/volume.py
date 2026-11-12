"""Monta tempos de quantos atletas você quiser, a partir dos tempos reais de 2024.

    import volume
    tempos = volume.gerar(1_000_000)   # array (1000000, 5) em segundos

Cada linha é a linha de um atleta que concluiu 2024 com as cinco parciais, sorteada com
repetição. O sorteio é sempre o mesmo: rodar duas vezes dá o mesmo array.
Serve para ver o que muda quando o volume cresce. Não é uma prova de verdade.
"""
import numpy as np

import parciais


def base(edicao=2024):
    r = parciais.carregar()
    linhas = (r["edicao"] == edicao) & (r["status"] == "concluiu") & ~np.isnan(r["tempos"]).any(axis=1)
    return r["tempos"][linhas]


def gerar(n, edicao=2024):
    tempos = base(edicao)
    sorteio = np.random.default_rng(17).integers(0, len(tempos), size=n)
    return tempos[sorteio]
