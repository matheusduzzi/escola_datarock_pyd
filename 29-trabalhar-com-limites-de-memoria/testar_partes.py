"""Testa a leitura por partes e a comparação do memoria.py com as primeiras 30 mil linhas do histórico.

    python3 testar_partes.py

Para cada caso, diz o que era esperado (igual ou diferente) e o que a comparação respondeu.
Sai com 1 se a comparação errar algum caso. Rode antes python3 gerar.py.
"""
import io
import sys

import pandas as pd

import memoria as m

with open(m.ARQUIVO, encoding='utf-8') as f:
    AMOSTRA = ''.join(next(f) for _ in range(30_001))


def arquivo():
    return io.StringIO(AMOSTRA)


def por_partes(tamanho, tipos=m.TIPOS):
    return m.faturamento_por_partes(arquivo(), tamanho, tipos)


def distintos(tamanho, somando):
    pares, contagens = [], []
    for p in pd.read_csv(arquivo(), usecols=m.COLUNAS, dtype=m.TIPOS, chunksize=tamanho):
        contagens.append(m.clientes_distintos(p))
        e = p[p['status'] == 'entregue']
        pares.append(pd.DataFrame({'mes': e['data'].astype(str).str[:7], 'id_cliente': e['id_cliente']}).drop_duplicates())
    if somando:
        return pd.concat(contagens).groupby(level=0).sum().astype(float)
    return pd.concat(pares).drop_duplicates().groupby('mes')['id_cliente'].size().astype(float)


inteiro = pd.read_csv(arquivo())
pedidos = inteiro['id_pedido']
cortados = sum(pedidos.iloc[i - 1] == pedidos.iloc[i] for i in range(3_333, len(pedidos), 3_333))
certo = m.faturamento(inteiro)
certo_distintos = m.clientes_distintos(inteiro).astype(float)


def um_centavo(s):
    s = s.copy()
    s.iloc[3] += 0.01
    return s


def ruido(s):
    s = s.copy()
    s.iloc[3] += 0.001
    return s


CASOS = [
    ('partes de 1000 linhas', lambda: por_partes(1_000), certo, True),
    (f'partes de 3333 linhas, que cortam {cortados} pedidos no meio', lambda: por_partes(3_333), certo, True),
    ('uma parte maior que o arquivo', lambda: por_partes(100_000), certo, True),
    ('as mesmas somas em outra ordem', lambda: certo.sample(frac=1, random_state=1), certo, True),
    ('diferença de um décimo de centavo, de arredondamento', lambda: ruido(certo), certo, True),
    ('um valor com um centavo a mais', lambda: um_centavo(certo), certo, False),
    ('uma categoria de um mês faltando', lambda: certo.drop(certo.index[0]), certo, False),
    ('valor lido como float32', lambda: por_partes(3_333, {**m.TIPOS, 'valor': 'float32'}), certo, False),
    ('clientes distintos somando as partes', lambda: distintos(3_333, True), certo_distintos, False),
    ('clientes distintos com os pares juntados', lambda: distintos(3_333, False), certo_distintos, True),
]

erros = 0
for nome, calcular, referencia, esperado in CASOS:
    igual, detalhe = m.iguais(calcular(), referencia, unidade='' if referencia is certo_distintos else 'R$ ')
    acertou = igual == esperado
    erros += not acertou
    print(f"{'certo ' if acertou else 'ERRADO'} {nome}: esperado {'igual' if esperado else 'diferente'}, "
          f"a comparação disse: {'igual' if igual else 'diferente'} ({detalhe})")
print(f'{erros} caso(s) com resposta errada')
sys.exit(1 if erros else 0)
