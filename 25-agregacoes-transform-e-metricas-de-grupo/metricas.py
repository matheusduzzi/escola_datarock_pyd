"""Métricas de grupo do triatlo, cada uma no grão que o pedido precisa, e a conferência num exemplo pequeno.

Uso, de dentro da pasta da aula:
    python3 metricas.py --passo caio      # a versão do Caio: a coluna vazia e a mediana com as duas edições
    python3 metricas.py --passo tabela    # uma linha por edição e categoria (agg)
    python3 metricas.py --passo atleta    # uma linha por atleta que concluiu, com números do grupo (transform e rank)
    python3 metricas.py --passo podio     # só as linhas das categorias com gente suficiente (filter)
    python3 metricas.py --passo taxa      # a taxa de conclusão de cada edição, do jeito certo e dos jeitos errados
    python3 metricas.py --passo exemplo   # as mesmas funções no exemplo pequeno, contra as respostas feitas à mão

No exercício, use as funções no Python:
    from metricas import *
    base = carregar_base()

Lê ../dados/triatlo (inscrições e resultados da API) e exemplo/.
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
DADOS = AQUI.parent / 'dados' / 'triatlo'
EXEMPLO = AQUI / 'exemplo'
ARQUIVOS = ['inscricoes_2024.csv', 'inscricoes_2025.csv', 'api_resultados.json']
CHAVE = ['edicao', 'id_inscricao']
GRUPO = ['edicao', 'categoria']
LARGOU = ['concluiu', 'DNF', 'DSQ']


class MetricaNaoBate(Exception):
    """Uma conta de grupo não bateu com a base ou com o exemplo feito à mão."""


def parar(mensagem):
    print(mensagem)
    print('Rode de dentro da pasta da aula, no kit do curso.')
    sys.exit(2)


def hms(segundos):
    """Segundos viram H:MM:SS, com sinal quando pedido por dif(); vazio vira '-'."""
    if pd.isna(segundos):
        return '-'
    s = int(round(float(segundos)))
    h, resto = divmod(abs(s), 3600)
    m, s2 = divmod(resto, 60)
    return f"{'-' if s < 0 else ''}{h}:{m:02d}:{s2:02d}"


def dif(segundos):
    """Diferença com sinal: +0:13:50 acima, -0:16:33 abaixo."""
    texto = hms(segundos)
    return texto if texto.startswith('-') or texto == '-' else '+' + texto


def pct(fracao):
    """0.8911 vira 89,1%."""
    return '-' if pd.isna(fracao) else f'{100 * fracao:.1f}%'.replace('.', ',')


def preparar(tabela):
    """Acrescenta tempo_s (segundos, vazio quando não há tempo), largou, concluiu e sem_resultado."""
    t = tabela.copy()
    t['tempo_s'] = pd.to_timedelta(t['tempo_oficial']).dt.total_seconds().astype('Int64')
    t['largou'] = t['status'].isin(LARGOU)
    t['concluiu'] = t['status'].eq('concluiu')
    t['sem_resultado'] = t['status'].isna()
    return t


def carregar_base():
    """Uma linha por inscrição das duas edições, com o resultado da API (left, one_to_one) e as colunas de preparar()."""
    faltando = [n for n in ARQUIVOS if not (DADOS / n).is_file()]
    if faltando:
        parar(f'arquivo não encontrado: {DADOS / faltando[0]}')
    partes = []
    for edicao, sep in ((2024, ','), (2025, ';')):
        t = pd.read_csv(DADOS / f'inscricoes_{edicao}.csv', sep=sep, dtype={'id_inscricao': str, 'equipe': str})
        partes.append(t.assign(edicao=edicao))
    inscricoes = pd.concat(partes, ignore_index=True).drop_duplicates()
    brutos = json.loads((DADOS / 'api_resultados.json').read_text(encoding='utf-8'))
    api = pd.DataFrame([{c: r[c] for c in CHAVE + ['status', 'tempo_oficial']} for r in brutos]).drop_duplicates()
    base = inscricoes.merge(api, on=CHAVE, how='left', validate='one_to_one')
    return preparar(base)


def ler_exemplo():
    """O exemplo pequeno: 8 inscrições que dá para contar de cabeça."""
    arquivo = EXEMPLO / 'resultados.csv'
    if not arquivo.is_file():
        parar(f'arquivo não encontrado: {arquivo}')
    return preparar(pd.read_csv(arquivo, dtype={'id_inscricao': str, 'tempo_oficial': str}))


def tabela(base, chave=GRUPO):
    """Uma linha por grupo: inscritos, largaram, concluíram, sem resultado, taxa e mediana do tempo de quem concluiu.

    Para se alguma coluna da chave tiver valor vazio: o groupby tiraria essas linhas sem avisar.
    Dê um nome ao vazio antes (por exemplo, 'sem equipe'). Para também se a soma dos inscritos não for o total.
    """
    vazios = {c: int(base[c].isna().sum()) for c in chave if base[c].isna().any()}
    if vazios:
        raise MetricaNaoBate('chave com valor vazio, o groupby tiraria essas linhas: '
                             + ', '.join(f'{c} vazia em {n} linhas' for c, n in vazios.items()))
    t = (base.groupby(chave)
         .agg(inscritos=('id_inscricao', 'size'), largaram=('largou', 'sum'), concluiram=('concluiu', 'sum'),
              sem_resultado=('sem_resultado', 'sum'), mediana_s=('tempo_s', 'median'))
         .reset_index())
    t['taxa'] = t['concluiram'] / t['largaram']
    if t['inscritos'].sum() != len(base):
        raise MetricaNaoBate(f'inscritos somados nos grupos: {t["inscritos"].sum()} | linhas da base: {len(base)}')
    return t


def por_atleta(base, chave=GRUPO):
    """Uma linha por atleta que concluiu, com a posição no grupo e a diferença para a mediana do grupo.

    Para se algum atleta concluiu sem tempo, ou se alguma linha ficar sem a mediana do grupo.
    """
    c = base[base['concluiu']].copy()
    sem_tempo = int(c['tempo_s'].isna().sum())
    if sem_tempo:
        raise MetricaNaoBate(f'atletas com status concluiu e sem tempo: {sem_tempo}')
    grupo = c.groupby(chave)['tempo_s']
    c['posicao'] = grupo.rank(method='min').astype(int)
    c['mediana_grupo_s'] = grupo.transform('median')
    c['dif_s'] = c['tempo_s'] - c['mediana_grupo_s']
    vazias = int(c['mediana_grupo_s'].isna().sum())
    if vazias:
        raise MetricaNaoBate(f'linhas sem a mediana do grupo: {vazias}')
    return c


def podio(atletas, chave=GRUPO, minimo=3, lugares=3):
    """Só as categorias com pelo menos `minimo` atletas que concluíram, e nelas só as `lugares` primeiras posições."""
    com_gente = atletas.groupby(chave).filter(lambda g: len(g) >= minimo)
    return com_gente[com_gente['posicao'] <= lugares].sort_values(chave + ['posicao'])


def taxa_geral(tab, nivel='edicao'):
    """A taxa de cada edição pelas contas somadas, ao lado da média das taxas dos grupos e da taxa por inscritos."""
    s = tab.groupby(nivel).agg(inscritos=('inscritos', 'sum'), largaram=('largaram', 'sum'),
                               concluiram=('concluiram', 'sum'), grupos=('taxa', 'size'),
                               media_das_taxas=('taxa', 'mean'))
    s['taxa'] = s['concluiram'] / s['largaram']
    s['por_inscritos'] = s['concluiram'] / s['inscritos']
    return s


def fmt_tabela(t):
    return pd.DataFrame({'edicao': t['edicao'], 'categoria': t['categoria'], 'inscritos': t['inscritos'],
                         'largaram': t['largaram'], 'concluiram': t['concluiram'],
                         'taxa': t['taxa'].map(pct), 'mediana': t['mediana_s'].map(hms)})


def fmt_atletas(c, extra=()):
    return pd.DataFrame({'edicao': c['edicao'], 'categoria': c['categoria'], 'id_inscricao': c['id_inscricao'],
                         'tempo': c['tempo_s'].map(hms), 'posicao': c['posicao'],
                         'mediana': c['mediana_grupo_s'].map(hms), 'diferenca': c['dif_s'].map(dif),
                         **{k: v for k, v in extra}})


def passo_caio(base):
    c = base[base['concluiu']].copy()
    print(f'A versão do Caio, com quem concluiu nas duas edições: {len(c)} linhas.\n')
    print("1) c['mediana_categoria'] = c.groupby('categoria')['tempo_s'].median()")
    c['mediana_categoria'] = c.groupby('categoria')['tempo_s'].median()
    print(f"   linhas com a coluna vazia: {int(c['mediana_categoria'].isna().sum())} de {len(c)}\n")
    print("2) c['mediana_categoria'] = c.groupby('categoria')['tempo_s'].transform('median')")
    c['mediana_categoria'] = c.groupby('categoria')['tempo_s'].transform('median')
    print(f"   linhas com a coluna vazia: {int(c['mediana_categoria'].isna().sum())} de {len(c)}")
    a = c[c['id_inscricao'] == '2025-0001'].iloc[0]
    print(f"   2025-0001 ({a['categoria']}, {hms(a['tempo_s'])}): mediana {hms(a['mediana_categoria'])}"
          f" | diferença {dif(a['tempo_s'] - a['mediana_categoria'])}\n")
    t25 = tabela(base[base['edicao'] == 2025], ['categoria'])
    print(f"3) taxa de conclusão de 2025 = média das taxas das {len(t25)} categorias: {pct(t25['taxa'].mean())}")


def passo_tabela(base):
    t = tabela(base)
    print(f"tabela: {len(t)} linhas, uma por edição e categoria | inscritos somados: {t['inscritos'].sum()}"
          f" | linhas da base: {len(base)}\n")
    print(fmt_tabela(t[t['edicao'] == 2025]).to_string(index=False))


def passo_atleta(base):
    c = por_atleta(base)
    print(f"por atleta: {len(c)} linhas, uma por atleta que concluiu | concluíram na base: {int(base['concluiu'].sum())}"
          f" | sem a mediana do grupo: {int(c['mediana_grupo_s'].isna().sum())}\n")
    m = c[(c['edicao'] == 2025) & (c['categoria'] == 'M45-49')].sort_values('posicao')
    mostrar = pd.concat([m.head(3), m[m['id_inscricao'] == '2025-0001']])
    print(fmt_atletas(mostrar).to_string(index=False))
    juntas = base[base['concluiu'] & base['categoria'].eq('M45-49')]['tempo_s'].median()
    print(f"\nmediana de M45-49 em 2025: {hms(m['tempo_s'].median())} | com as duas edições juntas: {hms(juntas)}")
    print(f"atletas de M45-49 em 2025: {len(m)} | acima da mediana: {int((m['dif_s'] > 0).sum())}"
          f" | abaixo: {int((m['dif_s'] < 0).sum())} | na mediana: {int((m['dif_s'] == 0).sum())}")


def passo_podio(base):
    c = por_atleta(base)
    por_grupo = c.groupby(GRUPO).size()
    fora = por_grupo[por_grupo < 3]
    p = podio(c)
    print(f"categorias com pelo menos 3 que concluíram: {int((por_grupo >= 3).sum())} de {len(por_grupo)}")
    for (edicao, categoria), n in fora.items():
        print(f"  fora do pódio: {edicao} {categoria} ({n} concluíram)")
    print(f"pódio: {len(p)} linhas | categorias no pódio: {p.groupby(GRUPO).ngroups}\n")
    print(fmt_atletas(p[(p['edicao'] == 2024) & p['categoria'].isin(['F60-64', 'M65+'])]).to_string(index=False))


def passo_taxa(base):
    s = taxa_geral(tabela(base))
    print('taxa de conclusão de cada edição\n')
    print(pd.DataFrame({'inscritos': s['inscritos'], 'largaram': s['largaram'], 'concluiram': s['concluiram'],
                        'concluiram/largaram': s['taxa'].map(pct),
                        'media_das_taxas': s['media_das_taxas'].map(pct),
                        'concluiram/inscritos': s['por_inscritos'].map(pct)}).to_string())
    t = tabela(base)
    pequenas = t[(t['edicao'] == 2025)].nsmallest(3, 'largaram')
    print('\nas 3 categorias de 2025 com menos gente que largou:')
    print(fmt_tabela(pequenas).to_string(index=False))


def conferir_exemplo():
    """Roda tabela(), por_atleta(), podio() e taxa_geral() no exemplo e compara com as respostas feitas à mão."""
    ex = ler_exemplo()
    esperado_t = pd.read_csv(EXEMPLO / 'esperado_tabela.csv', dtype={'mediana': str})
    esperado_a = pd.read_csv(EXEMPLO / 'esperado_atletas.csv', dtype={'id_inscricao': str, 'diferenca': str})
    t = tabela(ex)
    feito_t = pd.DataFrame({'edicao': t['edicao'], 'categoria': t['categoria'], 'inscritos': t['inscritos'],
                            'largaram': t['largaram'], 'concluiram': t['concluiram'],
                            'taxa': t['taxa'].round(4), 'mediana': t['mediana_s'].map(hms)})
    a = por_atleta(ex)
    feito_a = pd.DataFrame({'id_inscricao': a['id_inscricao'], 'posicao': a['posicao'],
                            'diferenca': a['dif_s'].map(dif)}).sort_values('id_inscricao').reset_index(drop=True)
    esperado_a = esperado_a.sort_values('id_inscricao').reset_index(drop=True)
    p = podio(a)
    s = taxa_geral(t)
    contas = [
        ('tabela', feito_t.equals(esperado_t[feito_t.columns]) if list(esperado_t.columns) == list(feito_t.columns) else False),
        ('por atleta', feito_a.equals(esperado_a[feito_a.columns]) if list(esperado_a.columns) == list(feito_a.columns) else False),
        ('pódio: só 2025 F40-44, com e1, e2 e e3', sorted(p['id_inscricao']) == ['e1', 'e2', 'e3']),
        ('taxa de 2025: 5 de 6 que largaram', round(float(s.loc[2025, 'taxa']), 4) == round(5 / 6, 4)),
    ]
    return t, a, p, s, contas


def passo_exemplo(_base=None):
    t, a, p, s, contas = conferir_exemplo()
    print('o exemplo pequeno, com as mesmas funções\n')
    print(fmt_tabela(t).to_string(index=False))
    print()
    print(fmt_atletas(a.sort_values(GRUPO + ['posicao'])).to_string(index=False))
    print(f"\npódio (pelo menos 3 que concluíram): {', '.join(p['id_inscricao'])}")
    print(f"taxa de 2025: {int(s.loc[2025, 'concluiram'])} de {int(s.loc[2025, 'largaram'])} = {pct(s.loc[2025, 'taxa'])}"
          f" | média das taxas: {pct(s.loc[2025, 'media_das_taxas'])}\n")
    for nome, bate in contas:
        print(f"  {nome}: {'bate com a conta à mão' if bate else 'NÃO BATE'}")
    if not all(b for _, b in contas):
        print('\nAlguma conta do exemplo não bateu. Veja a função antes de rodar na base.')
        sys.exit(1)


PASSOS = {'caio': passo_caio, 'tabela': passo_tabela, 'atleta': passo_atleta, 'podio': passo_podio,
          'taxa': passo_taxa, 'exemplo': passo_exemplo}


def main():
    p = argparse.ArgumentParser(description='Métricas de grupo do triatlo, no grão certo.')
    p.add_argument('--passo', required=True, choices=list(PASSOS))
    passo = p.parse_args().passo
    base = None if passo == 'exemplo' else carregar_base()
    try:
        PASSOS[passo](base)
    except MetricaNaoBate as erro:
        print(f'\nA conta não bateu: {erro}')
        sys.exit(1)


if __name__ == '__main__':
    main()
