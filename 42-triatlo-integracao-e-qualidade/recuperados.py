"""O exercício: juntar à base os resultados que a cronometragem recuperou depois da prova.

Você escreve a função juntar_recuperados. O juntar.py chama a função e mostra o resultado;
o test_recuperados.py tem os testes que você completa.

As regras estão no enunciado do exercício, na aula. Em resumo:
1. Um recuperado só preenche inscrição com o status "sem resultado". Na linha preenchida,
   fonte_resultado vira "recuperados", copias diz quantas vezes ele veio no arquivo,
   parciais_vazias conta as parciais vazias dele e origem_pagina e origem_posicao ficam vazias.
2. Recuperado igual ao que a base já tem: nada muda e não é pendência.
3. Recuperado diferente do que a base já tem: a base não muda; pendência
   "diferente do resultado da API".
4. id_inscricao que não está na base: pendência "inscrição que não existe".
5. Cópia idêntica no arquivo conta uma vez. Duas versões diferentes da mesma inscrição no
   arquivo: nenhuma entra; pendência "duas versões no arquivo".
6. A linha preenchida passa nas regras de integrar.conferir. Se quebrar alguma, a inscrição
   continua "sem resultado" e vira pendência "quebra a regra «<nome da regra>»".
7. A base que entrou na função não muda: a função retorna uma base nova.
"""
import integrar


def juntar_recuperados(base, recuperados):
    """Retorna (nova_base, pendencias).

    base: a base do rodar.py (DataFrame, uma linha por inscrição, colunas de integrar.COLUNAS).
    recuperados: a lista de resultados do recuperados.json, no formato da API.
    nova_base: a base com os recuperados que passaram, mesmas colunas e mesmos tipos.
    pendencias: um dicionário {id_inscricao: motivo} com o que não entrou e precisa de alguém decidir.
    """
    raise NotImplementedError("escreva a função juntar_recuperados")
