"""Pedido 2 da prática guiada: jeitos diferentes de medir o mesmo quadro, com 1 milhão de linhas.

    python3 medicao.py

E e F medem outra conta, a conversão das parciais de texto para segundos, em Python puro,
sem e com o tracemalloc ligado.
"""
import time
import tracemalloc

import medir
import parciais
import versoes
import volume

inicio = time.perf_counter()
tempos = volume.gerar(1_000_000)
versoes.quadro(tempos)
a = time.perf_counter() - inicio

inicio = time.perf_counter()
versoes.quadro(tempos)
b = time.perf_counter() - inicio

melhor, pior = medir.tempo(lambda: versoes.quadro(tempos))

tracemalloc.start()
d, _ = medir.tempo(lambda: versoes.quadro(tempos))
tracemalloc.stop()

texto = [p for linha in parciais.carregar()["texto"] for p in linha if p is not None]


def converter():
    return [parciais.segundos(p) for p in texto]


e, _ = medir.tempo(converter)
tracemalloc.start()
f, _ = medir.tempo(converter)
tracemalloc.stop()

print(f"A  um perf_counter em volta de gerar + quadro:  {medir.texto(a)}")
print(f"B  um perf_counter só no quadro, uma chamada:   {medir.texto(b)}")
print(f"C  medir.tempo, melhor e pior de 5 rodadas:     {medir.texto(melhor)} a {medir.texto(pior)}")
print(f"D  medir.tempo com o tracemalloc ligado:        {medir.texto(d)}")
print()
print(f"converter {len(texto)} parciais de texto para segundos")
print(f"E  medir.tempo:                                 {medir.texto(e)}")
print(f"F  medir.tempo com o tracemalloc ligado:        {medir.texto(f)}")
