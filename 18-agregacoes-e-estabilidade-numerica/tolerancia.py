"""Pedido 2 da prática guiada: seis comparações, True ou False."""
import math

import numpy as np

contas = [
    ("0.1 + 0.2 == 0.3", lambda: 0.1 + 0.2 == 0.3),
    ("np.isclose(0.1 + 0.2, 0.3)", lambda: np.isclose(0.1 + 0.2, 0.3)),
    ("np.isclose(41772.49, 41772.2)", lambda: np.isclose(41772.49, 41772.2)),
    ("math.isclose(41772.49, 41772.2)", lambda: math.isclose(41772.49, 41772.2)),
    ("np.isclose(41772.49, 41772.2, rtol=0, atol=0.001)", lambda: np.isclose(41772.49, 41772.2, rtol=0, atol=0.001)),
    ("np.isclose(0.000000005, 0)", lambda: np.isclose(0.000000005, 0)),
    ("math.isclose(0.000000005, 0)", lambda: math.isclose(0.000000005, 0)),
]
for texto, conta in contas:
    print(f"{texto:<52}-> {bool(conta())}")
