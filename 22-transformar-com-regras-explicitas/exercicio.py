"""Exercício: as inscrições de 2026 do triatlo.

Escreva a função montar_etapas abaixo. Depois rode, de dentro desta pasta:

    python3 gerar.py
    python3 exercicio.py

Enquanto a função não estiver escrita, o programa para com o código 1.
Com a função escrita, ele roda as etapas pelo pipeline.rodar, grava contagens_inscricoes.csv
e mostra o resumo para a Lívia. Sai com 0 se todas as etapas passarem nas checagens do
pipeline.rodar, e com 1 se alguma parar.
"""
import sys

import pandas as pd

import pipeline
from pipeline import Etapa, ErroDeEtapa  # noqa: F401  (Etapa é o que a sua função monta)

ANO_PROVA = 2026
CADASTRO = '../dados/triatlo/atletas.csv'


def faixa(idade):
    """A faixa de idade da competição, pela idade no ano da prova: 18-24, 25-29, ..., 60-64, 65+."""
    idade = int(idade)
    if idade < 25:
        return '18-24'
    if idade >= 65:
        return '65+'
    base = idade // 5 * 5
    return f'{base}-{base + 4}'


def brl(x):
    texto = 'R$ ' + f'{abs(x):,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')
    return '-' + texto if x < 0 else texto


def ler():
    """A lista de inscrições como o sistema exportou, com o id do atleta e o ano como inteiros."""
    return pd.read_csv('inscricoes_2026.csv', dtype={'id_atleta': 'Int64', 'ano_nascimento': 'Int64'})


def cadastro():
    """O cadastro de atletas da competição: id_atleta, nome, sexo, ano_nascimento, uf."""
    return pd.read_csv(CADASTRO, dtype={'id_atleta': 'Int64', 'ano_nascimento': 'Int64'})


def montar_etapas():
    """Retorna a lista de Etapa, na ordem em que devem rodar.

    Cada Etapa tem o tipo (limpeza, regra ou imputação), um nome curto, a função que recebe
    a tabela e retorna a tabela nova, as colunas que ela muda e, nas regras e imputações,
    o motivo. Veja as etapas da loja no loja.py.
    """
    raise NotImplementedError('falta escrever montar_etapas')


def resumo(final):
    idade = ANO_PROVA - final['ano_nascimento']
    certa = final['sexo'] + idade.map(faixa, na_action='ignore')
    print(f'inscrições: {len(final)} | categoria vazia: {final["categoria"].isna().sum()} | '
          f'categoria diferente de sexo + faixa: {(final["categoria"] != certa).sum()}')
    pago = final['valor_pago']
    print(f'arrecadado: {brl(pago.sum())} | pagamentos: {(pago > 0).sum()} | '
          f'valor 0: {(pago == 0).sum()} | valor vazio: {pago.isna().sum()}')
    print('\ninscrições por categoria:')
    print(final['categoria'].value_counts(dropna=False).sort_index().to_string())


def main():
    try:
        etapas = montar_etapas()
    except NotImplementedError as e:
        print(e)
        sys.exit(1)
    tabela = ler()
    print(f'inscricoes_2026.csv: {len(tabela)} linhas')
    try:
        final, contagens = pipeline.rodar(tabela, etapas, acompanhar=['sexo', 'ano_nascimento', 'valor_pago'],
                                          medidas={'arrecadado': lambda t: brl(t['valor_pago'].sum())})
    except ErroDeEtapa as e:
        print('o pipeline parou:', e)
        sys.exit(1)
    contagens.to_csv('contagens_inscricoes.csv', index=False)
    print(pipeline.mostrar(contagens))
    print()
    resumo(final)


if __name__ == '__main__':
    main()
