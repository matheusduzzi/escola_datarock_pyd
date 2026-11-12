"""As versões do quadro do ranking e a regra que diz se duas versões dão o mesmo quadro.

O quadro é o da aula 18: para cada etapa e para o total, média, mediana, desvio (ddof=0),
mínimo e máximo. Cada versão recebe o array de tempos guardado do jeito dela e retorna
um array (6, 5): uma linha por etapa mais o total, uma coluna por estatística.

    import versoes
    for v in versoes.VERSOES:
        guardado = v["guardar"](tempos)
        quadro = v["conta"](guardado)
"""
import numpy as np

# A regra de equivalência, escrita antes de medir qualquer tempo.
# 1 milésimo de segundo: a tolerância do boletim na aula 18.
RTOL, ATOL = 0.0, 0.001


def quadro(tempos):
    """A versão de hoje: a conta do quadro.py da aula 18, coluna por coluna."""
    total = tempos.sum(axis=1)
    linhas = []
    for col in list(tempos.T) + [total]:
        linhas.append((col.mean(), np.median(col), col.std(), col.min(), col.max()))
    return np.array(linhas)


def quadro_ordenado(tempos):
    """Proposta da IA: uma ordenação por coluna dá a mediana, o mínimo e o máximo de uma vez."""
    total = tempos.sum(axis=1)
    linhas = []
    for col in list(tempos.T) + [total]:
        ordem = np.sort(col)
        n = len(ordem)
        mediana = ordem[n // 2] if n % 2 else (ordem[n // 2 - 1] + ordem[n // 2]) / 2
        linhas.append((col.mean(), mediana, col.std(), ordem[0], ordem[-1]))
    return np.array(linhas)


def quadro_eixo(tempos):
    """Proposta da IA: cada estatística numa chamada só, com axis=0, sem o loop das colunas."""
    tudo = np.column_stack([tempos, tempos.sum(axis=1)])
    return np.column_stack([tudo.mean(axis=0), np.median(tudo, axis=0), tudo.std(axis=0),
                            tudo.min(axis=0), tudo.max(axis=0)])


def quadro_soma64(tempos):
    """A conta do quadro com soma, média e desvio feitos em float64, qualquer que seja o tipo guardado."""
    total = tempos.sum(axis=1, dtype=np.float64)
    linhas = []
    for col in list(tempos.T) + [total]:
        linhas.append((col.mean(dtype=np.float64), np.median(col), col.std(dtype=np.float64),
                       col.min(), col.max()))
    return np.array(linhas, dtype=np.float64)


def em_float64(tempos):
    return tempos


def em_float32(tempos):
    return tempos.astype(np.float32)


VERSOES = [
    {"nome": "hoje", "guardar": em_float64, "conta": quadro},
    {"nome": "float32", "guardar": em_float32, "conta": quadro},
    {"nome": "uma ordenação", "guardar": em_float64, "conta": quadro_ordenado},
    {"nome": "axis=0", "guardar": em_float64, "conta": quadro_eixo},
    {"nome": "float32 + soma64", "guardar": em_float32, "conta": quadro_soma64},
]


def conferencia(q):
    """Soma das médias das etapas menos a média do total: a nota do boletim da aula 18."""
    q = q.astype(np.float64)
    return q[:5, 0].sum() - q[5, 0]


def equivale(q, referencia):
    """O mesmo quadro: mesma forma, cada número a até ATOL segundo, e a nota do boletim continua valendo."""
    if q.shape != referencia.shape:
        return False
    q = q.astype(np.float64)
    perto = np.isclose(q, referencia, rtol=RTOL, atol=ATOL).all()
    return bool(perto and abs(conferencia(q)) <= ATOL)
