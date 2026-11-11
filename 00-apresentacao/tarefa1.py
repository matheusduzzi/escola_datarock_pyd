# Tarefa 1. Leia o programa inteiro e anote a saída na folha antes de rodar.

pedido = {
    "id": 7,
    "cidade": "Santos",
    "itens": [
        {"produto": "caneca", "qtd": 2, "preco": 25.0},
        {"produto": "camiseta", "qtd": 1, "preco": 60.0},
    ],
}
cupom = "VOLTA10"

total = 0
for item in pedido["itens"]:
    total = total + item["qtd"] * item["preco"]

if cupom == "VOLTA10":
    total = total - 10

if total > 100:
    frete = 0
else:
    frete = 15

codigo = str(pedido["id"]) + "0"
print(total, frete, total + frete, codigo)
