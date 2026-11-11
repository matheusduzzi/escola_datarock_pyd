"""Pedido 2 da prática guiada. Antes de rodar, escreva o que cada print vai mostrar."""


def os_dois_maiores(precos):
    precos.sort(reverse=True)
    return precos[:2]


def com_frete(precos, frete):
    precos = [preco + frete for preco in precos]
    return precos


precos = [102.92, 287.62, 251.75]

maiores = os_dois_maiores(precos)
print("1.", maiores)
print("2.", precos)

com_15 = com_frete(precos, 15)
print("3.", com_15)
print("4.", precos)

categoria = ("Eletro", [102.92, 287.62])
categoria[1].append(251.75)
print("5.", categoria)
