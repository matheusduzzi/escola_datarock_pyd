"""O script do Caio, só com o caminho trocado para a pasta da aula.

    python3 juntar_direto.py

Junta todos os .json da pasta exportacoes/ numa tabela só, do jeito mais direto.
Roda sem erro. A aula mostra o que ele deixa passar.
"""
import glob

import pandas as pd

arquivos = glob.glob("exportacoes/*.json")
pedidos = pd.concat([pd.read_json(a, dtype=False) for a in arquivos], ignore_index=True)

print(len(arquivos), "arquivos lidos")
print(len(pedidos), "pedidos")
print(pedidos.groupby(pedidos["data_pedido"].str[:7]).size().to_string())
print("id_pedido repetido:", pedidos["id_pedido"].duplicated().sum())
