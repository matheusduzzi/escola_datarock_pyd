"""Separa a exportação nova da loja online em duas tabelas ligadas pelo id_pedido.

    python3 separar_pedidos.py
    python3 separar_pedidos.py --arquivo outro-arquivo.json

saida/pedidos.csv: uma linha por pedido, com o cliente, o cupom e a entrega abertos em colunas.
saida/itens.csv: uma linha por produto do carrinho, com o id_pedido e a posição do item.

Antes de gravar, olha as regras do combinado com a plataforma. Se alguma falha, mostra todos os
problemas, termina com o código 1 e não grava nada.
"""
import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
ARQUIVO = AQUI / "pedidos-online-novembro-semana-1.json"
SAIDA = AQUI / "saida"
STATUS = {"pago", "enviado", "entregue", "cancelado"}

logging.basicConfig(format="%(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger("separar")


def separar(pedidos):
    """Retorna (linhas de pedido, linhas de item, problemas). Não grava nada."""
    linhas_pedido, linhas_item, problemas = [], [], []
    vistos = set()
    for registro, pedido in enumerate(pedidos, start=1):
        antes = len(problemas)
        id_pedido = pedido.get("id_pedido")
        onde = f"registro {registro}" + (f" (pedido {id_pedido})" if id_pedido else "")
        if not id_pedido:
            problemas.append(f"{onde}: sem id_pedido")
            continue
        if id_pedido in vistos:
            problemas.append(f"{onde}: id_pedido repetido")
            continue
        vistos.add(id_pedido)

        status = pedido.get("status")
        if status not in STATUS:
            problemas.append(f"{onde}: status {status!r} fora de {sorted(STATUS)}")

        itens = pedido.get("itens")
        if not isinstance(itens, list):
            problemas.append(f"{onde}: sem a lista itens")
            itens = []
        elif not itens and status != "cancelado":
            problemas.append(f"{onde}: lista de itens vazia num pedido {status}")

        subtotal = 0.0
        for item_n, item in enumerate(itens, start=1):
            faltam = [c for c in ("id_produto", "quantidade", "preco_unitario") if item.get(c) is None]
            if faltam:
                problemas.append(f"{onde}, item {item_n}: sem {', '.join(faltam)}")
                continue
            valor_item = round(item["quantidade"] * item["preco_unitario"], 2)
            subtotal += valor_item
            linhas_item.append({"id_pedido": id_pedido, "item": item_n, "id_produto": item["id_produto"],
                                "quantidade": item["quantidade"], "preco_unitario": item["preco_unitario"],
                                "valor_item": valor_item})

        cupom = pedido.get("cupom")  # sem a chave ou com null: o pedido não usou cupom
        if cupom is not None and (not cupom.get("codigo") or cupom.get("desconto") is None):
            problemas.append(f"{onde}: cupom sem codigo ou sem desconto")
            cupom = None
        cupom = cupom or {}

        entrega = pedido.get("entrega") or {}
        tipo = entrega.get("tipo")
        frete = entrega.get("frete")
        if tipo == "correio" and frete is None:
            problemas.append(f"{onde}: entrega por correio sem frete")
        elif tipo == "retirada" and frete is not None:
            problemas.append(f"{onde}: retirada na loja com frete")
        elif tipo not in ("correio", "retirada"):
            problemas.append(f"{onde}: tipo de entrega {tipo!r}")

        cliente = pedido.get("cliente") or {}
        if cliente.get("id_cliente") is None:
            problemas.append(f"{onde}: sem cliente.id_cliente")

        esperado = round(subtotal - cupom.get("desconto", 0.0) + (frete or 0.0), 2) if status != "cancelado" else 0.0
        if len(problemas) == antes and pedido.get("valor_total") != esperado:
            problemas.append(f"{onde}: valor_total {pedido.get('valor_total')} e a conta dá {esperado}")

        linhas_pedido.append({
            "id_pedido": id_pedido, "data_pedido": pedido.get("data_pedido"), "status": status,
            "id_cliente": cliente.get("id_cliente"), "cidade": cliente.get("cidade"),
            "n_itens": len(itens), "subtotal_itens": round(subtotal, 2),
            "cupom": cupom.get("codigo"), "desconto": cupom.get("desconto"),
            "tipo_entrega": tipo, "frete": frete, "valor_total": pedido.get("valor_total"),
        })
    return linhas_pedido, linhas_item, problemas


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arquivo", type=Path, default=ARQUIVO)
    args = ap.parse_args()

    pedidos_json = json.loads(args.arquivo.read_text(encoding="utf-8"))
    linhas_pedido, linhas_item, problemas = separar(pedidos_json)
    if problemas:
        log.error("o arquivo tem %d problema(s). Nada foi gravado.", len(problemas))
        for p in problemas:
            log.error("  %s", p)
        return 1

    pedidos = pd.DataFrame(linhas_pedido)
    itens = pd.DataFrame(linhas_item)
    print(f"{len(pedidos_json)} pedidos no arquivo, {len(pedidos)} na tabela de pedidos")
    print(f"{len(itens)} itens na tabela de itens; a soma das listas dá {pedidos['n_itens'].sum()}")
    print("id_pedido único em pedidos:", pedidos["id_pedido"].is_unique)
    print("id_pedido + item único em itens:", not itens.duplicated(["id_pedido", "item"]).any())
    print("todo item tem o seu pedido:", itens["id_pedido"].isin(pedidos["id_pedido"]).all())
    SAIDA.mkdir(exist_ok=True)
    pedidos.to_csv(SAIDA / "pedidos.csv", index=False)
    itens.to_csv(SAIDA / "itens.csv", index=False)
    print("gravei saida/pedidos.csv e saida/itens.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
