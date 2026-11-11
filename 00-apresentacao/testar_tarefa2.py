"""Roda a função total_pedido de tarefa2.py com os três exemplos do enunciado."""
import sys

try:
    from tarefa2 import total_pedido
except ModuleNotFoundError as erro:
    if erro.name != "tarefa2":
        raise
    print("Não achei tarefa2.py na mesma pasta deste teste. Coloque os dois arquivos juntos e rode de novo.")
    sys.exit(1)
except ImportError:
    print("tarefa2.py ainda não tem a função total_pedido. Escreva a função e rode de novo.")
    sys.exit(1)

exemplos = [
    ([], 0),
    ([{"qtd": 2, "preco": 25.0}], 50.0),
    ([{"qtd": 2, "preco": 25.0}, {"qtd": 1, "preco": 60.0}], 110.0),
]

erros = 0
for itens, esperado in exemplos:
    obtido = total_pedido(itens)
    if obtido == esperado:
        print(f"ok     {len(itens)} itens: {obtido}")
    else:
        print(f"errado {len(itens)} itens: retornou {obtido!r}, o esperado é {esperado!r}")
        erros += 1

sys.exit(1 if erros else 0)
