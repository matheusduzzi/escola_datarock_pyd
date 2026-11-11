"""Compara a tabela de onde você saiu com a tabela que voltou. É a conferência de ida e volta.

Uso, dentro de um programa da pasta da aula:
    from conferir import ida_e_volta
    igual = ida_e_volta(original, volta, chave=['edicao', 'id_inscricao'])

A ordem das linhas e a ordem das colunas não contam: as duas tabelas são ordenadas pela chave
e as colunas da volta são postas na ordem do original antes de comparar. O resto conta:
quantidade de linhas, chave repetida, chaves que sumiram ou apareceram, colunas, tipos e cada
célula. Vazio no mesmo lugar nas duas é igual. Vazio de um lado e valor do outro é diferença.
Retorna True só se tudo bater.
"""
import pandas as pd


def ida_e_volta(original, volta, chave, mostrar=True):
    achados = []
    col_o, col_v = list(original.columns), list(volta.columns)
    if len(original) != len(volta):
        achados.append(f'linhas: {len(original)} no original, {len(volta)} na volta')
    faltam = [c for c in col_o if c not in col_v]
    sobram = [c for c in col_v if c not in col_o]
    if faltam:
        achados.append('colunas que sumiram: ' + ', '.join(map(str, faltam)))
    if sobram:
        achados.append('colunas que apareceram: ' + ', '.join(map(str, sobram)))
    sem_chave = [c for c in chave if c not in col_v]
    if sem_chave:
        achados.append('a volta não tem a chave: ' + ', '.join(sem_chave))
    else:
        for nome, tabela in [('original', original), ('volta', volta)]:
            rep = int(tabela.duplicated(subset=chave).sum())
            if rep:
                achados.append(f'chave repetida na tabela {nome}: {rep} linha{"s" if rep > 1 else ""} a mais')
        chaves_o = set(map(tuple, original[chave].astype(str).values))
        chaves_v = set(map(tuple, volta[chave].astype(str).values))
        so_o, so_v = sorted(chaves_o - chaves_v), sorted(chaves_v - chaves_o)
        if so_o:
            achados.append(f'chaves que sumiram na volta: {len(so_o)} (ex.: {" / ".join(so_o[0])})')
        if so_v:
            achados.append(f'chaves que apareceram na volta: {len(so_v)} (ex.: {" / ".join(so_v[0])})')
        comuns = [c for c in col_o if c in col_v]
        tipos = [f'{c} ({original[c].dtype} -> {volta[c].dtype})' for c in comuns
                 if original[c].dtype != volta[c].dtype]
        if tipos:
            achados.append('tipos diferentes: ' + ', '.join(tipos))
        if not so_o and not so_v and not any('chave repetida' in a for a in achados):
            a = original[comuns].sort_values(chave, kind='stable').reset_index(drop=True)
            b = volta[comuns].sort_values(chave, kind='stable').reset_index(drop=True)
            for c in comuns:
                va, vb = a[c].astype(object), b[c].astype(object)
                vazio_a, vazio_b = va.isna(), vb.isna()
                dif = (vazio_a != vazio_b) | (~vazio_a & ~vazio_b & (va.astype(str) != vb.astype(str)))
                if dif.any():
                    i = dif.idxmax()
                    ex = ' / '.join(str(a.at[i, k]) for k in chave)
                    achados.append(f'células diferentes em {c}: {int(dif.sum())} (ex.: {ex}: '
                                   f'{va[i] if not vazio_a[i] else "<NA>"} -> {vb[i] if not vazio_b[i] else "<NA>"})')
    if mostrar:
        print(f'conferência de ida e volta (chave: {" + ".join(chave)})')
        print(f'  original: {len(original)} linhas x {original.shape[1]} colunas | '
              f'volta: {len(volta)} linhas x {volta.shape[1]} colunas')
        for a in achados:
            print('  - ' + a)
        print('  resultado: ' + ('igual' if not achados else 'diferente'))
    return not achados


if __name__ == '__main__':
    print(__doc__)
