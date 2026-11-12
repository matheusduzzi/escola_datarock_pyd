"""Estraga a conversão do formulário de dez jeitos e vê se o checar_conversao acusa cada um.

    python3 testar_checar.py

Sai com 1 se o checar_conversao responder errado em algum caso.
"""
import sys

import pandas as pd

import checar_conversao
import tipos


def casos():
    f = tipos.ler()
    conv, rej, _ = tipos.converter(f)
    rv = rej['coluna'] == 'valor_pago'
    vazio_val = f.index[f['valor_pago'] == ''][0]
    vazio_nasc = f.index[f['nascimento'] == ''][0]
    yield 'a conversão certa', f, conv, rej, True

    com_rej = f['id_resposta'].isin(rej['id_resposta'])
    yield 'dropna nas respostas com rejeição', f, conv[~com_rej.to_numpy()].reset_index(drop=True), rej, False

    yield "errors='coerce' sem registro no valor_pago", f, conv, rej[~rv].reset_index(drop=True), False

    r = rej.copy()
    r.loc[r.index[0], 'motivo'] = ''
    yield 'uma rejeição sem motivo', f, conv, r, False

    extra = pd.DataFrame([{'id_resposta': f.loc[vazio_val, 'id_resposta'], 'coluna': 'valor_pago',
                           'valor_original': '', 'motivo': 'vazio'}])
    yield 'a célula vazia registrada como rejeição', f, conv, pd.concat([rej, extra], ignore_index=True), False

    c = conv.copy()
    i = f.index[f['valor_pago'] == '98,00'][0]
    c.loc[i, 'valor_pago'] = 98.0
    yield 'o 98,00 rejeitado e mantido na tabela', f, c, rej, False

    c = conv.copy()
    c['valor_pago'] = c['valor_pago'].astype('float64')
    yield 'valor_pago em float64', f, c, rej, False

    r = rej.copy()
    rc = r['coluna'] == 'categoria'
    r.loc[rc, 'valor_original'] = r.loc[rc, 'valor_original'].str.upper()
    yield 'valor_original já ajustado (ELITE no lugar de Elite)', f, conv, r, False

    yield 'as respostas fora de ordem', f, conv.sort_values('categoria').reset_index(drop=True), rej, False

    c = conv.copy()
    c.loc[vazio_val, 'valor_pago'] = 0.0
    c.loc[vazio_nasc, 'nascimento'] = pd.Timestamp('1990-01-01')
    yield 'o vazio preenchido com 0 e com uma data', f, c, rej, False

    yield 'a mesma rejeição duas vezes', f, conv, pd.concat([rej, rej.iloc[:1]], ignore_index=True), False


def main():
    erradas = 0
    for nome, f, conv, rej, esperado_ok in casos():
        problemas = checar_conversao.checar(f, conv, rej, 'id_resposta', tipos.TIPOS)
        disse_ok = not problemas
        acertou = disse_ok == esperado_ok
        erradas += not acertou
        print(f'{"certo " if acertou else "ERRADO"} {nome}: esperado {"ok" if esperado_ok else "problema"}, '
              f'checar disse: {"ok" if disse_ok else "; ".join(problemas)}')
    print(f'{erradas} caso(s) com resposta errada')
    sys.exit(1 if erradas else 0)


if __name__ == '__main__':
    main()
