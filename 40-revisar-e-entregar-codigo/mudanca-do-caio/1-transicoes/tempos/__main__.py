"""O comando do projeto. Rode da pasta do projeto: python3 -m tempos"""
import sys
from pathlib import Path

from tempos import calculo, grafico, leitura

SAIDA = Path(__file__).resolve().parent.parent / "saida"


def main():
    try:
        resultados = leitura.ler_resultados()
        categorias = leitura.ler_categorias()
    except (FileNotFoundError, ValueError) as erro:
        sys.exit(f"erro: {erro}")
    tabela = calculo.por_categoria(resultados, categorias)
    print("Mediana de quem terminou, por categoria")
    mostrar = tabela.copy()
    for coluna in ["natacao", "ciclismo", "corrida", "transicoes", "total"]:
        mostrar[coluna] = mostrar[coluna].map(calculo.relogio)
    print(mostrar.to_string())
    print(f"Terminaram: {int(tabela['atletas'].sum())} de {len(resultados)} inscritos")
    SAIDA.mkdir(exist_ok=True)
    tabela.to_csv(SAIDA / "tempos-por-categoria.csv")
    grafico.gravar(tabela, SAIDA / "medianas-por-categoria.png")
    print("Tabela gravada em saida/tempos-por-categoria.csv")
    print("Gráfico gravado em saida/medianas-por-categoria.png")


if __name__ == "__main__":
    main()
