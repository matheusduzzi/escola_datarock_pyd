"""O que acontece com páginas por número quando a lista muda no meio da coleta.

    python3 pagina_que_escorrega.py

Não chama a API. Uma lista de 10 resultados, 4 por página, como a API do kit corta:
a página N vai da posição (N - 1) * 4 até N * 4.
"""


def pagina(lista, n, por_pagina=4):
    inicio = (n - 1) * por_pagina
    return lista[inicio:inicio + por_pagina]


resultados = [f"R{i:02d}" for i in range(1, 11)]
print("total antes:", len(resultados))
p1 = pagina(resultados, 1)
print("página 1:", p1)

# Entre a página 1 e a 2, chega um resultado novo no começo da lista.
resultados.insert(0, "R00")
print("chegou R00 no começo; total agora:", len(resultados))
p2, p3 = pagina(resultados, 2), pagina(resultados, 3)
print("página 2:", p2)
print("página 3:", p3)

coletados = p1 + p2 + p3
print("coletei", len(coletados), "linhas:", coletados)
print("vieram duas vezes:", sorted({r for r in coletados if coletados.count(r) > 1}))
print("ficaram de fora:", sorted(set(resultados) - set(coletados)))
print("a soma bate com o total de agora?", len(coletados) == len(resultados))
