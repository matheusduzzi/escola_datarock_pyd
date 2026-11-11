"""Ticket médio do mês, depois da aula: uma função para ler, uma para calcular, uma para mostrar."""
import csv
import re
import sys
from pathlib import Path

PEDIDOS = Path(__file__).resolve().parent.parent / "dados" / "loja" / "pedidos.csv"


def ler_pedidos(caminho):
    """Lê o CSV de pedidos e retorna uma lista de dicionários, com todos os valores em texto."""
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def resumo_do_mes(pedidos, mes):
    """Resumo dos pedidos entregues de um mês.

    Recebe: pedidos, uma lista de dicionários com as colunas do pedidos.csv, em texto,
        como o csv.DictReader lê; mes, um texto no formato "AAAA-MM".
    Retorna: um dicionário novo com mes; pedidos, quantos pedidos entregues o mês tem;
        sem_valor, quantos deles estão sem valor; faturamento, a soma dos valores em reais;
        e ticket, o faturamento dividido pelos pedidos com valor, ou None se nenhum tem valor.
    Altera: nada. A lista e os dicionários recebidos saem como entraram.
    Recusa: mes fora do formato "AAAA-MM" levanta ValueError.
    Não faz: ler arquivo, mostrar na tela, decidir o que fazer com o pedido sem valor.
    """
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", mes):
        raise ValueError(f"mês fora do formato AAAA-MM: {mes!r}")
    do_mes = [p for p in pedidos if p["status"] == "entregue" and p["data_pedido"][:7] == mes]
    valores = [float(p["valor"]) for p in do_mes if p["valor"] != ""]
    faturamento = round(sum(valores), 2)
    return {
        "mes": mes,
        "pedidos": len(do_mes),
        "sem_valor": len(do_mes) - len(valores),
        "faturamento": faturamento,
        "ticket": round(faturamento / len(valores), 2) if valores else None,
    }


def mostrar(resumo):
    """Retorna a linha do relatório para um resumo. Não imprime."""
    if resumo["ticket"] is None:
        ticket = "sem pedidos com valor"
    else:
        ticket = f"R$ {resumo['ticket']:.2f}"
    return (f"{resumo['mes']}: ticket médio {ticket}, {resumo['pedidos']} pedidos entregues, "
            f"{resumo['sem_valor']} sem valor")


def main(meses):
    pedidos = ler_pedidos(PEDIDOS)
    for mes in meses:
        print(mostrar(resumo_do_mes(pedidos, mes)))


if __name__ == "__main__":
    main(sys.argv[1:] or ["2026-05", "2026-06"])
