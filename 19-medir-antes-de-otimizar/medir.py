"""Mede o tempo e o pico de memória de uma função, um de cada vez.

    import medir
    melhor, pior = medir.tempo(lambda: minha_conta(dados))
    resultado, pico = medir.pico(lambda: minha_conta(dados))
    print(medir.texto(melhor), medir.mb(pico))

Tempo: o timeit chama a função várias vezes, até passar de 0,2 segundo, e repete essa rodada
5 vezes. Volta o melhor e o pior tempo por chamada. O melhor é o que a máquina consegue; a
distância até o pior mostra o quanto a medida varia.

Memória: o tracemalloc conta a memória que o Python e o NumPy pedem enquanto a função roda.
O pico é o máximo que ficou pedido ao mesmo tempo, sem contar o que já existia antes.

As duas medidas nunca rodam juntas: o tracemalloc deixa o programa mais lento.
"""
import timeit
import tracemalloc


def tempo(funcao, repeticoes=5):
    """(melhor, pior) tempo por chamada, em segundos."""
    relogio = timeit.Timer(funcao)
    chamadas, _ = relogio.autorange()
    rodadas = relogio.repeat(repeat=repeticoes, number=chamadas)
    return min(rodadas) / chamadas, max(rodadas) / chamadas


def pico(funcao):
    """(resultado, pico em bytes) de uma chamada de funcao()."""
    tracemalloc.start()
    try:
        resultado = funcao()
        _, maximo = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return resultado, maximo


def texto(seg):
    """0.0000123 vira '12.3 µs'; 0.0456 vira '45.6 ms'."""
    if seg < 1e-3:
        return f"{seg * 1e6:.1f} µs"
    if seg < 1:
        return f"{seg * 1e3:.1f} ms"
    return f"{seg:.2f} s"


def mb(nbytes):
    """16_000_000 vira '16.0 MB' (1 MB = 1 milhão de bytes, como o nbytes / 1e6)."""
    return f"{nbytes / 1e6:.1f} MB"
