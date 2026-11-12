"""A receita do semestre da Loja Exemplo, de sete jeitos.

Rode de dentro da pasta da aula, depois do gerar.py:

    python3 loja.py --jeito ia          o código da IA, comparado com o fechamento do financeiro
    python3 loja.py --jeito limpeza     o status e as linhas repetidas
    python3 loja.py --jeito regra       quem entra na receita
    python3 loja.py --jeito imputacao   três jeitos de preencher o valor vazio
    python3 loja.py --jeito ordem       a mesma média antes e depois da limpeza e da regra
    python3 loja.py --jeito certo       o pipeline com as contagens de cada etapa
    python3 loja.py --jeito gerente     o pedido sem valor fica fora até o caixa confirmar
"""
import argparse

import pandas as pd

import pipeline
from pipeline import Etapa

PRODUTOS = '../dados/loja/produtos.csv'


def brl(x):
    texto = 'R$ ' + f'{abs(x):,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')
    return '-' + texto if x < 0 else texto


def ler():
    return pd.read_csv('pedidos_caixa.csv')


def produtos():
    return pd.read_csv(PRODUTOS)


def fechamento():
    return pd.read_csv('fechamento_financeiro.csv')


def resumo(p):
    """Pedidos, receita e ticket médio de uma tabela já preparada."""
    n, receita = len(p), p['valor'].sum()
    return n, receita, receita / n


def comparar(p, rotulo):
    f = fechamento()
    n, receita, ticket = resumo(p)
    nf, rf = int(f['pedidos_entregues'].sum()), f['receita'].sum()
    print(f'{rotulo:<12} pedidos {n:>5} | receita {brl(receita):>16} | ticket {brl(ticket):>10}')
    print(f'{"financeiro":<12} pedidos {nf:>5} | receita {brl(rf):>16} | ticket {brl(rf / nf):>10}')
    print(f'{"diferença":<12} pedidos {n - nf:>+5} | receita {brl(receita - rf):>16}')


# ---------------------------------------------------------------- o código da IA

def preparar_ia(p):
    p['valor'] = p['valor'].fillna(p['valor'].mean())
    p = p.drop_duplicates()
    p = p[p['status'] == 'entregue']
    return p


def jeito_ia():
    p = ler()
    print(f'pedidos_caixa.csv: {len(p)} linhas')
    comparar(preparar_ia(p), 'código da IA')


# ---------------------------------------------------------------- as etapas

def padronizar_status(p):
    p['status'] = p['status'].str.strip().str.lower()
    return p


def tirar_repetidas(p):
    return p.drop_duplicates()


def so_entregue(p):
    return p[p['status'] == 'entregue'].copy()


def preencher_valor(p):
    preco = p['id_produto'].map(produtos().set_index('id_produto')['preco'])
    vazio = p['valor'].isna()
    p['valor'] = p['valor'].fillna((preco * p['quantidade']).round(2))
    p['valor_preenchido'] = vazio & p['valor'].notna()
    return p


ETAPAS = [
    Etapa('limpeza', 'padronizar status', padronizar_status, muda=('status',)),
    Etapa('limpeza', 'tirar linha repetida', tirar_repetidas),
    Etapa('regra', 'só pedido entregue', so_entregue,
          motivo='A gerente: receita é o que foi entregue; cancelado não entra.'),
    Etapa('imputação', 'valor vazio = preço × quantidade', preencher_valor, muda=('valor',),
          motivo='Nas linhas com valor, o valor é sempre preço × quantidade.'),
]


def jeito_limpeza():
    p = ler()
    print('status como veio do caixa:')
    print(p['status'].map(repr).value_counts().to_string())
    limpo = padronizar_status(p.copy())
    print('\nstatus depois de strip() e lower():')
    print(limpo['status'].value_counts().to_string())
    rep = p.duplicated()
    print(f'\nlinhas iguais a uma linha anterior: {rep.sum()}')
    print(f'id_pedido repetido: {p["id_pedido"].duplicated().sum()} | '
          f'id repetido com alguma coluna diferente: {(p["id_pedido"].duplicated() & ~rep).sum()}')
    print('dias das repetidas:', p.loc[rep, 'data_pedido'].value_counts().sort_index().to_dict())
    print(f'valor vazio: {p["valor"].isna().sum()} linhas, '
          f'{p.loc[~rep, "valor"].isna().sum()} sem contar as repetidas')
    print('repetidas com valor vazio:', p.loc[rep & p['valor'].isna(), ['id_pedido', 'data_pedido']].to_dict('records'))


def jeito_regra():
    p = tirar_repetidas(padronizar_status(ler()))
    print('pedidos sem repetição, por status:')
    t = p.groupby('status').agg(pedidos=('id_pedido', 'size'), valor_vazio=('valor', lambda s: s.isna().sum()),
                                soma_do_valor=('valor', 'sum'))
    t['soma_do_valor'] = t['soma_do_valor'].map(brl)
    print(t.to_string())


def jeito_imputacao():
    p = so_entregue(tirar_repetidas(padronizar_status(ler())))
    pr = produtos().set_index('id_produto')['preco']
    calc = (p['id_produto'].map(pr) * p['quantidade']).round(2)
    com = p['valor'].notna()
    iguais = (p.loc[com, 'valor'].round(2) == calc[com]).sum()
    print(f'pedidos entregues: {len(p)} | com valor: {com.sum()} | valor vazio: {(~com).sum()}')
    print(f'nas linhas com valor, valor == preço × quantidade: {iguais} de {com.sum()}')
    print()
    jeitos = {
        'fillna(0)': p['valor'].fillna(0),
        'fillna(média)': p['valor'].fillna(p['valor'].mean()),
        'preço × quantidade': p['valor'].fillna(calc),
    }
    rf = fechamento()['receita'].sum()
    print(f'{"jeito":<20}{"os 11 preenchidos somam":>24}{"receita":>18}{"diferença do financeiro":>26}')
    for nome, v in jeitos.items():
        print(f'{nome:<20}{brl(v[~com].sum()):>24}{brl(v.sum()):>18}{brl(v.sum() - rf):>26}')
    print(f'\nmédia do valor nos {com.sum()} com valor: {brl(p["valor"].mean())}')
    print(f'preço × quantidade dos 11, do menor ao maior: {", ".join(brl(x) for x in sorted(calc[~com]))}')


def jeito_ordem():
    bruto = ler()
    limpo = so_entregue(tirar_repetidas(padronizar_status(bruto)))
    print(f'média do valor, tabela como veio ({bruto["valor"].notna().sum()} valores): {brl(bruto["valor"].mean())}')
    print(f'média do valor, depois da limpeza e da regra ({limpo["valor"].notna().sum()} valores): '
          f'{brl(limpo["valor"].mean())}')
    canc = tirar_repetidas(padronizar_status(bruto))
    canc = canc[canc['status'] == 'cancelado']
    print(f'média do valor dos cancelados ({canc["valor"].notna().sum()} valores): {brl(canc["valor"].mean())}')
    print()
    ia = preparar_ia(bruto.copy())
    print(f'código da IA: valor preenchido com {brl(bruto["valor"].mean())} | '
          f'pedidos com esse valor no fim: {(ia["valor"] == bruto["valor"].mean()).sum()}')


def jeito_certo():
    p = ler()
    final, contagens = pipeline.rodar(p, ETAPAS, acompanhar=['valor'],
                                      medidas={'receita': lambda t: brl(t['valor'].sum())})
    contagens.to_csv('contagens.csv', index=False)
    print(pipeline.mostrar(contagens))
    print()
    comparar(final, 'pipeline')
    f = fechamento().set_index('mes')
    mes = final.assign(mes=final['data_pedido'].str[:7]).groupby('mes').agg(
        pedidos=('id_pedido', 'size'), receita=('valor', 'sum'), preenchidos=('valor_preenchido', 'sum'))
    print()
    print('por mês, contra o fechamento do financeiro:')
    print(f'{"mês":<9}{"pedidos":>8}{"receita":>16}{"preenchidos":>13}{"financeiro":>16}  bate')
    for r in mes.itertuples():
        bate = r.pedidos == f.loc[r.Index, 'pedidos_entregues'] and abs(r.receita - f.loc[r.Index, 'receita']) < 0.005
        print(f'{r.Index:<9}{r.pedidos:>8}{brl(r.receita):>16}{int(r.preenchidos):>13}'
              f'{brl(f.loc[r.Index, "receita"]):>16}  {"sim" if bate else "não"}')


def so_com_valor(p):
    return p[p['valor'].notna()].copy()


def jeito_gerente():
    etapas = ETAPAS[:3] + [Etapa('regra', 'só pedido com valor anotado', so_com_valor,
                                 motivo='A gerente: pedido sem valor espera o caixa confirmar.')]
    final, contagens = pipeline.rodar(ler(), etapas, acompanhar=['valor'],
                                      medidas={'receita': lambda t: brl(t['valor'].sum())})
    print(pipeline.mostrar(contagens.tail(2)))
    print()
    comparar(final, 'pipeline')


JEITOS = {'ia': jeito_ia, 'limpeza': jeito_limpeza, 'regra': jeito_regra, 'imputacao': jeito_imputacao,
          'ordem': jeito_ordem, 'certo': jeito_certo, 'gerente': jeito_gerente}

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='A receita do semestre da Loja Exemplo.')
    ap.add_argument('--jeito', choices=list(JEITOS), required=True)
    JEITOS[ap.parse_args().jeito]()
