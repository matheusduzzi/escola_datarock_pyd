"""Quanto os tempos ocupam e como eles ficam guardados na memória.

    python3 memoria.py
    python3 memoria.py --linhas 1000000
"""
import argparse
import sys

import numpy as np

import parciais

ap = argparse.ArgumentParser()
ap.add_argument("--linhas", type=int, help="estima a memória para esse número de linhas, sem montar o array")
args = ap.parse_args()

tempos = parciais.carregar()["tempos"]

if args.linhas:
    print(f"Estimativa para {args.linhas} linhas, só os números:")
    for nome, tipo, colunas in (("tempos float64", "float64", 5), ("tempos float32", "float32", 5),
                                ("tempos int16", "int16", 5), ("status '<U8'", "<U8", 1), ("máscara bool", "bool", 1)):
        tamanho = np.dtype(tipo).itemsize
        print(f"  {nome:<15} {colunas * tamanho:>2} bytes por linha -> {args.linhas * colunas * tamanho:>10} bytes")
    sys.exit(0)

print("tempos:", tempos.shape, tempos.dtype)
print("itemsize:", tempos.itemsize, "bytes por número")
print("nbytes:", tempos.nbytes, "bytes =", tempos.size, "números x", tempos.itemsize, "bytes")
print("strides:", tempos.strides, "| guardado linha a linha:", tempos.flags["C_CONTIGUOUS"])

transposto = tempos.T
print("\ntempos.T:", transposto.shape, "| strides:", transposto.strides,
      "| usa os mesmos números:", np.shares_memory(tempos, transposto))
achatado = tempos.reshape(-1)
print("tempos.reshape(-1):", achatado.shape, "| usa os mesmos números:", np.shares_memory(tempos, achatado))
convertido = tempos.astype(np.float32)
print("tempos.astype(np.float32):", convertido.nbytes, "bytes | usa os mesmos números:",
      np.shares_memory(tempos, convertido))

lista = tempos.tolist()
bytes_lista = sys.getsizeof(lista) + sum(sys.getsizeof(l) for l in lista) + sum(
    sys.getsizeof(v) for l in lista for v in l)
print("\nOs mesmos números numa lista de listas do Python:", bytes_lista, "bytes")
print("Cada número do Python é um objeto de", sys.getsizeof(4459.0), "bytes, fora o lugar dele na lista")
