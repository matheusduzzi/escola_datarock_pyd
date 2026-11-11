"""O pedido 2 da prática guiada: o que acontece com tempos depois de cada divisão.

    python3 vista.py
"""
import numpy as np

import parciais

r = parciais.carregar()
tempos = r["tempos"]
de_2024 = r["edicao"] == 2024
print("antes:                    tempos[1, 0] =", tempos[1, 0])

so_2024 = tempos[de_2024]
so_2024 /= 60
print("depois de so_2024 /= 60:  tempos[1, 0] =", tempos[1, 0])

natacao = tempos[:, 0]
natacao /= 60
print("depois de natacao /= 60:  tempos[1, 0] =", round(tempos[1, 0], 2))
