"""Casos de fronteira do resumo_do_mes, escritos a partir do contrato, antes de rodar.

Cada caso tem uma lista pequena de pedidos, o mês e o resultado esperado. O esperado vem do
contrato do docstring, não do que a função retorna hoje.
"""
import copy

from ticket_contrato import resumo_do_mes


def pedido(id_pedido, data, valor, status="entregue"):
    """Um pedido como o csv.DictReader lê: tudo em texto."""
    return {"id_pedido": str(id_pedido), "id_cliente": "1", "id_produto": "1", "data_pedido": data,
            "quantidade": "1", "valor": valor, "status": status}


def resumo(mes, pedidos, sem_valor, faturamento, ticket):
    return {"mes": mes, "pedidos": pedidos, "sem_valor": sem_valor, "faturamento": faturamento,
            "ticket": ticket}


CASOS = [
    ("primeiro e último dia do mês entram, o dia 1 do mês seguinte não",
     [pedido(1, "2026-05-01", "10.00"), pedido(2, "2026-05-31", "30.00"), pedido(3, "2026-06-01", "99.00")],
     "2026-05", resumo("2026-05", 2, 0, 40.0, 20.0)),
    ("cancelado não entra",
     [pedido(1, "2026-05-10", "10.00"), pedido(2, "2026-05-11", "500.00", "cancelado")],
     "2026-05", resumo("2026-05", 1, 0, 10.0, 10.0)),
    ("pedido sem valor conta no mês, mas fica fora do ticket",
     [pedido(1, "2026-05-10", "10.00"), pedido(2, "2026-05-11", "30.00"), pedido(3, "2026-05-12", "")],
     "2026-05", resumo("2026-05", 3, 1, 40.0, 20.0)),
    ("mês sem nenhum pedido",
     [pedido(1, "2026-05-10", "10.00")],
     "2026-07", resumo("2026-07", 0, 0, 0.0, None)),
    ("mês em que todos os pedidos estão sem valor",
     [pedido(1, "2026-05-10", ""), pedido(2, "2026-05-11", "")],
     "2026-05", resumo("2026-05", 2, 2, 0.0, None)),
    ("mês escrito sem o zero",
     [pedido(1, "2026-05-10", "10.00")],
     "2026-5", ValueError),
    ("mês 13",
     [pedido(1, "2026-05-10", "10.00")],
     "2026-13", ValueError),
]


def rodar(descricao, pedidos, mes, esperado):
    try:
        obtido = resumo_do_mes(pedidos, mes)
    except Exception as erro:
        obtido = type(erro)
    return obtido == esperado, obtido


def main():
    falhas = 0
    for descricao, pedidos, mes, esperado in CASOS:
        certo, obtido = rodar(descricao, pedidos, mes, esperado)
        falhas += not certo
        print(("ok    " if certo else "FALHA ") + descricao)
        if not certo:
            print(f"      esperado {esperado}\n      obtido   {obtido}")

    pedidos = [pedido(1, "2026-05-10", "10.00"), pedido(2, "2026-05-11", "")]
    antes = copy.deepcopy(pedidos)
    primeira = resumo_do_mes(pedidos, "2026-05")
    segunda = resumo_do_mes(pedidos, "2026-05")
    for certo, descricao in [(pedidos == antes, "a lista recebida sai como entrou"),
                             (primeira == segunda, "duas chamadas seguidas dão o mesmo resumo")]:
        falhas += not certo
        print(("ok    " if certo else "FALHA ") + descricao)
    print(f"{falhas} falhas em {len(CASOS) + 2} casos")
    return falhas


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
