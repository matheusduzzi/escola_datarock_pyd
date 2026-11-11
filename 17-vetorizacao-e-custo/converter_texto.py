"""Dois jeitos de converter as parciais de texto ('1:14:19') para segundos.

    python3 converter_texto.py

Um loop com a função segundos e a mesma função dentro do np.vectorize.
Os dois precisam dar os mesmos números.
"""
import json

import numpy as np

import cronometro
import parciais


def textos():
    itens = json.loads(parciais.ARQUIVO.read_text(encoding="utf-8"))
    return [i["parciais"][e] for i in itens for e in parciais.ETAPAS if i["parciais"][e] is not None]


def com_loop(lista):
    return [parciais.segundos(t) for t in lista]


segundos_vetorizado = np.vectorize(parciais.segundos)


def com_vectorize(arr):
    return segundos_vetorizado(arr)


def main():
    lista = textos()
    arr = np.array(lista)
    iguais = np.array_equal(np.array(com_loop(lista)), com_vectorize(arr))
    print(f"parciais em texto: {len(lista)} | os dois dão os mesmos números: {iguais}")
    print(f"loop com segundos():     {cronometro.texto(cronometro.medir(lambda: com_loop(lista)))}")
    print(f"np.vectorize(segundos):  {cronometro.texto(cronometro.medir(lambda: com_vectorize(arr)))}")


if __name__ == "__main__":
    main()
