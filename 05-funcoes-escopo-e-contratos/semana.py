"""Pedido 3 da prática guiada: a semana do mês de cada data que você passar no comando.

Uso: python3 semana.py 2026-05-01 2026-05-07
"""
import sys


def semana_do_mes(data):
    """Semana do mês de uma data "AAAA-MM-DD": dias 1 a 7 são a semana 1, 8 a 14 a semana 2, e assim por diante."""
    dia = int(data[8:10])
    return (dia - 1) // 7 + 1


for data in sys.argv[1:]:
    try:
        print(data, "->", semana_do_mes(data))
    except Exception as erro:
        print(data, "->", type(erro).__name__)
