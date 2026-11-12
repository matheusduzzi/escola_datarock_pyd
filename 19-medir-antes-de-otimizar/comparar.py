"""O relatório: tempo e memória das cinco versões, em três volumes, com a equivalência ao lado.

    python3 comparar.py

Em cada volume, a entrada é a mesma para todas as versões (volume.gerar, sempre o mesmo sorteio).
O array é guardado antes de medir: o cronômetro e o tracemalloc só pegam a conta.
guardado: o tamanho do array que a conta recebe (nbytes).
pico: a memória a mais que a conta pediu ao mesmo tempo, pelo tracemalloc.
melhor e pior: o melhor e o pior tempo por chamada nas 5 rodadas do timeit.
"""
import medir
import versoes
import volume

for n in (10_000, 100_000, 1_000_000):
    tempos = volume.gerar(n)
    hoje = versoes.quadro(tempos)
    print(f"{n} linhas")
    print(f"  {'versão':<18}{'guardado':>10}{'pico':>10}{'melhor':>11}{'pior':>11}  equivale")
    for v in versoes.VERSOES:
        guardado = v["guardar"](tempos)
        conta = v["conta"]
        q, pico = medir.pico(lambda: conta(guardado))
        melhor, pior = medir.tempo(lambda: conta(guardado))
        print(f"  {v['nome']:<18}{medir.mb(guardado.nbytes):>10}{medir.mb(pico):>10}"
              f"{medir.texto(melhor):>11}{medir.texto(pior):>11}  {versoes.equivale(q, hoje)}")
    print()
