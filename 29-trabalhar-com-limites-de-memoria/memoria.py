"""O faturamento por mês e categoria do histórico do site, de seis jeitos.

    python3 memoria.py --jeito ia        o código da IA: lê o arquivo inteiro
    python3 memoria.py --jeito colunas   quanto cada coluna pesa e a leitura só das colunas da conta
    python3 memoria.py --jeito tipos     as colunas com tipos menores, e o tipo que muda a conta
    python3 memoria.py --jeito partes    a leitura por partes, com três tamanhos de parte
    python3 memoria.py --jeito distintos clientes por mês: a conta que não se soma por partes
    python3 memoria.py --jeito comparar  a comparação de memória e resultado, gravada em comparacao.md

Rode antes python3 gerar.py, que escreve historico_itens.csv.
"""
import argparse
import sys

import pandas as pd

from medir import medir, mb

ARQUIVO = 'historico_itens.csv'
COLUNAS = ['data', 'categoria', 'status', 'valor', 'id_cliente']
TIPOS = {'data': 'category', 'categoria': 'category', 'status': 'category', 'id_cliente': 'int32'}
PARTE = 20_000


def faturamento(tabela):
    """Soma do valor dos itens entregues, por mês (AAAA-MM) e categoria.

    Soma primeiro por dia e categoria; o mês sai do resultado pequeno, com 912 dias, e não das 410 mil linhas."""
    entregues = tabela[tabela['status'] == 'entregue']
    por_dia = entregues.groupby(['data', 'categoria'], observed=True)['valor'].sum().reset_index()
    por_dia['mes'] = por_dia['data'].astype(str).str[:7]
    por_dia['categoria'] = por_dia['categoria'].astype(str)
    return por_dia.groupby(['mes', 'categoria'])['valor'].sum()


def faturamento_por_partes(caminho, tamanho, tipos=TIPOS, nrows=None):
    """Lê o arquivo em partes de `tamanho` linhas, soma cada parte e junta as somas no fim."""
    somas = []
    for parte in pd.read_csv(caminho, usecols=COLUNAS, dtype=tipos, chunksize=tamanho, nrows=nrows):
        somas.append(faturamento(parte))
    return pd.concat(somas).groupby(level=[0, 1]).sum()


def iguais(a, b, unidade='R$ '):
    """Compara dois resultados por mês e categoria, em centavos. Retorna (True ou False, o que mudou)."""
    a, b = a.round(2).sort_index(), b.round(2).sort_index()
    if not a.index.equals(b.index):
        so_a, so_b = a.index.difference(b.index), b.index.difference(a.index)
        return False, f'chaves diferentes: {len(so_a)} só no primeiro, {len(so_b)} só no segundo'
    diferentes = (a - b).abs() > 0.004
    if diferentes.any():
        return False, f'{int(diferentes.sum())} de {len(a)} valores diferentes (maior diferença {unidade}{(a - b).abs().max():.2f})'.replace('.', ',')
    return True, f'{len(a)} valores iguais em centavos'


def ler_inteiro():
    return pd.read_csv(ARQUIVO)


def total(serie):
    return f'R$ {serie.sum():,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')


def ler_e_somar():
    tabela = ler_inteiro()
    return tabela.shape, faturamento(tabela)


def jeito_ia():
    ((linhas, colunas), fat), pico = medir(ler_e_somar)
    print(f'historico_itens.csv: {linhas} linhas x {colunas} colunas')
    print(f'pico de memória da leitura e da conta: {mb(pico)}')
    print(f'faturamento: {len(fat)} linhas (30 meses x 5 categorias) | total {total(fat)}')
    print(fat.tail(5).round(2).to_string())


def jeito_colunas():
    tabela = ler_inteiro()
    peso = tabela.memory_usage(deep=True, index=False).sort_values(ascending=False) / 1e6
    print('memory_usage(deep=True) por coluna, em MB:')
    for coluna, valor in peso.items():
        print(f'  {coluna:<15} {tabela[coluna].dtype!s:<8} {valor:5.1f}' + ('  <- usada na conta' if coluna in COLUNAS else ''))
    print(f'  soma: {peso.sum():.1f} | as 5 colunas da conta: {peso[COLUNAS].sum():.1f}')
    certo = faturamento(tabela)
    del tabela
    fat, pico = medir(lambda: faturamento(pd.read_csv(ARQUIVO, usecols=COLUNAS)))
    print(f'\nread_csv com usecols, {len(COLUNAS)} colunas: pico da leitura e da conta {mb(pico)}')
    print('resultado igual ao da leitura inteira:', *iguais(fat, certo))


def jeito_tipos():
    so = pd.read_csv(ARQUIVO, usecols=COLUNAS)
    fat_tipos, pico = medir(lambda: faturamento(pd.read_csv(ARQUIVO, usecols=COLUNAS, dtype=TIPOS)))
    com_tipos = pd.read_csv(ARQUIVO, usecols=COLUNAS, dtype=TIPOS)
    antes = so.memory_usage(deep=True, index=False) / 1e6
    depois = com_tipos.memory_usage(deep=True, index=False) / 1e6
    print('coluna       antes             depois')
    for c in COLUNAS:
        print(f'{c:<12} {so[c].dtype!s:<8} {antes[c]:4.1f} MB   {com_tipos[c].dtype!s:<8} {depois[c]:4.1f} MB')
    print(f'read_csv com usecols e dtype: pico da leitura e da conta {mb(pico)}')
    certo = faturamento(so)
    print('resultado igual ao da leitura inteira:', *iguais(fat_tipos, certo))
    print(f"valores distintos: data {com_tipos['data'].nunique()} | categoria {com_tipos['categoria'].nunique()} | "
          f"status {com_tipos['status'].nunique()} | id_cliente de {com_tipos['id_cliente'].min()} a {com_tipos['id_cliente'].max()}")
    i16 = pd.read_csv(ARQUIVO, usecols=['id_cliente'], dtype={'id_cliente': 'int16'})['id_cliente']
    trocados = (i16 != so['id_cliente']).sum()
    primeiro = (i16 != so['id_cliente']).idxmax()
    print(f"\nid_cliente como int16: {trocados} valores trocados, sem erro nem aviso | "
          f"{so['id_cliente'][primeiro]} virou {i16[primeiro]} | int16 vai de -32768 a 32767")
    f32 = pd.read_csv(ARQUIVO, usecols=COLUNAS, dtype={**TIPOS, 'valor': 'float32'})
    print(f"valor como float32: {f32.memory_usage(deep=True, index=False)['valor'] / 1e6:.1f} MB")
    print('resultado igual ao da leitura inteira:', *iguais(faturamento(f32), certo))
    print(f'total com float64: {total(certo)} | com float32: {total(faturamento(f32))}')


def jeito_partes():
    certo = faturamento(pd.read_csv(ARQUIVO, usecols=COLUNAS))
    pedidos = pd.read_csv(ARQUIVO, usecols=['id_pedido'])['id_pedido']
    for tamanho in [10_000, PARTE, 50_000]:
        fat, pico = medir(faturamento_por_partes, ARQUIVO, tamanho)
        partes = -(-len(pedidos) // tamanho)
        print(f'chunksize={tamanho}: {partes} partes | pico {mb(pico)} | igual à leitura inteira:', *iguais(fat, certo))
    cortes = sum(pedidos.iloc[i - 1] == pedidos.iloc[i] for i in range(PARTE, len(pedidos), PARTE))
    print(f'\ncom chunksize={PARTE}, pedidos com itens em duas partes: {cortes}')


def clientes_distintos(tabela):
    entregues = tabela[tabela['status'] == 'entregue']
    return entregues.groupby(entregues['data'].astype(str).str[:7].rename('mes'))['id_cliente'].nunique()


def distintos_somando_partes(tamanho):
    contagens = [clientes_distintos(p) for p in pd.read_csv(ARQUIVO, usecols=COLUNAS, dtype=TIPOS, chunksize=tamanho)]
    return pd.concat(contagens).groupby(level=0).sum()


def distintos_por_partes(tamanho):
    pares = []
    for p in pd.read_csv(ARQUIVO, usecols=COLUNAS, dtype=TIPOS, chunksize=tamanho):
        e = p[p['status'] == 'entregue']
        pares.append(pd.DataFrame({'mes': e['data'].astype(str).str[:7], 'id_cliente': e['id_cliente']}).drop_duplicates())
    return pd.concat(pares).drop_duplicates().groupby('mes')['id_cliente'].size()


def jeito_distintos():
    certo = clientes_distintos(pd.read_csv(ARQUIVO, usecols=COLUNAS))
    errado = distintos_somando_partes(PARTE)
    junto = distintos_por_partes(PARTE)
    tab = pd.DataFrame({'leitura inteira': certo, 'somando as partes': errado, 'pares por partes': junto})
    print('clientes que receberam pedido, por mês:')
    print(tab.head(4).to_string())
    print(f'meses com conta diferente da leitura inteira: somando as partes {int((errado != certo).sum())} de {len(certo)} | '
          f'pares por partes {int((junto != certo).sum())} de {len(certo)}')
    print(f'maior conta somando as partes: {errado.max()} clientes em {errado.idxmax()}')


def jeito_comparar():
    jeitos = [
        ('lê tudo (o código da IA)', lambda n: faturamento(pd.read_csv(ARQUIVO, nrows=n))),
        ('só as 5 colunas da conta', lambda n: faturamento(pd.read_csv(ARQUIVO, usecols=COLUNAS, nrows=n))),
        ('5 colunas com tipos menores', lambda n: faturamento(pd.read_csv(ARQUIVO, usecols=COLUNAS, dtype=TIPOS, nrows=n))),
        (f'5 colunas, tipos e partes de {PARTE} linhas', lambda n: faturamento_por_partes(ARQUIVO, PARTE, nrows=n)),
        ('o mesmo, com valor em float32', lambda n: faturamento_por_partes(ARQUIVO, PARTE, {**TIPOS, 'valor': 'float32'}, n)),
    ]
    tamanhos = [100_000, 200_000, None]
    linhas = []
    certo = None
    for nome, funcao in jeitos:
        picos = []
        for n in tamanhos:
            fat, pico = medir(funcao, n)
            picos.append(pico)
        if certo is None:
            certo, resultado = fat, 'é a referência'
        else:
            ok, detalhe = iguais(fat, certo)
            resultado = ('igual: ' if ok else 'diferente: ') + detalhe
        linhas.append((nome, picos, resultado))
    n_linhas = f"{len(pd.read_csv(ARQUIVO, usecols=['id_item'])):,}".replace(',', '.')
    tabela = [f'| Jeito | 100 mil linhas | 200 mil linhas | {n_linhas} linhas (todas) | Resultado com o arquivo inteiro |',
              '|---|---:|---:|---:|---|']
    for nome, picos, resultado in linhas:
        tabela.append(f"| {nome} | {' | '.join(mb(p) for p in picos)} | {resultado} |")
    texto = '\n'.join(['# Faturamento por mês e categoria: memória e resultado', '',
                       f'Arquivo: historico_itens.csv, {n_linhas} linhas x 20 colunas. Resultado: {len(certo)} somas '
                       f'(30 meses x 5 categorias), total {total(certo)}, comparadas em centavos com a leitura do arquivo inteiro.',
                       '', 'Pico de memória de cada jeito, lendo as primeiras 100 mil linhas, as primeiras 200 mil e o arquivo todo:', '']
                      + tabela +
                      ['', '- O pico é medido com o tracemalloc (medir.py): a memória que o Python e o pandas pediram durante a leitura e a conta.',
                       '  O gerenciador de tarefas mostra mais, porque soma o próprio Python. A régua é a mesma para todos os jeitos.',
                       '- Tudo roda num computador só, uma parte depois da outra.', '',
                       'Gerado por `python3 memoria.py --jeito comparar`.', ''])
    with open('comparacao.md', 'w', encoding='utf-8') as f:
        f.write(texto)
    print('comparacao.md escrito\n')
    print('\n'.join(tabela))


if __name__ == '__main__':
    jeitos = {'ia': jeito_ia, 'colunas': jeito_colunas, 'tipos': jeito_tipos, 'partes': jeito_partes,
              'distintos': jeito_distintos, 'comparar': jeito_comparar}
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--jeito', choices=jeitos, required=True)
    jeito = ap.parse_args().jeito
    try:
        open(ARQUIVO).close()
    except FileNotFoundError:
        print('historico_itens.csv não encontrado: rode antes python3 gerar.py')
        sys.exit(1)
    jeitos[jeito]()
