"""Os gráficos e as contas da aula «Interatividade quando ajuda».

Rode de dentro da pasta da aula:
    python3 explorar.py --grafico todos
    python3 explorar.py --grafico helena
    python3 explorar.py --conta categorias
    python3 explorar.py --grafico livia

O gráfico interativo vira um arquivo HTML na pasta saidas/, que você abre no navegador.
O estático vira um PNG na mesma pasta. Depois de salvar, o programa imprime a ficha do gráfico,
lida do próprio objeto: é o que o navegador vai receber, ou o que está desenhado no PNG.
Os dados vêm de ../dados/triatlo. Parcial vazia fica vazia: nada vira zero.
Para usar nos seus gráficos: from explorar import carregar, concluintes, ficha, ficha_interativo
"""
import argparse
import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # desenha direto no arquivo, sem abrir janela
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

try:
    import plotly
    import plotly.express as px
except ImportError:
    print('o Plotly não está instalado neste Python. Instale com: python3 -m pip install plotly')
    sys.exit(2)

DADOS = Path('..') / 'dados' / 'triatlo'
SAIDAS = Path('saidas')
ETAPAS = ['natacao', 't1', 'ciclismo', 't2', 'corrida']
MUSGO, CINZA, OCRE = '#52645C', '#8C8C8C', '#B8742A'
CORES = {'2024': CINZA, '2025': MUSGO}
LARGARAM = ['concluiu', 'DNF', 'DSQ']  # DNS e "sem resultado" não largaram
DPI = 150


def segundos(texto):
    if texto is None:
        return pd.NA
    h, m, s = (int(p) for p in texto.split(':'))
    return h * 3600 + m * 60 + s


def carregar():
    """Uma linha por inscrição das duas edições, com o resultado quando existe.

    Colunas em minutos (natacao_min ... corrida_min), o tempo oficial em horas (oficial_h),
    numero_peito, categoria e equipe (vazia quando o atleta não tem equipe).
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
    t['status'] = t['status'].fillna('sem resultado')
    for etapa in ETAPAS:
        t[f'{etapa}_min'] = (t[etapa].astype('Float64') / 60).astype(float)
    t['oficial_h'] = (t['oficial'].astype('Float64') / 3600).astype(float)
    return t.drop(columns=ETAPAS + ['oficial'])


def concluintes(t):
    return t[t.status == 'concluiu']


def virgula(numero, casas=1):
    """85.4 -> '85,4': o texto do gráfico é para quem lê em português."""
    return f'{numero:.{casas}f}'.replace('.', ',')


def _texto(lista):
    return ' | '.join(lista) if lista else '(nenhum)'


def _marcas(eixo, rotulos):
    baixo, alto = sorted(eixo.get_view_interval())
    return [r.get_text().replace('\n', ' / ') for r, v in zip(rotulos, eixo.get_majorticklocs())
            if r.get_text() and baixo - 1e-9 <= v <= alto + 1e-9]


def ficha(fig, arquivo=None):
    """Ficha de uma figura do Matplotlib: o que o PNG tem de verdade."""
    fig.canvas.draw()
    if arquivo:
        largura, altura = (fig.get_size_inches() * DPI).round().astype(int)
        print(f'arquivo: {arquivo} ({largura} x {altura} px)')
    for ax in fig.axes:
        print(f'título: {(ax.get_title() or "(sem título)").replace(chr(10), " / ")}')
        print(f'eixo x: {(ax.get_xlabel() or "(sem nome)").replace(chr(10), " / ")} | limites {ax.get_xlim()[0]:g} a {ax.get_xlim()[1]:g}')
        print(f'  marcas do eixo x: {_texto(_marcas(ax.xaxis, ax.get_xticklabels()))}')
        print(f'eixo y: {ax.get_ylabel() or "(sem nome)"} | limites {ax.get_ylim()[0]:g} a {ax.get_ylim()[1]:g}')
        print(f'  marcas do eixo y: {_texto(_marcas(ax.yaxis, ax.get_yticklabels()))}')
        legenda = ax.get_legend() or (fig.legends[0] if fig.legends else None)
        if legenda is None:
            print('legenda: (sem legenda)')
        else:
            titulo = legenda.get_title().get_text()
            print(f'legenda: {(titulo + ": ") if titulo else ""}{_texto([x.get_text() for x in legenda.get_texts()])}')
        tamanhos = sorted({round(x.get_fontsize()) for x in ax.get_yticklabels() + ax.get_xticklabels() + ax.texts
                            + fig.texts + [ax.xaxis.label, ax.yaxis.label]})
        print(f'menor letra no gráfico: {tamanhos[0] if tamanhos else "-"} pt')
        for x in [x.get_text() for x in ax.texts] + [x.get_text() for x in fig.texts]:
            print('texto no gráfico: ' + x.replace('\n', ' / '))


def _pontos(valor):
    return 0 if valor is None else len(valor)


def ficha_interativo(fig, arquivo=None, menu=True):
    """Ficha de uma figura do Plotly: o que vai dentro do HTML que o navegador abre.

    Com menu=False, não lista as opções do menu, uma por linha.
    """
    if arquivo:
        html = Path(arquivo).read_text(encoding='utf-8')
        mb = Path(arquivo).stat().st_size / 1e6
        if 'src="https://cdn.plot.ly' in html:
            onde = 'carregado da internet (cdn.plot.ly): sem internet, o gráfico não aparece'
        elif re.search(r'plotly\.js v\d', html):
            onde = 'dentro do arquivo: abre sem internet'
        else:
            onde = 'não encontrado no arquivo'
        print(f'arquivo: {arquivo} ({virgula(mb)} MB) | plotly.js {onde}')
    lay = fig.layout
    print(f'título: {lay.title.text or "(sem título)"}')
    for nome, eixo in [('x', lay.xaxis), ('y', lay.yaxis)]:
        titulo = eixo.title.text or '(sem nome)'
        if eixo.range is not None:
            regua = f'régua fixa de {eixo.range[0]:g} a {eixo.range[1]:g}'
        else:
            regua = 'régua automática: o navegador recalcula a cada filtro'
        print(f'eixo {nome}: {titulo} | {regua}')
    print(f'separadores: {lay.separators!r}' if lay.separators else 'separadores: padrão do Plotly (ponto nos decimais)')
    print('séries: ' + _texto([f'{tr.name or "(sem nome)"} ({_pontos(tr.x)} pontos)' for tr in fig.data]))
    modelos = {tr.hovertemplate for tr in fig.data if tr.hovertemplate}
    for modelo in sorted(modelos):
        campos = re.sub(r'<extra>.*?</extra>', '', modelo).replace('<br>', ' / ')
        print(f'ao passar o mouse: {campos}')
    if not modelos:
        print('ao passar o mouse: (padrão do Plotly)')
    for caixa in lay.updatemenus:
        print(f'menu: {len(caixa.buttons)} opções')
        for botao in caixa.buttons if menu else []:
            dados = botao.args[0] if botao.args else {}
            if 'x' in dados:
                conta = [len(xs) for xs in dados['x']]
            else:
                conta = [_pontos(tr.x) for tr in fig.data]
            nomes = [tr.name or '(sem nome)' for tr in fig.data]
            print(f'  {botao.label}: ' + ' | '.join(f'{n} {k}' for n, k in zip(nomes, conta)))


def salvar(fig, nome):
    SAIDAS.mkdir(exist_ok=True)
    caminho = SAIDAS / f'{nome}.png'
    fig.savefig(caminho, dpi=DPI)
    plt.close(fig)
    return caminho


def salvar_html(fig, nome, plotlyjs=True):
    """plotlyjs=True põe o plotly.js dentro do arquivo; 'cdn' busca na internet ao abrir."""
    SAIDAS.mkdir(exist_ok=True)
    caminho = SAIDAS / f'{nome}.html'
    fig.write_html(caminho, include_plotlyjs=plotlyjs)
    return caminho


ROTULOS = {'ciclismo_min': 'Ciclismo (minutos)', 'corrida_min': 'Corrida (minutos)', 'edicao_txt': 'Edição'}
DETALHE = ('Peito %{customdata[0]}, %{customdata[1]}<br>Ciclismo: %{x:.1f} min<br>'
           'Corrida: %{y:.1f} min<extra>%{fullData.name}</extra>')


def todos(t):
    """O primeiro rascunho: todos os concluintes das duas edições, sem filtro."""
    c = concluintes(t).assign(edicao_txt=lambda d: d.edicao.astype(str))
    fig = px.scatter(c, x='ciclismo_min', y='corrida_min', color='edicao_txt', color_discrete_map=CORES,
                     custom_data=['numero_peito', 'categoria'], labels=ROTULOS,
                     title='Ciclismo e corrida de quem concluiu')
    fig.update_traces(hovertemplate=DETALHE, marker_size=6)
    return fig


def _regua(serie):
    """De dezena em dezena, com folga: do menor ao maior tempo de todas as categorias."""
    return [int((serie.min() - 5) // 10 * 10), int(-((-(serie.max() + 5)) // 10) * 10)]


def helena(t):
    """O gráfico da Helena: escolher a categoria no menu e ver cada atleta, com o número de peito."""
    c = concluintes(t).assign(edicao_txt=lambda d: d.edicao.astype(str))
    fig = todos(t)
    fig.update_layout(title_text='Ciclismo e corrida de quem concluiu: todas as categorias',
                      separators=',.', legend_title_text='Edição')
    # a régua fica parada: a mesma altura quer dizer os mesmos minutos em toda categoria
    fig.update_xaxes(range=_regua(c.ciclismo_min))
    fig.update_yaxes(range=_regua(c.corrida_min))

    botoes = []
    for categoria in ['Todas'] + sorted(c.categoria.unique()):
        parte = c if categoria == 'Todas' else c[c.categoria == categoria]
        xs, ys, extras = [], [], []
        for edicao in ['2024', '2025']:  # a mesma ordem das séries do px.scatter
            e = parte[parte.edicao_txt == edicao]
            xs.append(e.ciclismo_min.tolist())
            ys.append(e.corrida_min.tolist())
            extras.append(e[['numero_peito', 'categoria']].values.tolist())
        nome = 'todas as categorias' if categoria == 'Todas' else categoria
        botoes.append(dict(label=categoria, method='update',
                           args=[{'x': xs, 'y': ys, 'customdata': extras},
                                 {'title.text': f'Ciclismo e corrida de quem concluiu: {nome}'}]))
    fig.update_layout(updatemenus=[dict(buttons=botoes, x=1.0, y=1.15, xanchor='right', yanchor='top')])
    return fig


def tabela_categorias(t):
    """Mediana da corrida por categoria e edição, com quantos concluíram, da maior piora para a menor."""
    c = concluintes(t)
    m = c.groupby(['categoria', 'edicao']).corrida_min.agg(['median', 'count']).unstack('edicao')
    r = pd.DataFrame({'m2024': m[('median', 2024)], 'n2024': m[('count', 2024)],
                      'm2025': m[('median', 2025)], 'n2025': m[('count', 2025)]})
    r['dif'] = r.m2025 - r.m2024
    return r.sort_values('dif')


def livia(t):
    """O estático da Lívia: a mesma pergunta, respondida sem clicar."""
    r = tabela_categorias(t)
    acima = int((r.dif > 40).sum())
    fig, ax = plt.subplots(figsize=(8, 9), layout='constrained')
    y = range(len(r))
    ax.hlines(y, r.m2024, r.m2025, color='#C8C8C8', linewidth=2)
    ax.scatter(r.m2024, y, color=CINZA, s=40, label='2024', zorder=3)
    forte = r.dif > 40
    ax.scatter(r.m2025[~forte], [i for i, f in zip(y, forte) if not f], color=MUSGO, s=40, label='2025', zorder=3)
    ax.scatter(r.m2025[forte], [i for i, f in zip(y, forte) if f], color=OCRE, s=40,
               label='2025, mais de 40 min acima de 2024', zorder=3)
    ax.set_yticks(list(y), [f'{cat} ({a} e {b})' for cat, a, b in zip(r.index, r.n2024, r.n2025)], fontsize=10)
    ax.set_xlim(230, 345)
    for i, (dif, fim) in enumerate(zip(r.dif, r[['m2024', 'm2025']].max(axis=1))):
        ax.text(fim + 2, i, f'{"+" if dif >= 0 else "-"}{virgula(abs(dif))} min', va='center', fontsize=10)
    ax.set_xlabel('Corrida mediana de quem concluiu (minutos), 42,2 km nas duas edições\n'
                  'Entre parênteses, quantos concluíram na categoria em 2024 e em 2025', fontsize=10)
    ax.set_title(f'Em {acima} das 20 categorias, a corrida mediana de 2025\nficou mais de 40 minutos mais lenta',
                 fontsize=12)
    fig.legend(title='Edição', loc='outside lower center', ncols=3, fontsize=10, title_fontsize=10)
    ax.tick_params(axis='x', labelsize=10)
    return fig


def conta_categorias(t):
    r = tabela_categorias(t)
    print('corrida mediana de quem concluiu, em minutos (2024 com n | 2025 com n | diferença)')
    for cat, l in r.iterrows():
        print(f'{cat:7s} {virgula(l.m2024)} ({int(l.n2024)}) | {virgula(l.m2025)} ({int(l.n2025)}) | '
              f'{"+" if l.dif >= 0 else ""}{virgula(l.dif)}')
    c = concluintes(t)
    geral = c.groupby('edicao').corrida_min.median()
    print(f'todas juntas: {virgula(geral[2024])} | {virgula(geral[2025])} | +{virgula(geral[2025] - geral[2024])}')
    print(f'categorias com mais de 40 min de diferença: {int((r.dif > 40).sum())} | '
          f'com menos de 5 min: {int((r.dif < 5).sum())}')


GRAFICOS = {'todos': todos, 'helena': helena, 'livia': livia}
CONTAS = {'categorias': conta_categorias}


def main(argv=None):
    p = argparse.ArgumentParser(description='Gráficos e contas da aula «Interatividade quando ajuda».')
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--grafico', choices=sorted(GRAFICOS))
    g.add_argument('--conta', choices=sorted(CONTAS))
    a = p.parse_args(argv)
    t = carregar()
    if a.conta:
        CONTAS[a.conta](t)
        return
    fig = GRAFICOS[a.grafico](t)
    if a.grafico == 'livia':
        ficha(fig, salvar(fig, a.grafico))
    else:
        ficha_interativo(fig, salvar_html(fig, a.grafico))


if __name__ == '__main__':
    main()
