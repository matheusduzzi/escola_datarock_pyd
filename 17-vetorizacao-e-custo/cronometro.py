"""Mede quanto tempo uma função leva, do jeito que a documentação do timeit recomenda.

    import cronometro
    seg = cronometro.medir(lambda: minha_conta(dados))
    print(cronometro.texto(seg))

O timeit chama a função várias vezes, até passar de 0,2 segundo, e repete essa rodada 5 vezes.
Fica o melhor tempo por chamada: os piores costumam ser outro programa disputando a máquina.
A medição com mais cuidado, de tempo e de memória, é a da aula 19, «Medir antes de otimizar».
"""
import timeit


def medir(funcao, repeticoes=5):
    relogio = timeit.Timer(funcao)
    chamadas, _ = relogio.autorange()
    return min(relogio.repeat(repeat=repeticoes, number=chamadas)) / chamadas


def texto(seg):
    """0.0000123 vira '12.3 µs'; 0.0456 vira '45.6 ms'."""
    if seg < 1e-3:
        return f"{seg * 1e6:.1f} µs"
    if seg < 1:
        return f"{seg * 1e3:.1f} ms"
    return f"{seg:.2f} s"
