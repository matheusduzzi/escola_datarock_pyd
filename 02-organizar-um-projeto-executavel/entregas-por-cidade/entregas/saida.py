"""Saída: mostrar o resumo na tela e gravar o CSV, com o período no nome do arquivo."""


def nome_do_arquivo(inicio, fim):
    return f"entregas-por-cidade_{inicio}_a_{fim}.csv"


def mostrar(resumo, inicio, fim):
    print(f"Entregas por cidade de {inicio} a {fim}, em R$")
    print(resumo.to_string())
    print("Total:", round(resumo["faturamento"].sum(), 2))


def gravar(resumo, pasta, inicio, fim):
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / nome_do_arquivo(inicio, fim)
    resumo.to_csv(arquivo)
    return arquivo
