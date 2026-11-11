"""Os gráficos e as contas da aula «Evitar interpretações enganosas».

Rode de dentro da pasta da aula:
    python3 revisar.py --grafico caio
    python3 revisar.py --conta eixo
    python3 revisar.py --conta agregacao
    python3 revisar.py --conta cobertura
    python3 revisar.py --conta selecao
    python3 revisar.py --grafico corrigido
    python3 revisar.py --grafico abandono

Cada gráfico vira um PNG na pasta saidas/ e o programa imprime a ficha dele, lida do próprio
objeto do Matplotlib. Cada conta imprime os números que a revisão do gráfico usa.
Os dados vêm de ../dados/triatlo. Parcial vazia fica vazia: nada vira zero.
Para usar nos seus gráficos: from revisar import carregar, ficha, virgula
"""
import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # desenha direto no arquivo, sem abrir janela
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

DADOS = Path('..') / 'dados' / 'triatlo'
SAIDAS = Path('saidas')
ETAPAS = ['natacao', 't1', 'ciclismo', 't2', 'corrida']
NOMES = {'natacao': 'natação', 't1': 'T1', 'ciclismo': 'ciclismo', 't2': 'T2', 'corrida': 'corrida'}
MUSGO, CINZA, OCRE = '#52645C', '#8C8C8C', '#B8742A'
LARGARAM = ['concluiu', 'DNF', 'DSQ']  # DNS e "sem resultado" não largaram
DPI = 150


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
    for nome in ['api_resultados.json', 'inscricoes_2024.csv', 'inscricoes_2025.csv', 'atletas.csv', 'edicoes.csv']:
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


def edicoes():
    return pd.read_csv(DADOS / 'edicoes.csv').set_index('edicao')


def virgula(numero, casas=1):
    """85.4 -> '85,4': o texto do gráfico é para quem lê em português."""
    return f'{numero:.{casas}f}'.replace('.', ',')


def _texto(lista):
    return ' | '.join(lista) if lista else '(nenhum)'


def _marcas(eixo, rotulos):
    """Só as marcas que aparecem no desenho: o Matplotlib calcula também algumas fora dos limites."""
    baixo, alto = sorted(eixo.get_view_interval())
    return [r.get_text().replace('\n', ' / ') for r, v in zip(rotulos, eixo.get_majorticklocs())
            if r.get_text() and baixo - 1e-9 <= v <= alto + 1e-9]


def ficha(fig, arquivo=None):
    """Imprime o que o gráfico tem de verdade, lido do objeto: eixos, escala, legenda e marcas."""
    fig.canvas.draw()
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
        barras = [p for p in ax.patches if isinstance(p, Rectangle)]
        if barras:
            # barra em pé: todas com a mesma largura; barra deitada: todas com a mesma altura
            deitadas = len({round(p.get_height(), 9) for p in barras}) == 1 and len(barras) > 1 \
                and len({round(p.get_width(), 9) for p in barras}) > 1
            base = sorted({round(p.get_x() if deitadas else p.get_y(), 9) for p in barras})
            eixo, inicio = ('x', min(ax.get_xlim())) if deitadas else ('y', min(ax.get_ylim()))
            aviso = ''
            if any(b < inicio - 1e-9 for b in base):
                aviso = f' | o eixo {eixo} começa em {inicio:g}: a base das barras fica fora do desenho'
            print(f'barras: {len(barras)} {"deitadas" if deitadas else "em pé"} | base {_texto([f"{b:g}" for b in base])}{aviso}')
        for linha in ax.get_lines():
            y = list(linha.get_ydata())
            if linha.get_label().startswith('_') or len(y) < 2:
                continue
            print(f'linha {linha.get_label()}: ' + ' | '.join(f'{round(v, 1):g}' for v in y))
        for texto in [t.get_text() for t in ax.texts] + [t.get_text() for t in fig.texts]:
            print('texto no gráfico: ' + texto.replace('\n', ' / '))


def salvar(fig, nome):
    SAIDAS.mkdir(exist_ok=True)
    caminho = SAIDAS / f'{nome}.png'
    fig.savefig(caminho, dpi=DPI)
    ficha(fig, caminho.as_posix())
    plt.close(fig)


def concluintes(t):
    return t[t.status == 'concluiu']


def caio(t):
    """O gráfico que o Caio mandou para a assembleia, como ele fez."""
    media = concluintes(t).groupby('edicao').oficial_h.mean()
    fig, ax = plt.subplots(figsize=(6, 4.5), layout='constrained')
    ax.bar(['2024', '2025'], media.values, color=[CINZA, MUSGO])
    ax.set_ylim(11.5, 11.8)
    ax.set_title('2025 foi 9 minutos mais rápida')
    ax.set_ylabel('Tempo médio de prova (horas)')
    salvar(fig, 'caio')


def conta_eixo(t):
    media = concluintes(t).groupby('edicao').oficial_h.mean()
    a, b = media[2024], media[2025]
    print(f'média do tempo oficial: 2024 {virgula(a, 3)} h | 2025 {virgula(b, 3)} h')
    print(f'diferença: {virgula((a - b) * 60)} min, {virgula(100 * (a - b) / a)}% do tempo de 2024')
    for baixo in (11.5, 0):
        ha, hb = a - baixo, b - baixo
        print(f'eixo y a partir de {virgula(baixo, 1)} h: barra de 2024 com {virgula(ha, 3)}, de 2025 com {virgula(hb, 3)};'
              f' a de 2024 parece {virgula(ha / hb, 2)} vezes a de 2025')


def conta_agregacao(t):
    c = concluintes(t)
    print('quem concluiu, em minutos (média | mediana | quantos têm o tempo)')
    for etapa in ETAPAS:
        col = f'{etapa}_min'
        partes = []
        for ed in (2024, 2025):
            s = c[c.edicao == ed][col]
            partes.append(f'{ed}: {virgula(s.mean())} | {virgula(s.median())} | {s.notna().sum()}')
        print(f'{NOMES[etapa]:<9} ' + '   '.join(partes))
    partes = []
    for ed in (2024, 2025):
        s = c[c.edicao == ed].oficial_h * 60
        partes.append(f'{ed}: {virgula(s.mean())} | {virgula(s.median())} | {s.notna().sum()}')
    print(f'{"oficial":<9} ' + '   '.join(partes))


def conta_cobertura(t):
    for ed in (2024, 2025):
        d = t[t.edicao == ed]
        n = d.status.value_counts()
        larg = int(n.reindex(LARGARAM, fill_value=0).sum())
        conc = int(n.get('concluiu', 0))
        print(f'{ed}: inscritos {len(d)} | não largaram {int(n.get("DNS", 0)) + int(n.get("sem resultado", 0))}'
              f' (DNS {int(n.get("DNS", 0))}, sem resultado {int(n.get("sem resultado", 0))}) | largaram {larg}'
              f' | DNF {int(n.get("DNF", 0))} | DSQ {int(n.get("DSQ", 0))} | concluíram {conc}'
              f' ({virgula(100 * conc / larg)}% de quem largou)')
    c = concluintes(t)
    for ed in (2024, 2025):
        e = c[c.edicao == ed]
        print(f'{ed}, quem concluiu sem T1 marcado: {int(e.t1_min.isna().sum())} | sem T2 marcado: {int(e.t2_min.isna().sum())}')


def conta_selecao(t):
    ed = edicoes()
    for ano, linha in ed.iterrows():
        print(f'{ano}: natação {virgula(linha.natacao_km)} km | ciclismo {linha.ciclismo_km} km | '
              f'corrida {virgula(linha.corrida_km)} km | máxima {linha.temperatura_max_c} °C')
    c = concluintes(t).assign(mesma=lambda d: d.ciclismo_min + d.corrida_min)
    for ano in (2024, 2025):
        s = c[c.edicao == ano].mesma
        print(f'{ano}, ciclismo + corrida de quem concluiu: média {virgula(s.mean())} min | mediana {virgula(s.median())} min')


def corrigido(t):
    c = concluintes(t)
    km = edicoes()
    fig, ax = plt.subplots(figsize=(8, 4.5), layout='constrained')
    etapas = ['natacao', 'ciclismo', 'corrida']
    for i, (ed, cor) in enumerate([(2024, CINZA), (2025, MUSGO)]):
        e = c[c.edicao == ed]
        med = [e[f'{etapa}_min'].median() for etapa in etapas]
        barras = ax.bar([p + (i - 0.5) * 0.38 for p in range(3)], med, width=0.38, color=cor,
                        label=f'{ed} ({len(e)} concluíram)')
        ax.bar_label(barras, labels=[virgula(m, 0) for m in med], padding=2, fontsize=9)
        print(f'{ed}: ' + ' | '.join(f'{NOMES[etapa]} {virgula(m)} min' for etapa, m in zip(etapas, med)))
    ax.set_xticks(range(3), [f'natação\n{virgula(km.natacao_km[2024])} km em 2024, {virgula(km.natacao_km[2025])} km em 2025',
                             f'ciclismo\n{km.ciclismo_km[2024]} km nas duas',
                             f'corrida\n{virgula(km.corrida_km[2024])} km nas duas'])
    ax.set_title('Em 2025, a corrida foi 19 minutos mais lenta e a natação, mais curta')
    ax.set_ylabel('Tempo mediano da etapa (minutos)')
    ax.set_ylim(0, 460)  # espaço no topo para a nota
    ax.legend(title='Edição', loc='upper left')
    insc = t.groupby('edicao').size()
    fora = insc - c.groupby('edicao').size()
    ax.text(0.99, 0.98, f'Só quem concluiu. Ficaram fora {fora[2024]} de {insc[2024]} inscritos em 2024\n'
            f'e {fora[2025]} de {insc[2025]} em 2025. As transições não entram.\n'
            f'Máxima de {km.temperatura_max_c[2024]} °C em 2024 e {km.temperatura_max_c[2025]} °C em 2025.',
            transform=ax.transAxes, ha='right', va='top', fontsize=9, color='#444444')
    salvar(fig, 'corrigido')


def abandono(t):
    """O gráfico de abandono que o Caio mandou para a federação, como ele fez. É o do exercício."""
    d = t[t.edicao == 2025]
    inscritos = d.groupby('categoria').size()
    dnf = d[d.status == 'DNF'].groupby('categoria').size()
    taxa = (100 * dnf / inscritos).sort_values(ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(8, 4.5), layout='constrained')
    ax.bar(taxa.index, taxa.values, color=OCRE)
    ax.set_ylim(10, 32)
    ax.set_title('F55-59: a categoria que mais abandonou em 2025')
    ax.set_ylabel('Abandono (%)')
    print('valores do gráfico: ' + ' | '.join(f'{k} {virgula(v)}' for k, v in taxa.items()))
    salvar(fig, 'abandono')


GRAFICOS = {'caio': caio, 'corrigido': corrigido, 'abandono': abandono}
CONTAS = {'eixo': conta_eixo, 'agregacao': conta_agregacao, 'cobertura': conta_cobertura, 'selecao': conta_selecao}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    grupo = ap.add_mutually_exclusive_group(required=True)
    grupo.add_argument('--grafico', choices=list(GRAFICOS))
    grupo.add_argument('--conta', choices=list(CONTAS))
    args = ap.parse_args()
    dados = carregar()
    if args.grafico:
        GRAFICOS[args.grafico](dados)
    else:
        CONTAS[args.conta](dados)
