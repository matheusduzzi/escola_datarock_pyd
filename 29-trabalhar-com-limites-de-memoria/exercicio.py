"""Exercício: o resumo de 2025 por cidade, lido por partes.

Escreva COLUNAS_EX, TIPOS_EX e a função resumo_por_partes. Depois rode, de dentro desta pasta:

    python3 gerar.py
    python3 exercicio.py

Enquanto a função não estiver escrita, o programa para com o código 1.
Com a função escrita, ele compara o seu resultado com o da leitura inteira em três tamanhos de parte,
anota quantas linhas tinha a maior parte que a função leu e quantas linhas de itens ela juntou
com pd.concat, mede o pico de memória, grava
resumo_cidades.csv e sai com 0 se tudo estiver certo.
"""
import contextlib
import sys

import pandas as pd
from pandas.io.parsers.readers import TextFileReader

from medir import medir, mb

ARQUIVO = 'historico_itens.csv'
ANO = '2025'

# As colunas que a conta usa e os tipos de cada uma. Preencha.
COLUNAS_EX = []
TIPOS_EX = {}


def resumo_inteiro(caminho):
    """O código da IA: lê o arquivo inteiro e faz a conta. Serve de referência."""
    tabela = pd.read_csv(caminho)
    entregues = tabela[(tabela['status'] == 'entregue') & (tabela['data'].str[:4] == ANO)]
    resumo = entregues.groupby('cidade').agg(pedidos=('id_pedido', 'nunique'), faturamento=('valor', 'sum'))
    resumo['ticket_medio'] = resumo['faturamento'] / resumo['pedidos']
    return resumo


def resumo_por_partes(caminho, tamanho):
    """Lê o arquivo em partes de `tamanho` linhas, só com COLUNAS_EX e TIPOS_EX, e retorna o mesmo
    resumo que resumo_inteiro: uma linha por cidade, com as colunas pedidos (pedidos entregues em 2025,
    cada pedido contado uma vez), faturamento (soma do valor dos itens) e ticket_medio (faturamento / pedidos)."""
    raise NotImplementedError('falta escrever resumo_por_partes')


@contextlib.contextmanager
def anotando_partes(anotadas, juntadas):
    """Enquanto o bloco roda, anota em `anotadas` quantas linhas cada leitura do read_csv devolveu
    e em `juntadas` quantas linhas de itens cada pd.concat juntou.

    Toda leitura do read_csv passa por TextFileReader.read: a leitura inteira devolve o arquivo todo
    de uma vez, e a leitura com chunksize devolve uma parte por volta do for. Uma linha de item é uma
    linha de tabela com as mesmas colunas das partes lidas, inteira ou filtrada. A soma por pedido ou
    por cidade tem outras colunas e não conta."""
    original_read, original_concat = TextFileReader.read, pd.concat
    colunas_lidas = set()

    def read(self, *args, **kwargs):
        tabela = original_read(self, *args, **kwargs)
        anotadas.append(len(tabela))
        colunas_lidas.add(tuple(tabela.columns))
        return tabela

    def concat(objs, *args, **kwargs):
        if not isinstance(objs, dict):
            objs = list(objs)
        tabelas = objs.values() if isinstance(objs, dict) else objs
        juntadas.append(sum(len(t) for t in tabelas
                            if isinstance(t, pd.DataFrame) and tuple(t.columns) in colunas_lidas))
        return original_concat(objs, *args, **kwargs)

    TextFileReader.read, pd.concat = read, concat
    try:
        yield
    finally:
        TextFileReader.read, pd.concat = original_read, original_concat


def iguais(a, b):
    """Compara dois resumos: mesmas cidades, mesmos pedidos e os valores iguais em centavos."""
    a = a.set_axis(a.index.astype(str)).sort_index()
    b = b.set_axis(b.index.astype(str)).sort_index()
    if list(a.index) != list(b.index):
        return 'cidades diferentes'
    if 'pedidos' not in a or (a['pedidos'] != b['pedidos']).any():
        dif = int((a['pedidos'] - b['pedidos']).sum()) if 'pedidos' in a else 'sem a coluna'
        return f'pedidos diferentes (diferença no total: {dif})'
    for coluna in ['faturamento', 'ticket_medio']:
        if coluna not in a or ((a[coluna] - b[coluna]).abs() > 0.004).any():
            return f'{coluna} diferente'
    return ''


def main():
    if not COLUNAS_EX:
        print('falta preencher COLUNAS_EX e TIPOS_EX')
    try:
        resumo_por_partes(ARQUIVO, 20_000)
    except NotImplementedError as e:
        print(e)
        sys.exit(1)
    referencia, pico_inteiro = medir(resumo_inteiro, ARQUIVO)
    problemas = []
    picos = {}
    for tamanho in [20_000, 3_333, 1_000_000]:
        anotadas, juntadas = [], []
        with anotando_partes(anotadas, juntadas):
            resumo, picos[tamanho] = medir(resumo_por_partes, ARQUIVO, tamanho)
        maior = max(anotadas, default=0)
        if tamanho < 1_000_000 and maior > tamanho:
            problemas.append(f'com chunksize={tamanho}, a maior parte lida tinha {maior} linhas: a função está lendo tudo de uma vez?')
        itens = max(juntadas, default=0)
        if tamanho < 1_000_000 and itens > tamanho:
            problemas.append(f'com chunksize={tamanho}, um pd.concat juntou {itens} linhas de itens das partes: '
                             'a função está remontando o arquivo antes da conta?')
        diferenca = iguais(resumo, referencia)
        print(f'chunksize={tamanho}: pico {mb(picos[tamanho])} | ' + (f'diferente: {diferenca}' if diferenca else 'igual à leitura inteira'))
        if diferenca:
            problemas.append(f'chunksize={tamanho}: {diferenca}')
    print(f'leitura inteira (resumo_inteiro): pico {mb(pico_inteiro)}')
    if picos[20_000] > 0.5 * pico_inteiro:
        problemas.append('o pico por partes não ficou abaixo da metade do pico da leitura inteira')
    resumo.round(2).to_csv('resumo_cidades.csv')
    print(f'resumo_cidades.csv: {len(resumo)} cidades | colunas: {", ".join(resumo.columns)}')
    print('resultado:', 'ok' if not problemas else '; '.join(problemas))
    sys.exit(1 if problemas else 0)


if __name__ == '__main__':
    main()
