"""Pedidos de avaliação de junho: um por cliente e produto entregue, sem repetição.

Uso, de dentro da pasta da aula:
    python3 avaliacoes.py
    python3 avaliacoes.py --arquivo pedidos-junho.json --saida saida/avaliacoes-junho.csv

O export repete pedidos. Este programa tira as repetições em duas etapas, com a regra escrita:
1. Pedido: o id do pedido com o atualizado_em é uma versão. A mesma versão duas vezes é cópia
   e sai. Entre versões diferentes do mesmo pedido, vale a de atualizado_em mais recente.
2. Avaliação: a chave é a tupla (id do cliente, id do produto). Quem recebeu o mesmo produto
   em dois pedidos ganha um pedido de avaliação só.
No fim, as contas precisam fechar; se não fecharem, o programa para antes de gravar.
"""
import argparse
import csv
import json
from pathlib import Path


def ler(caminho):
    """Lista de registros do export, como vieram."""
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def tirar_copias(registros):
    """Tira a versão repetida: mesmo pedido com o mesmo atualizado_em. Retorna (versões, cópias).

    Cópia é o registro igual, campo por campo. A mesma versão com conteúdo diferente não é cópia:
    o programa para e mostra o pedido, porque não dá para saber qual dos dois vale.
    """
    vistas = {}
    for r in registros:
        versao = (r["id_pedido"], r["atualizado_em"])
        if versao in vistas and vistas[versao] != r:
            raise SystemExit(f"Pedido {r['id_pedido']} tem dois registros diferentes em {r['atualizado_em']}")
        vistas.setdefault(versao, r)
    versoes = list(vistas.values())
    return versoes, len(registros) - len(versoes)


def versao_final(versoes):
    """Um registro por pedido: o de atualizado_em mais recente, venha na ordem que vier."""
    final = {}
    for r in versoes:
        atual = final.get(r["id_pedido"])
        if atual is None or r["atualizado_em"] > atual["atualizado_em"]:
            final[r["id_pedido"]] = r
    return final


def pares_entregues(pedidos):
    """Conjunto de (id_cliente, id_produto) dos pedidos que ficaram entregues."""
    return {
        (p["cliente"]["id_cliente"], p["produto"]["id_produto"])
        for p in pedidos.values()
        if p["status"] == "entregue"
    }


def por_cidade(pedidos, pares):
    """{cidade: {id_cliente: [nomes dos produtos]}} só com os pares que ganham avaliação."""
    nome = {p["produto"]["id_produto"]: p["produto"]["nome"] for p in pedidos.values()}
    cidade = {p["cliente"]["id_cliente"]: p["cliente"]["cidade"] for p in pedidos.values()}
    resultado = {}
    for id_cliente, id_produto in sorted(pares):
        clientes = resultado.setdefault(cidade[id_cliente], {})
        clientes.setdefault(id_cliente, []).append(nome[id_produto])
    return resultado


def main(argumentos=None):
    parser = argparse.ArgumentParser(description="Pedidos de avaliação, um por cliente e produto.")
    parser.add_argument("--arquivo", default="pedidos-junho.json")
    parser.add_argument("--saida", default="saida/avaliacoes-junho.csv")
    args = parser.parse_args(argumentos)

    registros = ler(args.arquivo)
    versoes, copias = tirar_copias(registros)
    pedidos = versao_final(versoes)
    antigas = len(versoes) - len(pedidos)
    entregues = sum(1 for p in pedidos.values() if p["status"] == "entregue")
    pares = pares_entregues(pedidos)
    cidades = por_cidade(pedidos, pares)

    print("Registros no export:", len(registros))
    print("  cópias da mesma versão:", copias)
    print("  versões antigas de um pedido:", antigas)
    print("Pedidos diferentes:", len(pedidos))
    print("  entregues na versão final:", entregues)
    print("  cancelados na versão final:", len(pedidos) - entregues)
    print("Pedidos de avaliação (cliente e produto):", len(pares))
    print("  entregues que repetem cliente e produto:", entregues - len(pares))
    print()
    print(f"{'Cidade':<16}{'clientes':>9}{'avaliações':>12}")
    for nome_cidade, clientes in sorted(cidades.items(), key=lambda item: (-len(item[1]), item[0])):
        total = sum(len(produtos) for produtos in clientes.values())
        print(f"{nome_cidade:<16}{len(clientes):>9}{total:>12}")

    contas = {
        "registros = pedidos + cópias + versões antigas": len(registros) == len(pedidos) + copias + antigas,
        "avaliações por cidade somam o total": sum(
            len(produtos) for clientes in cidades.values() for produtos in clientes.values()) == len(pares),
    }
    falhou = [nome for nome, ok in contas.items() if not ok]
    if falhou:
        raise SystemExit("As contas não fecham: " + "; ".join(falhou))

    saida = Path(args.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    with open(saida, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["cidade", "id_cliente", "produto"])
        for nome_cidade in sorted(cidades):
            for id_cliente, produtos in sorted(cidades[nome_cidade].items()):
                for produto in sorted(produtos):
                    escritor.writerow([nome_cidade, id_cliente, produto])
    print()
    print("Lista gravada em", saida)


if __name__ == "__main__":
    main()
