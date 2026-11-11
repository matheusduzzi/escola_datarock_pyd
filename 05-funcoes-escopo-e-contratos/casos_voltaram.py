"""Casos de fronteira do clientes_que_voltaram, para o exercício.

Uso: python3 casos_voltaram.py voltaram        (testa a função do Caio, em voltaram.py)
     python3 casos_voltaram.py voltaram_novo   (testa a sua versão, em voltaram_novo.py)

Cada caso tem uma lista pequena de pedidos e uma ou mais chamadas, na ordem, cada uma com o
resultado esperado. Para um caso em que a função deve recusar, ponha a exceção como esperado,
por exemplo ValueError. Cada caso começa com o arquivo da função carregado de novo, então um caso
não interfere no outro. Escreva o esperado a partir do seu contrato, antes de rodar.
"""
import importlib
import sys


def pedido(id_cliente, data, status="entregue"):
    """Um pedido como o csv.DictReader lê: tudo em texto."""
    return {"id_pedido": "0", "id_cliente": str(id_cliente), "id_produto": "1", "data_pedido": data,
            "quantidade": "1", "valor": "10.00", "status": status}


CASOS = [
    ("quem recebeu nos dois meses aparece, quem recebeu em um só não",
     [pedido(5, "2026-05-10"), pedido(5, "2026-06-03"), pedido(6, "2026-05-12")],
     [("2026-05", "2026-06", [5])]),
    # Escreva os seus casos aqui, no mesmo formato.
]


def main(nome_do_arquivo):
    falhas = 0
    for descricao, pedidos, chamadas in CASOS:
        modulo = importlib.reload(importlib.import_module(nome_do_arquivo))
        for mes_antes, mes_depois, esperado in chamadas:
            try:
                obtido = modulo.clientes_que_voltaram(pedidos, mes_antes, mes_depois)
            except Exception as erro:
                obtido = type(erro)
            certo = obtido == esperado
            falhas += not certo
            print(("ok    " if certo else "FALHA ") + f"{descricao} ({mes_antes} e {mes_depois})")
            if not certo:
                print(f"      esperado {esperado}\n      obtido   {obtido}")
    print(f"{falhas} falhas")
    return falhas


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python3 casos_voltaram.py voltaram  (ou voltaram_novo)")
    raise SystemExit(1 if main(sys.argv[1]) else 0)
