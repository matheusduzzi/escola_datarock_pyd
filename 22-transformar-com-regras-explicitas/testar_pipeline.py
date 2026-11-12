"""Pedido 2 da prática guiada: estraga as etapas da loja e vê se o pipeline.rodar acusa.

Rode de dentro da pasta da aula, depois do gerar.py:

    python3 testar_pipeline.py

Cada caso diz o que se espera: "passa" ou "para". Sai com 1 se algum caso responder diferente.
"""
import sys

import pandas as pd

import loja
from pipeline import Etapa, ErroDeEtapa, rodar

E = loja.ETAPAS
LIMPAR, TIRAR, REGRA, IMPUTAR = E


def com(etapa, **mudancas):
    d = dict(tipo=etapa.tipo, nome=etapa.nome, funcao=etapa.funcao, muda=etapa.muda, motivo=etapa.motivo)
    d.update(mudancas)
    return Etapa(**d)


def imputar_e_tirar(p):
    return loja.preencher_valor(p).dropna(subset=['valor']).iloc[:-1]


def imputar_sem_marcar(p):
    return loja.preencher_valor(p).drop(columns='valor_preenchido')


def imputar_arredondando(p):
    p = loja.preencher_valor(p)
    p['valor'] = p['valor'].round(0)
    return p


def regra_e_preencher(p):
    p = loja.so_entregue(p)
    p['valor'] = p['valor'].fillna(0)
    return p


def filtrar_e_reindexar(p):
    return loja.so_entregue(p).reset_index(drop=True)


def repetir_linhas(p):
    return pd.concat([p, p.tail(3).rename(index=lambda i: i + 100000)])


CASOS = [
    ('as quatro etapas da aula', E, 'passa'),
    ('limpeza que troca o vazio por 0', [LIMPAR, TIRAR, REGRA,
     Etapa('limpeza', 'vazio vira 0', lambda p: p.assign(valor=p['valor'].fillna(0)), muda=('valor',))], 'para'),
    ('regra sem motivo', [LIMPAR, TIRAR, com(REGRA, motivo='')], 'para'),
    ('regra que também preenche o valor, sem declarar', [LIMPAR, TIRAR, com(REGRA, funcao=regra_e_preencher)], 'para'),
    ('regra que refaz o índice', [LIMPAR, TIRAR, com(REGRA, funcao=filtrar_e_reindexar)], 'para'),
    ('imputação que tira linhas', [LIMPAR, TIRAR, REGRA, com(IMPUTAR, funcao=imputar_e_tirar)], 'para'),
    ('imputação sem a coluna de marca', [LIMPAR, TIRAR, REGRA, com(IMPUTAR, funcao=imputar_sem_marcar)], 'para'),
    ('imputação que arredonda os valores que já existiam',
     [LIMPAR, TIRAR, REGRA, com(IMPUTAR, funcao=imputar_arredondando)], 'para'),
    ('imputação antes de tirar as repetidas', [LIMPAR, IMPUTAR, TIRAR, REGRA], 'passa'),
    ('etapa que cria linhas', [LIMPAR, Etapa('limpeza', 'repetir', repetir_linhas), TIRAR, REGRA, IMPUTAR], 'para'),
    ('tipo que não existe', [com(LIMPAR, tipo='ajuste')], 'para'),
]

if __name__ == '__main__':
    p = loja.ler()
    errados = 0
    for nome, etapas, esperado in CASOS:
        try:
            final, contagens = rodar(p, etapas, acompanhar=['valor'])
            obtido = 'passa'
            detalhe = f'{len(final)} linhas, {int(final["valor_preenchido"].sum())} preenchidos'
        except ErroDeEtapa as e:
            obtido, detalhe = 'para', str(e)
        if obtido != esperado:
            errados += 1
        print(f'{"ok " if obtido == esperado else "ERRADO"} {nome}: {obtido} | {detalhe}')
    print(f'\n{errados} caso(s) com resposta errada')
    sys.exit(1 if errados else 0)
