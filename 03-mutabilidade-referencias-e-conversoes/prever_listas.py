"""Pedido 1 da prática guiada. Antes de rodar, escreva o que cada print vai mostrar."""

modelo = {"cidade": "Campinas", "avisos": []}

mesmo = modelo
copia = dict(modelo)

copia["cidade"] = "Santos"
copia["avisos"].append("frete grátis")

print("1.", modelo)
print("2.", copia)
print("3.", mesmo is modelo, copia is modelo, copia["avisos"] is modelo["avisos"])

ids = [87, 472]
outra = ids
outra += [604]
print("4.", ids)

outra = outra + [79]
print("5.", ids, outra)
