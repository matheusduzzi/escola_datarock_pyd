"""As respostas do formulário de inscrição de 2026, convertidas de cinco jeitos.

    python3 tipos.py --jeito ia          o código que a IA passou
    python3 tipos.py --jeito numeros     o valor pago
    python3 tipos.py --jeito datas       a data de nascimento
    python3 tipos.py --jeito categorias  a categoria
    python3 tipos.py --jeito certo       as três colunas, com o relatório de conversões e rejeições

Rode python3 gerar.py antes, para ter os arquivos de entrada.
"""
import argparse
import sys
import warnings

import pandas as pd

import checar_conversao
import conversao

PROVA = pd.Timestamp('2026-05-24')
FAIXAS = ['18-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65+']
CATEGORIAS = [s + f for s in 'FM' for f in FAIXAS]
PRECOS = [980, 1150]
FORMATOS = ['%d/%m/%Y', '%Y-%m-%d']
# Quem corre a prova de 2026 tem de 18 a 100 anos no dia da prova.
NASC_MIN, NASC_MAX = '1926-05-25', '2008-05-24'
TIPOS = {'nascimento': 'datetime64[ns]', 'categoria': 'category', 'valor_pago': 'Float64'}


def reais(valor):
    return 'R$ ' + f'{valor:,.2f}'.replace(',', 'x').replace('.', ',').replace('x', '.')


def ler():
    return pd.read_csv('formulario_2026.csv', dtype=str, keep_default_na=False)


def extrato():
    return pd.read_csv('extrato_tesouraria.csv', dtype={'id_resposta': str})


def jeito_ia():
    f = pd.read_csv('formulario_2026.csv')
    with warnings.catch_warnings(record=True) as avisos:
        warnings.simplefilter('always')
        f['nascimento'] = pd.to_datetime(f['nascimento'], errors='coerce')
        f['valor_pago'] = pd.to_numeric(f['valor_pago'].str.replace('R$', '').str.replace(',', '.'),
                                        errors='coerce')
        f['categoria'] = f['categoria'].astype(pd.CategoricalDtype(CATEGORIAS))
        f = f.dropna()
    print(f'o código da IA rodou sem erro ({len(avisos)} aviso)')
    print(f'formulario_2026.csv: 480 respostas | depois do dropna: {len(f)}')
    print(f'total pago na conta da IA: {reais(f["valor_pago"].sum())}')
    e = extrato()
    print(f'extrato da tesouraria: {len(e)} pagamentos, {reais(e["valor"].sum())}')
    junto = f.assign(id_resposta=f['id_resposta'].astype(str)).merge(e, on='id_resposta', how='left')
    print(f'das {len(f)} respostas que sobraram, valor igual ao extrato: {(junto["valor_pago"] == junto["valor"]).sum()}')
    print('\naviso do to_datetime:', str(avisos[0].message) if avisos else '(nenhum)')


def jeito_numeros():
    f = ler()
    print('jeitos de escrever o valor_pago (cada dígito vira 9):')
    print(conversao.forma(f['valor_pago']).value_counts().to_string())
    try:
        pd.to_numeric(f['valor_pago'])
    except ValueError as e:
        print(f'\nto_numeric sem errors: ValueError: {e}')
    ia = pd.to_numeric(f['valor_pago'].str.replace('R$', '').str.replace(',', '.'), errors='coerce')
    print("\ncom replace e errors='coerce', como a IA fez:")
    for texto in ['1.150', '1.150,00', 'R$ 980,00', '1150.00', 'isento']:
        print(f'  {texto!r:14} -> {ia[f["valor_pago"] == texto].iloc[0]}')
    print(f'  viraram 1.15: {(ia == 1.15).sum()} | viraram NaN: {ia.isna().sum()} (vazias no arquivo: {(f["valor_pago"] == "").sum()})')
    valores, motivo = conversao.numero_br(f['valor_pago'], permitidos=PRECOS)
    print('\ncom conversao.numero_br e a tabela de preços (980 ou 1150):')
    print(f'  convertidos: {valores.notna().sum()} | vazios no arquivo: {conversao.texto(f["valor_pago"]).isna().sum()}'
          f' | rejeitados: {motivo.notna().sum()}')
    for (m, t), n in pd.DataFrame({'m': motivo, 't': f['valor_pago']}).dropna().value_counts().sort_index().items():
        print(f'  {m}: {t!r} ({n})')
    e = extrato().set_index('id_resposta')['valor']
    v = pd.Series(valores.to_numpy(), index=f['id_resposta'])
    v = v[v.notna()]
    print(f'  convertidos iguais ao extrato: {(v == e.reindex(v.index)).sum()} de {len(v)}')


def jeito_datas():
    f = ler()
    print('jeitos de escrever o nascimento, por canal (cada dígito vira 9):')
    print(pd.crosstab(conversao.forma(f['nascimento']), f['canal']).to_string())
    with warnings.catch_warnings(record=True) as avisos:
        warnings.simplefilter('always')
        sem = pd.to_datetime(f['nascimento'].replace('', None), errors='coerce')
    print(f"\nto_datetime com errors='coerce' e sem format: {sem.isna().sum()} NaT"
          f" (vazias no arquivo: {(f['nascimento'] == '').sum()})")
    print('  NaT por canal:', sem.isna().groupby(f['canal']).sum().to_dict())
    print('  aviso:', str(avisos[0].message) if avisos else '(nenhum)')
    valores, motivo = conversao.data(f['nascimento'], FORMATOS)
    print(f"\ncom os formatos {FORMATOS}, sem faixa:")
    print(f'  convertidas: {valores.notna().sum()} | rejeitadas: {motivo.notna().sum()}')
    for (m, t), n in pd.DataFrame({'m': motivo, 't': f['nascimento']}).dropna().value_counts().sort_index().items():
        print(f'  {m}: {t!r}' + (f' ({n})' if n > 1 else ''))
    print(f'  5/3/1984 com %d/%m/%Y: {pd.to_datetime("5/3/1984", format="%d/%m/%Y").date()}')
    idade = (PROVA.year - valores.dt.year)
    print(f'  menor e maior ano: {valores.dt.year.min():.0f} e {valores.dt.year.max():.0f}'
          f' | idade na prova abaixo de 18: {(idade < 18).sum()} | acima de 100: {(idade > 100).sum()}')
    valores, motivo = conversao.data(f['nascimento'], FORMATOS, NASC_MIN, NASC_MAX)
    print(f'\ncom a faixa de {NASC_MIN} a {NASC_MAX} (18 a 100 anos no dia da prova):')
    print(f'  convertidas: {valores.notna().sum()} | rejeitadas: {motivo.notna().sum()} | '
          + ', '.join(f'{k} {v}' for k, v in motivo.value_counts().sort_index().items()))


def jeito_categorias():
    f = ler()
    direto = f['categoria'].astype(pd.CategoricalDtype(CATEGORIAS))
    vazias = (f['categoria'] == '').sum()
    print(f'astype com as {len(CATEGORIAS)} categorias: {direto.isna().sum()} NaN, sem erro (vazias no arquivo: {vazias})')
    perdidas = f.loc[direto.isna() & (f['categoria'] != ''), 'categoria']
    print('  o que virou NaN:', ', '.join(f'{t!r} ({n})' if n > 1 else repr(t)
                                         for t, n in perdidas.value_counts().sort_index().items()))
    valores, motivo, ajustes = conversao.categoria(f['categoria'], CATEGORIAS)
    print('\ncom conversao.categoria (tira espaços e põe em maiúscula antes de comparar):')
    print(f'  convertidas: {valores.notna().sum()}, {ajustes} delas só depois do ajuste | rejeitadas: {motivo.notna().sum()}')
    print('  rejeitadas:', ', '.join(f'{t!r} ({n})' for t, n in f.loc[motivo.notna(), 'categoria'].value_counts().items()))
    print(f'  tipo: {valores.dtype} | categorias na lista: {len(valores.cat.categories)}')


def converter(f):
    nasc, m_nasc = conversao.data(f['nascimento'], FORMATOS, NASC_MIN, NASC_MAX)
    cat, m_cat, ajustes = conversao.categoria(f['categoria'], CATEGORIAS)
    valor, m_valor = conversao.numero_br(f['valor_pago'], permitidos=PRECOS)
    convertida = pd.DataFrame({'id_resposta': f['id_resposta'], 'canal': f['canal'],
                               'nascimento': nasc, 'categoria': cat, 'valor_pago': valor})
    rej = conversao.rejeicoes(f['id_resposta'], f, {'nascimento': m_nasc, 'categoria': m_cat, 'valor_pago': m_valor})
    rel = conversao.relatorio(f, convertida, rej, list(TIPOS), {'categoria': ajustes})
    return convertida, rej, rel


def jeito_certo():
    f = ler()
    convertida, rej, rel = converter(f)
    rel.to_csv('conversoes.csv', index=False)
    rej.to_csv('rejeicoes.csv', index=False)
    print(f'conversoes.csv: {len(rel)} linhas | rejeicoes.csv: {len(rej)} linhas')
    print(rel.to_string(index=False))
    print('\nrejeições por motivo:')
    print(rej.groupby(['coluna', 'motivo']).size().to_string())
    print('\nas primeiras linhas de rejeicoes.csv:')
    print(rej.head(5).to_string(index=False))
    problemas = checar_conversao.checar(f, convertida, rej, 'id_resposta', TIPOS)
    print('\nchecar_conversao:', 'ok' if not problemas else '; '.join(problemas))

    e = extrato().set_index('id_resposta')['valor']
    v = convertida.set_index('id_resposta')['valor_pago']
    ok = v[v.notna()]
    print(f'\nvalor convertido: {len(ok)} respostas, {reais(ok.sum())} | iguais ao extrato: {(ok == e.reindex(ok.index)).sum()}')
    sem = v[v.isna()].index
    no_extrato = e.reindex(sem).dropna()
    print(f'sem valor convertido: {len(sem)} respostas | {len(no_extrato)} delas têm pagamento no extrato: {reais(no_extrato.sum())}')
    print(f'{reais(ok.sum())} + {reais(no_extrato.sum())} = {reais(ok.sum() + no_extrato.sum())} | extrato: {reais(e.sum())}')
    print(f'\ninscrições: {len(convertida)} | com categoria: {convertida["categoria"].notna().sum()}'
          f' | sem categoria aceita: {convertida["categoria"].isna().sum()}')
    sys.exit(1 if problemas else 0)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--jeito', required=True, choices=['ia', 'numeros', 'datas', 'categorias', 'certo'])
    jeito = p.parse_args().jeito
    {'ia': jeito_ia, 'numeros': jeito_numeros, 'datas': jeito_datas, 'categorias': jeito_categorias,
     'certo': jeito_certo}[jeito]()
