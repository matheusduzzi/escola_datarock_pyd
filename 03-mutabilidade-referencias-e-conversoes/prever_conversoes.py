"""Pedido 3 da prática guiada. Antes de rodar, escreva o que cada print vai mostrar."""

print("1.", int("3"), int(" 3 "), float("102.92"))
print("2.", int(2.9), int(-2.9), round(2.5), round(3.5))
print("3.", bool("False"), bool("0"), bool(""), bool(0))
print("4.", "10" < "9", 10 < 9)
print("5.", "3" + "2", int("3") + int("2"))
print("6.", 0.1 + 0.2, round(0.1 + 0.2, 2))

try:
    print(int("3.0"))
except ValueError as erro:
    print("7.", "ValueError:", erro)
