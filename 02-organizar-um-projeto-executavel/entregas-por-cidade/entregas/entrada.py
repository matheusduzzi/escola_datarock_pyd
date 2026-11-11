"""Entrada: ler as tabelas da Loja Exemplo e parar cedo se faltar arquivo ou coluna."""
import pandas as pd

COLUNAS = {
    "pedidos.csv": ["id_pedido", "id_cliente", "data_pedido", "valor", "status"],
    "clientes.csv": ["id_cliente", "cidade"],
}


def ler_tabela(pasta, nome):
    arquivo = pasta / nome
    if not arquivo.is_file():
        raise FileNotFoundError(f"não achei {nome} em {pasta}. Veja LOJA_DADOS no .env.")
    tabela = pd.read_csv(arquivo)
    faltam = [c for c in COLUNAS[nome] if c not in tabela.columns]
    if faltam:
        raise ValueError(f"{nome} está sem as colunas {faltam}.")
    return tabela


def ler_base(pasta):
    return ler_tabela(pasta, "pedidos.csv"), ler_tabela(pasta, "clientes.csv")
