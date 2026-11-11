"""Simulação da promoção de julho, sem mexer no catálogo de hoje.

O preço vira número uma vez, na leitura. A simulação monta um catálogo novo.
"""
import csv
from pathlib import Path

PRODUTOS = Path(__file__).resolve().parent.parent / "dados" / "loja" / "produtos.csv"


def ler_catalogo(caminho):
    """Catálogo por id_produto, com o preço em float."""
    catalogo = {}
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            catalogo[linha["id_produto"]] = {
                "nome": linha["nome"],
                "categoria": linha["categoria"],
                "preco": float(linha["preco"]),
            }
    return catalogo


def simular_desconto(catalogo, categoria, desconto):
    """Retorna um catálogo novo com o desconto na categoria. O catálogo recebido não muda."""
    simulado = {}
    for id_produto, produto in catalogo.items():
        novo = dict(produto)
        if novo["categoria"] == categoria:
            novo["preco"] = round(novo["preco"] * (1 - desconto), 2)
        simulado[id_produto] = novo
    return simulado


def main():
    catalogo = ler_catalogo(PRODUTOS)
    promocao = simular_desconto(catalogo, "Eletro", 0.10)

    print(f"{'Eletro':<16}{'hoje':>9}{'promoção':>10}")
    for id_produto, produto in catalogo.items():
        if produto["categoria"] == "Eletro":
            print(f"{produto['nome']:<16}{produto['preco']:>9.2f}{promocao[id_produto]['preco']:>10.2f}")

    print()
    print("Os 3 mais baratos da loja hoje, para a vitrine:")
    baratos = sorted(catalogo.values(), key=lambda produto: produto["preco"])[:3]
    for produto in baratos:
        print(f"  {produto['nome']}: {produto['preco']:.2f}")


if __name__ == "__main__":
    main()
