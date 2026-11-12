"""Mede as chaves de um merge antes de juntar: quantas vezes cada chave aparece e quantas têm par.

Uso, de dentro da pasta da aula:
    python3 medir.py --merge peito        # o merge do Caio, pelo número de peito
    python3 medir.py --merge resultados   # inscrições e resultados pela edição e pela inscrição
    python3 medir.py --merge validar      # o mesmo merge com validate, como os dados chegam e sem as cópias

No exercício, use as funções no Python:
    from medir import carregar, medir
    t = carregar()
    medir(t['inscricoes'], t['atletas'], 'id_atleta', 'inscricoes', 'atletas')

Lê ../dados/triatlo. As tabelas entram como chegam nos arquivos, com as linhas repetidas.
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
DADOS = AQUI.parent / 'dados' / 'triatlo'
ARQUIVOS = ['inscricoes_2024.csv', 'inscricoes_2025.csv', 'atletas.csv', 'edicoes.csv', 'api_resultados.json']
VALIDATE = {(True, True): 'one_to_one', (True, False): 'one_to_many',
            (False, True): 'many_to_one', (False, False): 'many_to_many'}


def carregar():
    """As tabelas do projeto, como chegam: inscricoes (as duas edições), resultados, atletas e edicoes."""
    faltando = [n for n in ARQUIVOS if not (DADOS / n).is_file()]
    if faltando:
        print(f'arquivo não encontrado: {DADOS / faltando[0]}')
        print('Rode de dentro da pasta da aula, no kit do curso.')
        sys.exit(2)
    partes = []
    for edicao, sep in ((2024, ','), (2025, ';')):
        tabela = pd.read_csv(DADOS / f'inscricoes_{edicao}.csv', sep=sep, dtype={'id_inscricao': str, 'equipe': str})
        partes.append(tabela.assign(edicao=edicao))
    inscricoes = pd.concat(partes, ignore_index=True)
    brutos = json.loads((DADOS / 'api_resultados.json').read_text(encoding='utf-8'))
    resultados = pd.DataFrame([{c: r[c] for c in ('edicao', 'id_inscricao', 'numero_peito', 'status', 'tempo_oficial')}
                               for r in brutos])
    return {'inscricoes': inscricoes, 'resultados': resultados,
            'atletas': pd.read_csv(DADOS / 'atletas.csv'), 'edicoes': pd.read_csv(DADOS / 'edicoes.csv')}


def lado(tabela, chave, nome):
    """Quantas linhas, quantas chaves diferentes e qual a maior repetição de uma chave."""
    contagem = tabela.groupby(chave).size()
    repetidas = int((contagem > 1).sum())
    print(f'{nome}: {len(tabela)} linhas | {len(contagem)} chaves diferentes | '
          f'maior repetição: {int(contagem.max())} | chaves repetidas: {repetidas}')
    return repetidas == 0


def cobertura(de, para, chave, nome_de, nome_para):
    """Quantas chaves diferentes de um lado aparecem do outro."""
    a = de[chave].drop_duplicates()
    b = para[chave].drop_duplicates()
    com_par = len(a.merge(b, on=chave))
    print(f'  {com_par} de {len(a)} chaves de {nome_de} têm par em {nome_para} ({len(a) - com_par} sem par)')


def medir(esq, dir, chave, nome_esq='esquerda', nome_dir='direita'):
    """Imprime, antes do merge, o que os dados mostram sobre a chave: repetição, cobertura e linhas."""
    chave = [chave] if isinstance(chave, str) else list(chave)
    print('chave:', ' + '.join(chave))
    unica_esq = lado(esq, chave, nome_esq)
    unica_dir = lado(dir, chave, nome_dir)
    print('cobertura:')
    cobertura(esq, dir, chave, nome_esq, nome_dir)
    cobertura(dir, esq, chave, nome_dir, nome_esq)
    validate = VALIDATE[(unica_esq, unica_dir)]
    print(f'o validate mais exigente que esses dados passam: {validate}')
    linhas = {how: len(esq[chave].merge(dir[chave], on=chave, how=how)) for how in ('inner', 'left', 'outer')}
    print(f'linhas depois do merge: inner {linhas["inner"]} | left {linhas["left"]} | outer {linhas["outer"]}')
    return validate


def peito(t):
    print('O merge do Caio: resultados com inscrições só pelo número de peito.\n')
    medir(t['resultados'], t['inscricoes'], 'numero_peito', 'resultados', 'inscricoes')
    juntos = t['resultados'].merge(t['inscricoes'], on='numero_peito')
    concluiu = juntos[(juntos['edicao_x'] == 2025) & (juntos['status'] == 'concluiu')]
    print(f'\ncolunas que vieram repetidas: {[c for c in juntos.columns if c.endswith(("_x", "_y"))]}')
    print(f'mulheres que concluíram em 2025, contadas nesse merge: {int(concluiu["categoria"].str.startswith("F").sum())}')
    peito_102 = juntos[juntos['numero_peito'] == 102][['edicao_x', 'id_inscricao_x', 'status', 'edicao_y',
                                                        'id_inscricao_y', 'id_atleta', 'categoria']]
    print('\no peito 102 depois do merge:')
    print(peito_102.to_string(index=False))


def resultados(t):
    print('Inscrições com resultados pela edição e pela inscrição.\n')
    medir(t['inscricoes'], t['resultados'], ['edicao', 'id_inscricao'], 'inscricoes', 'resultados')
    for nome in ('inscricoes', 'resultados'):
        tab = t[nome]
        copias = tab[tab.duplicated(['edicao', 'id_inscricao'], keep=False)]
        iguais = len(copias) == 0 or not tab.drop_duplicates().duplicated(['edicao', 'id_inscricao']).any()
        print(f'{nome}: linhas com chave repetida {len(copias)} | as cópias são iguais: {"sim" if iguais else "não"}')
    sem = t['inscricoes'].drop_duplicates()
    sem = sem[~sem.set_index(['edicao', 'id_inscricao']).index.isin(
        t['resultados'].set_index(['edicao', 'id_inscricao']).index)]
    print('inscrições sem resultado, por edição:', sem.groupby('edicao').size().to_dict())


def validar(t):
    chave = ['edicao', 'id_inscricao']
    for rotulo, ins, res in (('como chegam', t['inscricoes'], t['resultados']),
                             ('sem as cópias iguais', t['inscricoes'].drop_duplicates(), t['resultados'].drop_duplicates())):
        print(f'== {rotulo}: {len(ins)} inscrições, {len(res)} resultados')
        try:
            base = ins.merge(res, on=chave, how='left', validate='one_to_one')
        except pd.errors.MergeError as erro:
            print(f'MergeError: {erro}')
        else:
            print(f'passou: {len(base)} linhas | sem resultado: {int(base["status"].isna().sum())}')
            concluiu = base[(base['edicao'] == 2025) & (base['status'] == 'concluiu')]
            print(f'mulheres que concluíram em 2025: {int(concluiu["categoria"].str.startswith("F").sum())} '
                  f'de {len(concluiu)} que concluíram')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Mede as chaves de um merge do triatlo antes de juntar.')
    ap.add_argument('--merge', required=True, choices=['peito', 'resultados', 'validar'])
    escolha = ap.parse_args().merge
    {'peito': peito, 'resultados': resultados, 'validar': validar}[escolha](carregar())
