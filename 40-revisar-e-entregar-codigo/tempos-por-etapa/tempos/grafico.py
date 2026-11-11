"""Gráfico: a mediana de cada etapa, uma barra por categoria."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def gravar(tabela, arquivo):
    etapas = ["natacao", "ciclismo", "corrida"]
    minutos = tabela[etapas] / 60
    eixo = minutos.plot.bar(figsize=(8, 4.5), rot=0)
    eixo.set_xlabel("categoria")
    eixo.set_ylabel("mediana, em minutos")
    eixo.set_title("Mediana de cada etapa, de quem terminou")
    eixo.legend(["natação", "ciclismo", "corrida"])
    eixo.figure.tight_layout()
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    eixo.figure.savefig(arquivo, dpi=100, metadata={"Software": None})
    plt.close(eixo.figure)
    return arquivo
