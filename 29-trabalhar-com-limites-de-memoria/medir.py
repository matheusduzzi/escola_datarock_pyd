"""Mede o pico de memória que o Python e o pandas pediram enquanto uma função rodava.

Usa o tracemalloc, da biblioteca padrão. Ele conta a memória que o Python e o NumPy pedem;
o gerenciador de tarefas do sistema mostra mais, porque soma o próprio Python e as bibliotecas
carregadas. Para comparar dois jeitos de fazer a mesma coisa, a medida é a mesma régua.
"""
import tracemalloc


def medir(funcao, *args, **kwargs):
    """Roda funcao(*args, **kwargs) e retorna (resultado, pico em MB)."""
    tracemalloc.start()
    try:
        resultado = funcao(*args, **kwargs)
        _, pico = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return resultado, pico / 1e6


def mb(valor):
    """Formata megabytes com uma casa: 250.5 vira '250,5 MB'."""
    return f'{valor:.1f}'.replace('.', ',') + ' MB'
