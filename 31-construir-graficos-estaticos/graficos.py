"""Os gráficos da aula «Construir gráficos estáticos».

Rode de dentro da pasta da aula:
    python3 graficos.py --grafico rascunho
    python3 graficos.py --grafico chegada
    python3 graficos.py --grafico edicoes
    python3 graficos.py --grafico inscritos
    python3 graficos.py --grafico dispersao-matplotlib
    python3 graficos.py --grafico dispersao-seaborn
    python3 graficos.py --grafico todos

Cada gráfico vira um PNG na pasta saidas/ e o programa imprime a ficha dele: título, eixos,
escala, legenda e quantas marcas foram desenhadas, lidos do próprio objeto do Matplotlib.
Os dados vêm de ../dados/triatlo. Parcial vazia fica vazia: nada vira zero.
Para usar nos seus gráficos: from graficos import carregar, ficha
"""
import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # desenha direto no arquivo, sem abrir janela
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import PathPatch, Rectangle  # noqa: E402
from matplotlib.ticker import PercentFormatter  # noqa: E402

DADOS = Path('..') / 'dados' / 'triatlo'
SAIDAS = Path('saidas')
ETAPAS = ['natacao', 't1', 'ciclismo', 't2', 'corrida']
MUSGO, OCRE = '#52645C', '#B8742A'
CINZAS = ['#8C8C8C', '#ABABAB', '#C9C9C9', '#E0E0E0']
DPI = 150  # pontos por polegada no PNG: 8 x 4,5 polegadas viram 1200 x 675 px


def segundos(texto):
    if texto is None:
        return pd.NA
    h, m, s = (int(p) for p in texto.split(':'))
    return h * 3600 + m * 60 + s


def carregar():
    """Uma linha por inscrição das duas edições, com o resultado quando existe.

    Colunas em minutos (natacao_min ... corrida_min) e o tempo oficial em horas (oficial_h).
    O status 'sem resultado' marca a inscrição que não tem nenhum resultado no arquivo.
    """
    for nome in ['api_resultados.json', 'inscricoes_2024.csv', 'inscricoes_2025.csv', 'atletas.csv']:
        if not (DADOS / nome).is_file():
            print(f'arquivo não encontrado: {DADOS / nome}. Rode de dentro da pasta da aula, no kit do curso.')
            sys.exit(2)
    res = pd.DataFrame(json.loads((DADOS / 'api_resultados.json').read_text(encoding='utf-8')))
    res = res.drop_duplicates(subset=['edicao', 'id_inscricao'])  # cópias iguais, vistas na aula 26
    parciais = pd.json_normalize(res['parciais'].tolist())
    parciais.index = res.index
    for etapa in ETAPAS:
        res[etapa] = parciais[etapa].map(segundos).astype('Int64')
    res['oficial'] = res['tempo_oficial'].map(segundos).astype('Int64')
    insc = pd.concat([pd.read_csv(DADOS / 'inscricoes_2024.csv'),
                      pd.read_csv(DADOS / 'inscricoes_2025.csv', sep=';')]).drop_duplicates()
    insc['edicao'] = insc['id_inscricao'].str[:4].astype(int)
    atletas = pd.read_csv(DADOS / 'atletas.csv')
    t = insc.merge(atletas[['id_atleta', 'sexo', 'ano_nascimento']], on='id_atleta', how='left', validate='many_to_one')
    t = t.merge(res[['edicao', 'id_inscricao', 'status', 'oficial'] + ETAPAS], on=['edicao', 'id_inscricao'],
                how='left', validate='one_to_one')
    t['idade'] = t['edicao'] - t['ano_nascimento']
    t['status'] = t['status'].fillna('sem resultado')
    for etapa in ETAPAS:
        t[f'{etapa}_min'] = (t[etapa].astype('Float64') / 60).astype(float)
    t['oficial_h'] = (t['oficial'].astype('Float64') / 3600).astype(float)
    return t


def virgula(numero, casas=1):
    """85.4 -> '85,4': o rótulo do gráfico é para quem lê em português."""
    return f'{numero:.{casas}f}'.replace('.', ',')


def _texto(lista):
    return ' | '.join(lista) if lista else '(nenhum)'


def _marcas(eixo, rotulos):
    """Só as marcas que aparecem no desenho: o Matplotlib calcula também algumas fora dos limites."""
    baixo, alto = sorted(eixo.get_view_interval())
    return [r.get_text() for r, v in zip(rotulos, eixo.get_majorticklocs())
            if r.get_text() and baixo - 1e-9 <= v <= alto + 1e-9]


def ficha(fig, arquivo=None):
    """Imprime o que o gráfico tem de verdade, lido do objeto: eixos, escala, legenda e marcas."""
    fig.canvas.draw()  # monta os textos dos ticks como vão sair no arquivo
    if arquivo:
        largura, altura = (fig.get_size_inches() * DPI).round().astype(int)
        print(f'arquivo: {arquivo} ({largura} x {altura} px)')
    for i, ax in enumerate(fig.axes, start=1):
        if len(fig.axes) > 1:
            print(f'-- área {i}')
        print(f'título: {ax.get_title() or "(sem título)"}')
        print(f'eixo x: {ax.get_xlabel() or "(sem nome)"} | limites {ax.get_xlim()[0]:g} a {ax.get_xlim()[1]:g}')
        print(f'  marcas do eixo x: {_texto(_marcas(ax.xaxis, ax.get_xticklabels()))}')
        print(f'eixo y: {ax.get_ylabel() or "(sem nome)"} | limites {ax.get_ylim()[0]:g} a {ax.get_ylim()[1]:g}'
              f' | escala {ax.get_yscale()}')
        print(f'  marcas do eixo y: {_texto(_marcas(ax.yaxis, ax.get_yticklabels()))}')
        legenda = ax.get_legend() or (fig.legends[0] if fig.legends else None)
        if legenda is None:
            print('legenda: (sem legenda)')
        else:
            titulo = legenda.get_title().get_text()
            print(f'legenda: {(titulo + ": ") if titulo else ""}{_texto([t.get_text() for t in legenda.get_texts()])}')
        retangulos = [p for p in ax.patches if isinstance(p, Rectangle)]
        com_tamanho = [p for p in retangulos if p.get_height() * p.get_width() != 0]
        if com_tamanho:
            print(f'barras: {len(retangulos)} (com tamanho: {len(com_tamanho)})')
        caixas = [p for p in ax.patches if isinstance(p, PathPatch)]
        if caixas:
            print(f'caixas: {len(caixas)}')
        for linha in ax.get_lines():
            y = [v for v in linha.get_ydata()]
            if linha.get_label().startswith('_') or len(y) < 2:
                continue
            print(f'linha {linha.get_label()}: ' + ' | '.join(f'{round(v, 1):g}' for v in y))
        pontos = [len(c.get_offsets()) for c in ax.collections if len(c.get_offsets())]
        if pontos:
            print(f'pontos: {sum(pontos)} em {len(pontos)} grupo(s) de marcas ({" + ".join(map(str, pontos))})')
        for texto in [t.get_text() for t in ax.texts] + [t.get_text() for t in fig.texts]:
            print('texto no gráfico: ' + texto.replace('\n', ' / '))


def salvar(fig, nome):
    SAIDAS.mkdir(exist_ok=True)
    caminho = SAIDAS / f'{nome}.png'
    fig.savefig(caminho, dpi=DPI)
    ficha(fig, caminho.as_posix())
    plt.close(fig)


def rascunho(t):
    """O primeiro gráfico do Caio: o padrão do pandas, sem decidir nada."""
    c = t[(t.edicao == 2025) & t.oficial.notna()]
    ax = c['oficial'].astype(float).plot.hist()
    salvar(ax.figure, 'rascunho')


def chegada(t):
    d = t[t.edicao == 2025]
    c = d[d.oficial_h.notna()]
    fig, ax = plt.subplots(figsize=(8, 4.5), layout='constrained')
    contagens, bordas, _ = ax.hist(c.oficial_h, bins=range(8, 17), color=MUSGO, edgecolor='white')
    ax.set_title('Em que tempo chegou mais gente em 2025')
    ax.set_xlabel('Tempo oficial de prova (horas)')
    ax.set_ylabel('Atletas por faixa de 1 hora')
    ax.set_xticks(range(8, 17))
    ax.set_ylim(0, 100)
    fora = len(d) - len(c)
    ax.text(0.99, 0.97, f'{len(c)} atletas que concluíram.\n{fora} inscritos sem tempo oficial ficam fora.',
            transform=ax.transAxes, ha='right', va='top', fontsize=9, color='#444444')
    print('contagem por faixa: ' + ', '.join(f'{int(a)}-{int(b)} h: {int(n)}'
                                             for a, b, n in zip(bordas[:-1], bordas[1:], contagens)))
    salvar(fig, 'chegada')


def pontos_da_prova(t, ed, filtro=None):
    """Quem largou (concluiu, DNF ou DSQ) e quantos ainda estavam na prova em cada ponto, em número e em %."""
    d = t[(t.edicao == ed) & t.status.isin(['concluiu', 'DNF', 'DSQ'])]
    if filtro is not None:
        d = d[filtro(d)]
    contagem = [len(d)] + [int(d[etapa].notna().sum()) for etapa in ['natacao', 'ciclismo', 'corrida']]
    return [100 * n / contagem[0] for n in contagem], contagem


PONTOS = ['largada', 'fim da natação', 'fim do ciclismo', 'chegada']


def edicoes(t):
    fig, ax = plt.subplots(figsize=(8, 4.5), layout='constrained')
    for ed, cor in [(2024, '#8C8C8C'), (2025, MUSGO)]:
        pct, n = pontos_da_prova(t, ed)
        ax.plot(range(4), pct, marker='o', color=cor, linewidth=2, label=f'{ed} ({n[0]} largaram)')
        print(f'{ed}: ' + ' | '.join(f'{p} {a} ({virgula(b)}%)' for p, a, b in zip(PONTOS, n, pct)))
    ax.set_xticks(range(4), PONTOS)
    ax.set_title('Em que parte da prova os atletas saíram')
    ax.set_xlabel('Ponto da prova, na ordem em que acontece')
    ax.set_ylabel('Ainda na prova (% de quem largou)')
    ax.set_ylim(80, 100)
    ax.set_yticks(range(80, 101, 5))
    ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
    ax.legend(title='Edição', loc='lower left')
    ax.text(0.99, 0.03, 'O eixo y começa em 80%.\n2025: natação de 1,9 km e máxima de 31 °C.',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=9, color='#444444')
    salvar(fig, 'edicoes')


def inscritos(t):
    d = t[t.edicao == 2025]
    ordem = ['concluiu', 'DNF', 'DNS', 'DSQ', 'sem resultado']
    n = d.status.value_counts().reindex(ordem, fill_value=0)
    pct = 100 * n / n.sum()
    fig, ax = plt.subplots(figsize=(8, 3), layout='constrained')
    esquerda = 0
    for (status, qtd), p, cor in zip(n.items(), pct, [MUSGO] + CINZAS):
        barra = ax.barh(0, p, left=esquerda, color=cor, edgecolor='white',
                        label=f'{status}: {qtd} ({virgula(p)}%)')
        esquerda += p
        if p > 5:
            ax.bar_label(barra, labels=[f'{virgula(p)}%'], label_type='center', color='white', fontsize=11)
    ax.set_title(f'Dos {n.sum()} inscritos de 2025, quantos terminaram')
    ax.set_xlabel('% dos inscritos')
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(PercentFormatter(decimals=0))
    ax.set_yticks([])
    fig.legend(loc='outside lower center', ncols=3, fontsize=9, frameon=False)
    print('partes: ' + ' | '.join(f'{k} {v} ({virgula(p)}%)' for (k, v), p in zip(n.items(), pct)))
    salvar(fig, 'inscritos')


def concluintes_2025(t):
    return t[(t.edicao == 2025) & (t.status == 'concluiu')].copy()


SEXO = {'F': 'Feminino', 'M': 'Masculino'}


def nota_dispersao(ax, n):
    ax.text(0.01, 0.98, f'Cada ponto é um dos {n} atletas que concluíram.', transform=ax.transAxes,
            ha='left', va='top', fontsize=9, color='#444444')


def dispersao_matplotlib(t):
    c = concluintes_2025(t)
    fig, ax = plt.subplots(figsize=(7, 5), layout='constrained')
    for sexo, cor in [('F', OCRE), ('M', MUSGO)]:
        g = c[c.sexo == sexo]
        ax.scatter(g.natacao_min, g.corrida_min, s=14, alpha=0.6, color=cor, label=SEXO[sexo])
    ax.set_title('Quem nada mais rápido corre mais rápido? (2025)')
    ax.set_xlabel('Natação (minutos)')
    ax.set_ylabel('Corrida (minutos)')
    ax.legend(title='Sexo', loc='lower right')
    nota_dispersao(ax, len(c))
    salvar(fig, 'dispersao-matplotlib')


def dispersao_seaborn(t):
    import seaborn as sns
    c = concluintes_2025(t)
    c['Sexo'] = c['sexo'].map(SEXO)  # a legenda do Seaborn usa o nome da coluna e os valores dela
    fig, ax = plt.subplots(figsize=(7, 5), layout='constrained')
    sns.scatterplot(data=c, x='natacao_min', y='corrida_min', hue='Sexo', hue_order=['Feminino', 'Masculino'],
                    palette=[OCRE, MUSGO], s=14, alpha=0.6, linewidth=0, ax=ax)
    print('== o que o Seaborn fez sozinho')
    ficha(fig)
    ax.set_title('Quem nada mais rápido corre mais rápido? (2025)')
    ax.set_xlabel('Natação (minutos)')
    ax.set_ylabel('Corrida (minutos)')
    sns.move_legend(ax, 'lower right')
    nota_dispersao(ax, len(c))
    print('== depois dos rótulos do Matplotlib')
    salvar(fig, 'dispersao-seaborn')


GRAFICOS = {'rascunho': rascunho, 'chegada': chegada, 'edicoes': edicoes, 'inscritos': inscritos,
            'dispersao-matplotlib': dispersao_matplotlib, 'dispersao-seaborn': dispersao_seaborn}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--grafico', required=True, choices=list(GRAFICOS) + ['todos'])
    args = ap.parse_args()
    dados = carregar()
    for nome, funcao in GRAFICOS.items():
        if args.grafico in (nome, 'todos'):
            if args.grafico == 'todos':
                print(f'##### {nome}')
            funcao(dados)
