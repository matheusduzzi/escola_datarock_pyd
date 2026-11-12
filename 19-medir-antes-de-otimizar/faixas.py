"""As versões da contagem por faixa de hora, para o exercício.

A Lívia quer saber quantos atletas do ranking terminaram em cada faixa de hora do tempo total:
de 8h a 8h59min59s, de 9h a 9h59min59s, e assim até a faixa das 16h. Cada versão recebe o array
de tempos (n, 5) em segundos e retorna 9 contagens, da faixa das 8h à das 16h.

    import faixas
    for nome, conta in faixas.VERSOES:
        print(nome, conta(tempos))
"""
import numpy as np

HORAS = np.arange(8, 17)


def faixas_hoje(tempos):
    """A versão de hoje: uma máscara por faixa."""
    total = tempos.sum(axis=1)
    contagem = []
    for h in HORAS:
        contagem.append(((total >= h * 3600) & (total < (h + 1) * 3600)).sum())
    return np.array(contagem)


def faixas_arredondada(tempos):
    """Proposta da IA: a hora de cada atleta com np.round, e o np.bincount conta todas de uma vez."""
    horas = np.round(tempos.sum(axis=1) / 3600).astype(np.int64)
    return np.bincount(horas, minlength=17)[8:17]


def faixas_bincount(tempos):
    """Proposta da IA: a hora cheia de cada atleta com a divisão inteira, e o np.bincount conta."""
    horas = (tempos.sum(axis=1) // 3600).astype(np.int64)
    return np.bincount(horas, minlength=17)[8:17]


def faixas_histogram(tempos):
    """Proposta da IA: o np.histogram com as bordas das faixas em segundos."""
    contagem, _ = np.histogram(tempos.sum(axis=1), bins=np.arange(8, 18) * 3600)
    return contagem


VERSOES = [
    ("hoje", faixas_hoje),
    ("arredondada", faixas_arredondada),
    ("bincount", faixas_bincount),
    ("histogram", faixas_histogram),
]
