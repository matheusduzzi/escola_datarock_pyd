"""Simulação da promoção de julho: o preço de hoje e o preço com desconto, lado a lado."""
import csv
from pathlib import Path

PRODUTOS = Path(__file__).resolve().parent.parent / "dados" / "loja" / "produtos.csv"


def ler_catalogo(caminho):
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return {linha["id_produto"]: linha for linha in csv.DictReader(arquivo)}


def simular_desconto(catalogo, categoria, desconto):
    simulado = catalogo
    for produto in simulado.values():
        if produto["categoria"] == categoria:
            produto["preco"] = round(float(produto["preco"]) * (1 - desconto), 2)
    return simulado


def main():
    catalogo = ler_catalogo(PRODUTOS)
    promocao = simular_desconto(catalogo, "Eletro", 0.10)

    print(f"{'Eletro':<16}{'hoje':>9}{'promoção':>10}")
    for id_produto, produto in catalogo.items():
        if produto["categoria"] == "Eletro":
            hoje = float(produto["preco"])
            com_desconto = float(promocao[id_produto]["preco"])
            print(f"{produto['nome']:<16}{hoje:>9.2f}{com_desconto:>10.2f}")

    print()
    print("Os 3 mais baratos da loja hoje, para a vitrine:")
    baratos = sorted(catalogo.values(), key=lambda produto: produto["preco"])[:3]
    for produto in baratos:
        print(f"  {produto['nome']}: {produto['preco']}")


if __name__ == "__main__":
    main()
