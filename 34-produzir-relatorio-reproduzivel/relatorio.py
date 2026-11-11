"""O relatório da prova, gerado inteiro pelo código. Aula «Produzir relatório reproduzível».

Rode de dentro da pasta da aula:
    python3 relatorio.py              grava a pasta relatorio/ do zero e imprime o que gravou
    python3 relatorio.py --numeros    imprime de onde vem cada número do texto

O relatório é um arquivo Markdown (relatorio.md) com as tabelas, as frases e os links para as
figuras, que ficam em relatorio/figuras/. Cada número das frases passa pelo registro (Registro.anota),
que guarda a conta e quem entra nela. A tabela de origem vai para o fim do relatório e para numeros.csv.
Se uma conta não fecha, o programa para com o código 1 e não grava nada: a pasta antiga fica como estava.
Os dados vêm de ../dados/triatlo. Parcial vazia fica vazia: nada vira zero.
Para usar no seu relatório: from relatorio import carregar, concluintes, Registro, tabela_md, salvar_figura
"""
import argparse
import csv
import hashlib
import io
import json
import math
import re
import shutil
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # desenha direto no arquivo, sem abrir janela
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

DADOS = Path('..') / 'dados' / 'triatlo'
SAIDA = Path('relatorio')
ARQUIVOS = ['edicoes.csv', 'atletas.csv', 'inscricoes_2024.csv', 'inscricoes_2025.csv', 'api_resultados.json']
ETAPAS = ['natacao', 't1', 'ciclismo', 't2', 'corrida']
LARGARAM = ['concluiu', 'DNF', 'DSQ']  # DNS e "sem resultado" não largaram
MUSGO, CINZA, OCRE = '#52645C', '#8C8C8C', '#B8742A'
DPI = 150
LIMIAR_MIN = 40  # regra do relatório: diferença de categoria que vai para o resumo
LIMIAR_N = 10    # regra do relatório: grupo com menos atletas que isso entra nos limites


class ContaNaoFecha(ValueError):
    """Os dados não passaram numa checagem: o relatório não é gravado."""


# ---------------------------------------------------------------- dados

def _segundos(texto):
    if texto is None:
        return pd.NA
    h, m, s = (int(p) for p in texto.split(':'))
    return h * 3600 + m * 60 + s


def carregar(dados=DADOS):
    """Uma linha por inscrição das duas edições, com o resultado da API quando existe.

    Para com ContaNaoFecha se a API tem resultado sem inscrição ou duas versões diferentes
    do mesmo resultado. Cópias idênticas (vistas na aula 26) são removidas.
    """
    dados = Path(dados)
    for nome in ARQUIVOS:
        if not (dados / nome).is_file():
            raise FileNotFoundError(f'arquivo não encontrado: {dados / nome}. '
                                    'Rode de dentro da pasta da aula, no kit do curso.')
    bruto = json.loads((dados / 'api_resultados.json').read_text(encoding='utf-8'))
    res = pd.DataFrame(bruto)
    res['_linha'] = [json.dumps(r, sort_keys=True, ensure_ascii=False) for r in bruto]
    res = res.drop_duplicates(subset='_linha').drop(columns='_linha')
    repetidos = res[res.duplicated(subset=['edicao', 'id_inscricao'], keep=False)]
    if len(repetidos):
        ids = ', '.join(sorted(repetidos.id_inscricao.unique()))
        raise ContaNaoFecha(f'{repetidos.id_inscricao.nunique()} resultado(s) com duas versões diferentes na API: {ids}')
    parciais = pd.json_normalize(res['parciais'].tolist())
    parciais.index = res.index
    for etapa in ETAPAS:
        res[etapa] = parciais[etapa].map(_segundos).astype('Int64')
    res['oficial'] = res['tempo_oficial'].map(_segundos).astype('Int64')

    insc = pd.concat([pd.read_csv(dados / 'inscricoes_2024.csv'),
                      pd.read_csv(dados / 'inscricoes_2025.csv', sep=';')]).drop_duplicates()
    insc['edicao'] = insc['id_inscricao'].str[:4].astype(int)
    chaves = set(zip(insc.edicao, insc.id_inscricao))
    orfaos = res[[(e, i) not in chaves for e, i in zip(res.edicao, res.id_inscricao)]]
    if len(orfaos):
        ids = ', '.join(f'{i} ({e})' for e, i in zip(orfaos.edicao, orfaos.id_inscricao))
        raise ContaNaoFecha(f'{len(orfaos)} resultado(s) da API sem inscrição: {ids}')

    atletas = pd.read_csv(dados / 'atletas.csv')
    t = insc.merge(atletas[['id_atleta', 'sexo', 'ano_nascimento']], on='id_atleta', how='left',
                   validate='many_to_one')
    t = t.merge(res[['edicao', 'id_inscricao', 'status', 'oficial'] + ETAPAS], on=['edicao', 'id_inscricao'],
                how='left', validate='one_to_one')
    t['status'] = t['status'].fillna('sem resultado')
    for etapa in ETAPAS:
        t[f'{etapa}_min'] = (t[etapa].astype('Float64') / 60).astype(float)
    t['oficial_h'] = (t['oficial'].astype('Float64') / 3600).astype(float)
    return t.drop(columns=ETAPAS + ['oficial'])


def carregar_edicoes(dados=DADOS):
    """edicoes.csv com a edição no índice: distâncias, data, temperatura e observação."""
    return pd.read_csv(Path(dados) / 'edicoes.csv').set_index('edicao')


def concluintes(t):
    return t[t.status == 'concluiu']


# ---------------------------------------------------------------- números e tabelas

def virgula(numero, casas=1):
    """85.4 -> '85,4': o texto do relatório é para quem lê em português."""
    return f'{numero:.{casas}f}'.replace('.', ',')


def formatar(valor, casas=1, unidade=''):
    texto = virgula(valor, casas)
    if unidade == '%':
        return texto + '%'
    return f'{texto} {unidade}' if unidade else texto


class Registro:
    """Os números do texto, cada um com a conta e com quem entra nela.

    anota() guarda o número e retorna o texto dele, pronto para a frase.
    r['nome'] retorna o mesmo texto de novo; nome que não foi anotado dá KeyError.
    """

    def __init__(self):
        self.linhas = []
        self._texto = {}

    def anota(self, nome, valor, conta, base, casas=1, unidade=''):
        if nome in self._texto:
            raise ValueError(f'número anotado duas vezes: {nome}')
        if pd.isna(valor) or not math.isfinite(float(valor)):
            raise ContaNaoFecha(f'o número {nome} ficou vazio ou infinito ({conta}): {valor}')
        texto = formatar(valor, casas, unidade)
        self._texto[nome] = texto
        self.linhas.append({'nome': nome, 'valor': texto, 'conta': conta, 'quem entra': base})
        return texto

    def __getitem__(self, nome):
        return self._texto[nome]

    def valores(self):
        """Só a parte numérica de cada texto anotado: '89,1%' -> '89,1'."""
        return {re.match(r'-?\d+(?:,\d+)?', t).group(0).lstrip('-') for t in self._texto.values()}

    def tabela(self):
        return pd.DataFrame(self.linhas, columns=['nome', 'valor', 'conta', 'quem entra'])


def tabela_md(df, casas=1):
    """Uma tabela do pandas em Markdown, com vírgula nos decimais. Não precisa do tabulate."""
    def celula(v):
        if isinstance(v, float):
            return '' if pd.isna(v) else virgula(v, casas)
        return str(v).replace('|', '\\|')
    linhas = ['| ' + ' | '.join(str(c) for c in df.columns) + ' |',
              '|' + '|'.join('---' for _ in df.columns) + '|']
    linhas += ['| ' + ' | '.join(celula(v) for v in linha) + ' |' for linha in df.itertuples(index=False)]
    return '\n'.join(linhas)


NUMERO = re.compile(r'(?<![\w,.\-+/])\d+(?:,\d+)?(?![\w])')
SECOES_LIVRES = ('## De onde vêm os números', '## Como gerar de novo')


def numeros_sem_origem(texto, registro, livres=()):
    """Números das frases do relatório que não estão no registro.

    Fica de fora: tabela (linha que começa com |), link de figura, título de seção e as duas
    seções do fim, que listam origem, versões e hashes. Os números em `livres` são aceitos
    (os anos das edições, por exemplo).
    """
    validos = registro.valores() | {str(x) for x in livres}
    faltam, livre = [], False
    for linha in texto.splitlines():
        if linha.startswith('## '):
            livre = linha.startswith(SECOES_LIVRES)
            continue
        if livre or linha.startswith(('|', '![', '#', '```')):
            continue
        faltam += [n for n in NUMERO.findall(linha) if n not in validos]
    return faltam


# ---------------------------------------------------------------- figuras

def salvar_figura(fig, caminho):
    """Grava o PNG e fecha a figura. O PNG do Matplotlib não leva a data em que foi gravado."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=DPI)
    plt.close(fig)
    return caminho


def figura_etapas(c, ed, r):
    etapas = ['natacao', 'ciclismo', 'corrida']
    nomes = {'natacao': 'natação', 'ciclismo': 'ciclismo', 'corrida': 'corrida'}
    fig, ax = plt.subplots(figsize=(8, 4.5), layout='constrained')
    for i, (edicao, cor) in enumerate([(2024, CINZA), (2025, MUSGO)]):
        e = c[c.edicao == edicao]
        med = [e[f'{etapa}_min'].median() for etapa in etapas]
        barras = ax.bar([p + (i - 0.5) * 0.38 for p in range(3)], med, width=0.38, color=cor,
                        label=f'{edicao} ({len(e)} concluíram)')
        ax.bar_label(barras, labels=[virgula(m, 0) for m in med], padding=2, fontsize=9)
    marcas = []
    for etapa in etapas:
        a, b = ed.loc[2024, f'{etapa}_km'], ed.loc[2025, f'{etapa}_km']
        dist = f'{virgula(a, 1 if a % 1 else 0)} km nas duas' if a == b else \
            f'{virgula(a, 1 if a % 1 else 0)} km em 2024, {virgula(b, 1 if b % 1 else 0)} km em 2025'
        marcas.append(f'{nomes[etapa]}\n{dist}')
    ax.set_xticks(range(3), marcas)
    ax.set_ylabel('Tempo mediano da etapa (minutos)')
    ax.set_ylim(0, 460)
    ax.legend(title='Edição', loc='upper left')
    ax.set_title(f'Em 2025, a corrida mediana ficou {r["dif_corrida"]} mais lenta', fontsize=12)
    return fig


def tabela_categorias(c):
    """Mediana da corrida por categoria e edição, com quantos concluíram, da menor piora para a maior."""
    m = c.groupby(['categoria', 'edicao']).corrida_min.agg(['median', 'count']).unstack('edicao')
    t = pd.DataFrame({'m2024': m[('median', 2024)], 'n2024': m[('count', 2024)],
                      'm2025': m[('median', 2025)], 'n2025': m[('count', 2025)]})
    t['dif'] = t.m2025 - t.m2024
    return t.sort_values('dif')


def figura_categorias(cat, r):
    fig, ax = plt.subplots(figsize=(8, 9), layout='constrained')
    y = list(range(len(cat)))
    forte = (cat.dif > LIMIAR_MIN).tolist()
    ax.hlines(y, cat.m2024, cat.m2025, color='#C8C8C8', linewidth=2)
    ax.scatter(cat.m2024, y, color=CINZA, s=40, label='2024', zorder=3)
    ax.scatter(cat.m2025[[not f for f in forte]], [i for i, f in zip(y, forte) if not f], color=MUSGO, s=40,
               label='2025', zorder=3)
    ax.scatter(cat.m2025[forte], [i for i, f in zip(y, forte) if f], color=OCRE, s=40,
               label=f'2025, mais de {LIMIAR_MIN} min acima de 2024', zorder=3)
    ax.set_yticks(y, [f'{k} ({a} e {b})' for k, a, b in zip(cat.index, cat.n2024, cat.n2025)], fontsize=10)
    ax.set_xlim(230, 345)
    for i, (dif, fim) in enumerate(zip(cat.dif, cat[['m2024', 'm2025']].max(axis=1))):
        ax.text(fim + 2, i, f'{"+" if dif >= 0 else "-"}{virgula(abs(dif))} min', va='center', fontsize=10)
    ax.set_xlabel('Corrida mediana de quem concluiu (minutos)\n'
                  'Entre parênteses, quantos concluíram na categoria em 2024 e em 2025', fontsize=10)
    ax.set_title(f'Em {r["cat_acima"]} das {r["n_categorias"]} categorias, a corrida mediana de 2025\n'
                 f'ficou mais de {LIMIAR_MIN} minutos mais lenta', fontsize=12)
    fig.legend(title='Edição', loc='outside lower center', ncols=3, fontsize=10, title_fontsize=10)
    ax.tick_params(axis='x', labelsize=10)
    return fig


# ---------------------------------------------------------------- o relatório

def _sentido(dif, feminino=True):
    if abs(dif) < 0.05:
        return 'igual'
    return ('mais lenta' if dif > 0 else 'mais rápida') if feminino else ('mais lento' if dif > 0 else 'mais rápido')


def montar(t, ed, pasta, dados=DADOS, r=None, carimbo=None):
    """Escreve relatorio.md, numeros.csv e as figuras dentro de `pasta`. Retorna o texto do relatório.

    `dados` é a pasta dos arquivos de entrada, que vão com o hash no fim do relatório.
    """
    r = r or Registro()
    pasta = Path(pasta)
    c = concluintes(t)
    contagem = t.groupby(['edicao', 'status']).size().unstack(fill_value=0)

    # participação: cada número das frases entra pelo registro
    for e in (2024, 2025):
        inscritos = int((t.edicao == e).sum())
        largaram = int(contagem.loc[e, LARGARAM].sum())
        concluiu = int(contagem.loc[e, 'concluiu'])
        r.anota(f'inscritos_{e}', inscritos, 'inscrições do ano, sem cópias', f'inscrições de {e}', casas=0)
        r.anota(f'largaram_{e}', largaram, 'status concluiu, DNF ou DSQ', f'inscrições de {e}', casas=0)
        r.anota(f'concluiu_{e}', concluiu, 'status concluiu', f'inscrições de {e}', casas=0)
        r.anota(f'taxa_largaram_{e}', 100 * concluiu / largaram, 'concluíram / largaram',
                f'quem largou em {e} (concluiu, DNF ou DSQ)', unidade='%')
        r.anota(f'taxa_inscritos_{e}', 100 * concluiu / inscritos, 'concluíram / inscritos',
                f'todos os inscritos de {e}', unidade='%')
        r.anota(f'fora_{e}', inscritos - concluiu, 'inscritos menos quem concluiu', f'inscrições de {e}', casas=0)
        r.anota(f'sem_resultado_{e}', int(contagem.loc[e].get('sem resultado', 0)),
                'inscrições sem resultado na API', f'inscrições de {e}', casas=0)

    med = c.groupby('edicao')[['natacao_min', 'ciclismo_min', 'corrida_min']].median()
    for e in (2024, 2025):
        r.anota(f'corrida_{e}', med.loc[e, 'corrida_min'], 'mediana da corrida', f'quem concluiu em {e}',
                unidade='min')
    dif_corrida = med.loc[2025, 'corrida_min'] - med.loc[2024, 'corrida_min']
    dif_ciclismo = med.loc[2025, 'ciclismo_min'] - med.loc[2024, 'ciclismo_min']
    r.anota('dif_corrida', abs(dif_corrida), 'mediana de 2025 menos mediana de 2024, corrida',
            'quem concluiu em cada edição', unidade='min')
    r.anota('dif_ciclismo', abs(dif_ciclismo), 'mediana de 2025 menos mediana de 2024, ciclismo',
            'quem concluiu em cada edição', unidade='min')

    cat = tabela_categorias(c)
    r.anota('n_categorias', len(cat), 'categorias com concluintes nas duas edições', 'quem concluiu', casas=0)
    r.anota('cat_acima', int((cat.dif > LIMIAR_MIN).sum()), f'categorias com diferença acima de {LIMIAR_MIN} min',
            'mediana da corrida de quem concluiu, por categoria', casas=0)
    r.anota('limiar_min', LIMIAR_MIN, 'regra do relatório', 'diferença que vai para o resumo', casas=0, unidade='min')

    for etapa in ('natacao', 'ciclismo', 'corrida'):
        for e in (2024, 2025):
            v = ed.loc[e, f'{etapa}_km']
            r.anota(f'{etapa}_km_{e}', v, f'edicoes.csv, coluna {etapa}_km', f'edição {e}',
                    casas=1 if v % 1 else 0, unidade='km')
    for e in (2024, 2025):
        r.anota(f'temp_{e}', ed.loc[e, 'temperatura_max_c'], 'edicoes.csv, coluna temperatura_max_c',
                f'edição {e}', casas=0, unidade='°C')

    pequenos = [(k, e, int(n)) for k in cat.index for e, n in ((2024, cat.loc[k, 'n2024']), (2025, cat.loc[k, 'n2025']))
                if n < LIMIAR_N]
    pequenos.sort()
    r.anota('limiar_n', LIMIAR_N, 'regra do relatório', 'grupo pequeno demais para ler a mediana', casas=0)
    r.anota('n_pequenos', len(pequenos), f'grupos de categoria e edição com menos de {LIMIAR_N} concluintes',
            'quem concluiu', casas=0)
    for k, e, n in pequenos:
        r.anota(f'n_{k}_{e}', n, 'concluintes da categoria na edição', f'{k} em {e}', casas=0)

    # figuras: o título usa o mesmo registro das frases
    figs = pasta / 'figuras'
    salvar_figura(figura_etapas(c, ed, r), figs / 'etapas.png')
    salvar_figura(figura_categorias(cat, r), figs / 'categorias.png')

    # tabelas: saem do DataFrame inteiro, com a origem na legenda
    part = pd.DataFrame({
        'Edição': [2024, 2025],
        'Inscritos': [r['inscritos_2024'], r['inscritos_2025']],
        'Largaram': [r['largaram_2024'], r['largaram_2025']],
        'Concluíram': [r['concluiu_2024'], r['concluiu_2025']],
        'DNF': [int(contagem.loc[e, 'DNF']) for e in (2024, 2025)],
        'DSQ': [int(contagem.loc[e, 'DSQ']) for e in (2024, 2025)],
        'DNS': [int(contagem.loc[e, 'DNS']) for e in (2024, 2025)],
        'Sem resultado': [r['sem_resultado_2024'], r['sem_resultado_2025']],
        'Concluíram / largaram': [r['taxa_largaram_2024'], r['taxa_largaram_2025']],
        'Concluíram / inscritos': [r['taxa_inscritos_2024'], r['taxa_inscritos_2025']],
    })
    etapas = pd.DataFrame({
        'Etapa': ['natação', 'ciclismo', 'corrida'],
        '2024 (km)': [r[f'{x}_km_2024'].replace(' km', '') for x in ('natacao', 'ciclismo', 'corrida')],
        '2025 (km)': [r[f'{x}_km_2025'].replace(' km', '') for x in ('natacao', 'ciclismo', 'corrida')],
        'Mediana 2024 (min)': [med.loc[2024, f'{x}_min'] for x in ('natacao', 'ciclismo', 'corrida')],
        'Mediana 2025 (min)': [med.loc[2025, f'{x}_min'] for x in ('natacao', 'ciclismo', 'corrida')],
    })
    cats = pd.DataFrame({'Categoria': cat.index, 'Concluíram 2024': cat.n2024.astype(int).astype(str),
                         'Mediana 2024 (min)': cat.m2024, 'Concluíram 2025': cat.n2025.astype(int).astype(str),
                         'Mediana 2025 (min)': cat.m2025, 'Diferença (min)': cat.dif}).iloc[::-1]

    nat = 'ficou mais curta' if ed.loc[2025, 'natacao_km'] < ed.loc[2024, 'natacao_km'] else 'mudou'
    linhas = ['# Relatório da prova de 2025', '',
              'Comissão técnica, para a assembleia da federação. Todas as tabelas, figuras e frases saem do '
              '`relatorio.py`, a partir dos arquivos listados no fim.', '']
    linhas += [
        '## O que mudou de 2024 para 2025', '',
        f'- Em 2025, {r["concluiu_2025"]} dos {r["largaram_2025"]} atletas que largaram concluíram a prova: '
        f'{r["taxa_largaram_2025"]}. Em 2024, foram {r["concluiu_2024"]} de {r["largaram_2024"]}: '
        f'{r["taxa_largaram_2024"]}.',
        f'- Sobre todos os inscritos, e não só sobre quem largou, a taxa foi {r["taxa_inscritos_2025"]} em 2025 '
        f'e {r["taxa_inscritos_2024"]} em 2024.',
        f'- A corrida mediana de quem concluiu ficou {r["dif_corrida"]} {_sentido(dif_corrida)}: '
        f'{r["corrida_2025"]} em 2025, contra {r["corrida_2024"]} em 2024. O ciclismo, com a mesma distância, '
        f'ficou {r["dif_ciclismo"]} {_sentido(dif_ciclismo, feminino=False)}.',
        f'- Em {r["cat_acima"]} das {r["n_categorias"]} categorias, a corrida mediana de 2025 ficou mais de '
        f'{r["limiar_min"]} acima da de 2024.',
        f'- A natação {nat}: {r["natacao_km_2024"]} em 2024 e {r["natacao_km_2025"]} em 2025.', '',
        '## Quem largou e quem concluiu', '',
        tabela_md(part), '',
        'Origem: inscrições de 2024 e 2025, com o status de cada uma na API. Largaram = concluiu, DNF ou DSQ. '
        'Inscrição sem resultado na API conta como inscrito que não largou.', '',
        '## O tempo de cada etapa', '',
        '![Tempo mediano da natação, do ciclismo e da corrida em 2024 e 2025](figuras/etapas.png)', '',
        tabela_md(etapas), '',
        'Origem: parciais da API de quem concluiu cada edição; distâncias do edicoes.csv. As transições não entram.', '',
        '## A corrida por categoria', '',
        '![Corrida mediana de cada categoria em 2024 e 2025](figuras/categorias.png)', '',
        tabela_md(cats), '',
        'Origem: corrida de quem concluiu, por categoria e edição. Diferença = mediana de 2025 menos mediana de 2024.', '',
        '## Limites', '',
        f'- A natação teve {r["natacao_km_2024"]} em 2024 e {r["natacao_km_2025"]} em 2025 '
        f'("{ed.loc[2025, "observacao"]}", no edicoes.csv). Por isso o tempo total e a natação não '
        'servem para comparar as edições.',
        f'- A máxima foi de {r["temp_2024"]} em 2024 e de {r["temp_2025"]} em 2025. O relatório mostra que a '
        'corrida ficou mais lenta. Ele não mostra que o calor foi a causa.',
        f'- As medianas são de quem concluiu. Ficaram fora {r["fora_2024"]} dos {r["inscritos_2024"]} inscritos '
        f'de 2024 e {r["fora_2025"]} dos {r["inscritos_2025"]} de 2025.',
        f'- Em {r["n_pequenos"]} grupos de categoria e edição, menos de {r["limiar_n"]} atletas concluíram. '
        'Neles, a mediana muda com um atleta a mais ou a menos:',
    ]
    linhas += [f'  - {k} em {e}: {r[f"n_{k}_{e}"]}' for k, e, _ in pequenos]
    linhas += [
        f'- {r["sem_resultado_2024"]} inscrições de 2024 e {r["sem_resultado_2025"]} de 2025 não têm resultado '
        'na API. Elas contam como inscritos que não largaram.', '',
        '## De onde vêm os números', '',
        'Cada número das frases acima, com a conta e com quem entra nela. A mesma tabela está em numeros.csv.', '',
        tabela_md(r.tabela()), '',
        '## Como gerar de novo', '',
        'Na pasta da aula, no kit do curso:', '', '```bash', 'python3 relatorio.py', '```', '',
        f'Gerado com Python {sys.version.split()[0]}, pandas {pd.__version__} e Matplotlib {matplotlib.__version__}.',
    ]
    if carimbo:  # um texto livre, por exemplo a data: fica nessa seção, fora da checagem dos números
        linhas += ['', carimbo]
    linhas += ['', 'Arquivos de entrada:', '']
    entrada = pd.DataFrame([{'Arquivo': n, 'Bytes': str(len(b)), 'SHA-256 (início)': hashlib.sha256(b).hexdigest()[:16]}
                            for n, b in ((n, (Path(dados) / n).read_bytes()) for n in ARQUIVOS)])
    linhas += [tabela_md(entrada), '']
    texto = '\n'.join(linhas)

    faltam = numeros_sem_origem(texto, r, livres=t.edicao.unique())
    if faltam:
        raise ContaNaoFecha(f'número no texto sem origem no registro: {", ".join(faltam)}')
    (pasta / 'relatorio.md').write_text(texto, encoding='utf-8')
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=['nome', 'valor', 'conta', 'quem entra'], lineterminator='\n')
    w.writeheader()
    w.writerows(r.linhas)
    (pasta / 'numeros.csv').write_text(buf.getvalue(), encoding='utf-8')
    return texto



def gerar(dados=DADOS, saida=SAIDA, carimbo=None):
    """Grava a pasta `saida` do zero. Se qualquer conta não fecha, não grava nada e a pasta antiga fica.

    Monta tudo numa pasta nova ao lado e só no fim troca pela antiga. Retorna os hashes do que gravou.
    `carimbo` é uma linha de texto livre que vai para a seção «Como gerar de novo».
    """
    dados, saida = Path(dados), Path(saida)
    t = carregar(dados)
    ed = carregar_edicoes(dados)
    for col in ('natacao_km', 'ciclismo_km', 'corrida_km', 'temperatura_max_c'):
        vazios = ed.index[ed[col].isna()].tolist()
        if vazios:
            raise ContaNaoFecha(f'edicoes.csv sem {col} em {vazios}')
    nova = saida.with_name(saida.name + '-novo')
    if nova.exists():
        shutil.rmtree(nova)
    nova.mkdir(parents=True)
    try:
        montar(t, ed, nova, dados, carimbo=carimbo)
    except BaseException:
        shutil.rmtree(nova, ignore_errors=True)
        raise
    if saida.exists():
        shutil.rmtree(saida)
    nova.rename(saida)
    return hashes(saida)


def hashes(pasta):
    """O SHA-256 (início) de cada arquivo da pasta, em ordem de nome."""
    pasta = Path(pasta)
    return {str(p.relative_to(pasta)): hashlib.sha256(p.read_bytes()).hexdigest()[:16]
            for p in sorted(pasta.rglob('*')) if p.is_file()}


def main(argv=None):
    p = argparse.ArgumentParser(description='Gera o relatório da prova, aula «Produzir relatório reproduzível».')
    p.add_argument('--dados', default=str(DADOS), help='pasta dos dados (padrão: ../dados/triatlo)')
    p.add_argument('--saida', default=str(SAIDA), help='pasta do relatório (padrão: relatorio)')
    p.add_argument('--numeros', action='store_true', help='depois de gerar, imprime a origem de cada número')
    a = p.parse_args(argv)
    try:
        hs = gerar(a.dados, a.saida)
    except FileNotFoundError as erro:
        print(erro)
        sys.exit(2)
    except ContaNaoFecha as erro:
        print(f'o relatório não foi gravado: {erro}')
        sys.exit(1)
    print(f'relatório gravado em {a.saida}/')
    for nome, h in hs.items():
        print(f'  {nome:24s} {h}')
    linhas = list(csv.DictReader((Path(a.saida) / 'numeros.csv').open(encoding='utf-8')))
    print(f'números nas frases: {len(linhas)} anotados, nenhum sem origem')
    if a.numeros:
        for l in linhas:
            print(f'  {l["nome"]:22s} {l["valor"]:>8s} | {l["conta"]} | {l["quem entra"]}')


if __name__ == '__main__':
    main()
