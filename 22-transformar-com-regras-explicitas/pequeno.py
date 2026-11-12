"""Pedido 1 da prática guiada: as quatro etapas da loja numa tabela de seis linhas.

Rode de dentro da pasta da aula:

    python3 pequeno.py
"""
import pandas as pd

import loja
import pipeline

PEDIDOS = pd.DataFrame({
    'id_pedido':  [1, 2, 3, 4, 1, 6],
    'id_produto': [10, 20, 10, 20, 10, 10],
    'quantidade': [2, 1, 1, 3, 2, 1],
    'valor':      [92.68, None, 46.34, None, 92.68, 46.34],
    'status':     ['entregue', 'Entregue ', 'cancelado', 'CANCELADO', 'entregue', 'entregue'],
})

if __name__ == '__main__':
    print(PEDIDOS.to_string(index=False))
    print()
    final, contagens = pipeline.rodar(PEDIDOS, loja.ETAPAS, acompanhar=['valor'],
                                      medidas={'receita': lambda t: loja.brl(t['valor'].sum())})
    print(pipeline.mostrar(contagens))
    print()
    print(final.to_string(index=False))
