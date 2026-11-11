"""Pedido 1 da prática guiada: escreva o que cada linha numerada mostra antes de rodar."""
FRETE = 15


def com_frete(valor):
    return valor + FRETE


def frete_de_natal():
    FRETE = 25
    return FRETE


def somar_ao_frete(extra):
    FRETE = FRETE + extra
    return FRETE


def anotar(id_pedido, anotados=[]):
    anotados.append(id_pedido)
    return anotados


print("1.", com_frete(100))
print("2.", frete_de_natal(), FRETE)
FRETE = 30
print("3.", com_frete(100))
try:
    somar_ao_frete(5)
except UnboundLocalError as erro:
    print("4.", type(erro).__name__)
print("5.", anotar(87), anotar(472))
print("6.", anotar(604, []), anotar(79))
