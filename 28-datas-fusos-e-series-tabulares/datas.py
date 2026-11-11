"""A série diária de pedidos da Loja Exemplo, do jeito da IA e do jeito certo.

    python3 datas.py --jeito ia          o código que a IA passou, comparado com a base
    python3 datas.py --jeito formato     a data do caixa lida com format='mixed' e com o formato escrito
    python3 datas.py --jeito fuso        o dia do site em UTC e em São Paulo; o caixa no fuso errado
    python3 datas.py --jeito calendario  os dias que somem no groupby e o dia incompleto do site
    python3 datas.py --jeito certo       escreve serie_diaria.csv e serie_diaria_LEIA-ME.md

Rode antes `python3 gerar.py`, que monta os arquivos de entrada nesta pasta.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

import checar_serie

AQUI = Path(__file__).resolve().parent
FUSO = 'America/Sao_Paulo'
INICIO, FIM = '2026-01-01', '2026-06-30'
ABRE, FECHA = 9, 20  # horário da loja física


def ler(nome, **kw):
    caminho = AQUI / nome
    if not caminho.exists():
        sys.exit(f'falta {nome}: rode antes python3 gerar.py')
    return pd.read_csv(caminho, **kw)


def ler_caixa():
    """Caixa da loja: dia/mês/ano e hora do relógio da loja, sem fuso."""
    caixa = ler('caixa_loja.csv', dtype={'data_hora': str})
    caixa['quando'] = pd.to_datetime(caixa['data_hora'], format='%d/%m/%Y %H:%M').dt.tz_localize(FUSO)
    return caixa


def ler_site():
    """Site: ISO 8601 em UTC, com o Z no fim."""
    site = ler('site_pedidos.csv')
    site['quando'] = pd.to_datetime(site['criado_em'], format='%Y-%m-%dT%H:%M:%SZ', utc=True).dt.tz_convert(FUSO)
    return site


def calendario():
    return pd.date_range(INICIO, FIM, freq='D').strftime('%Y-%m-%d')


def dia(quando):
    """O dia do pedido no relógio de São Paulo, como texto AAAA-MM-DD."""
    return quando.dt.tz_convert(FUSO).dt.strftime('%Y-%m-%d')


def base_por_dia():
    """A lista de pedidos do financeiro: o dia de cada pedido, sem hora."""
    pedidos = ler('../dados/loja/pedidos.csv')
    return pedidos.groupby('data_pedido').size()


def comparar_com_base(contagem, rotulo):
    base = base_por_dia()
    no_semestre = contagem[(contagem.index >= INICIO) & (contagem.index <= FIM)]
    lado = pd.DataFrame({'base': base, 'serie': no_semestre}).reindex(calendario()).astype('Int64')
    iguais = (lado['base'] == lado['serie']).sum()
    fora = contagem[(contagem.index < INICIO) | (contagem.index > FIM)]
    print(f'{rotulo}: {len(contagem)} dias, de {contagem.index.min()} a {contagem.index.max()}, '
          f'{int(contagem.sum())} pedidos')
    print(f'  dias fora do semestre: {len(fora)}, com {int(fora.sum())} pedidos')
    print(f'  dias do semestre iguais à base do financeiro: {iguais} de {len(lado)}')
    return lado


def janela_que_falta():
    """Cada exportação que falhou cobre um dia UTC inteiro. Retorna (início, fim) no relógio de São Paulo."""
    exp = ler('exportacoes_site.csv')
    janelas = []
    for d in exp.loc[exp['status'] != 'ok', 'dia_utc']:
        inicio = pd.Timestamp(d, tz='UTC')
        janelas.append((inicio.tz_convert(FUSO), (inicio + pd.Timedelta(days=1)).tz_convert(FUSO)))
    return janelas


def dias_parciais(janelas):
    """Dias de São Paulo que a janela sem dado corta, com as horas que faltam."""
    parciais = {}
    for inicio, fim in janelas:
        for d in pd.date_range(inicio.normalize(), fim, freq='D'):
            de, ate = max(inicio, d), min(fim, d + pd.Timedelta(days=1))
            if ate > de:
                parciais[d.strftime('%Y-%m-%d')] = f'{de:%H:%M} às {"24:00" if ate == d + pd.Timedelta(days=1) else f"{ate:%H:%M}"}'
    return parciais


def jeito_ia():
    caixa = ler('caixa_loja.csv')
    site = ler('site_pedidos.csv')
    # o código que a IA passou
    caixa['quando'] = pd.to_datetime(caixa['data_hora'], format='mixed')
    site['quando'] = pd.to_datetime(site['criado_em'])
    caixa['dia'] = caixa['quando'].dt.date
    site['dia'] = site['quando'].dt.date
    serie = pd.concat([caixa, site]).groupby('dia').size()
    print('o código da IA rodou sem erro')
    serie.index = pd.Index([str(d) for d in serie.index])
    lado = comparar_com_base(serie, 'série da IA')
    print('\nos cinco primeiros dias do semestre:')
    print(lado.head().rename_axis('dia').to_string())


def jeito_formato():
    caixa = ler('caixa_loja.csv', dtype={'data_hora': str})
    misto = pd.to_datetime(caixa['data_hora'], format='mixed')
    escrito = pd.to_datetime(caixa['data_hora'], format='%d/%m/%Y %H:%M')
    print(f'caixa_loja.csv: {len(caixa)} pedidos | primeira linha: {caixa["data_hora"].iloc[0]}')
    try:
        pd.to_datetime(caixa['data_hora'])
    except ValueError as e:
        linhas = str(e).splitlines()
        print('sem format: ValueError:', linhas[0].split(' You might')[0])
        print('  a mensagem sugere:', linhas[-1].strip())
    trocou = misto != escrito
    print(f"\ncom format='mixed': {trocou.sum()} pedidos com dia e mês trocados")
    print(f'  meses que aparecem: {sorted(misto.dt.month.unique().tolist())}')
    exemplo = caixa.loc[trocou, 'data_hora'].iloc[0]
    print(f'  exemplo: {exemplo} virou {misto[trocou].iloc[0]:%Y-%m-%d %H:%M}')
    print(f"com format='%d/%m/%Y %H:%M': 0 trocados | meses que aparecem: {sorted(escrito.dt.month.unique().tolist())}")
    try:
        pd.to_datetime(pd.Series(['31/02/2026 10:00']), format='%d/%m/%Y %H:%M')
    except ValueError as e:
        print("31/02/2026 10:00 com o formato escrito: ValueError:", str(e).split(',')[0])


def jeito_fuso():
    site = ler('site_pedidos.csv')
    utc = pd.to_datetime(site['criado_em'], format='%Y-%m-%dT%H:%M:%SZ', utc=True)
    sp = utc.dt.tz_convert(FUSO)
    muda = utc.dt.strftime('%Y-%m-%d') != sp.dt.strftime('%Y-%m-%d')
    print(f'site_pedidos.csv: {len(site)} pedidos | tipo depois do to_datetime: {utc.dtype}')
    i = muda.idxmax()
    print(f'  pedido {site.loc[i, "id_pedido"]}: {site.loc[i, "criado_em"]} -> em São Paulo {sp[i]}')
    print(f'  pedidos que mudam de dia ao passar para São Paulo: {muda.sum()} '
          f'(horas em São Paulo: {sorted(sp[muda].dt.hour.unique().tolist())})')
    try:
        utc.dt.tz_localize(FUSO)
    except TypeError as e:
        print(f'  tz_localize num horário que já tem fuso: TypeError: {e}')

    import pytz
    print(f'  {FUSO} vem da base de fusos do pytz {pytz.OLSON_VERSION}; 2026-01-02 em São Paulo: '
          f'{pd.Timestamp("2026-01-02", tz=FUSO):%z}')

    caixa = ler('caixa_loja.csv', dtype={'data_hora': str})
    sem_fuso = pd.to_datetime(caixa['data_hora'], format='%d/%m/%Y %H:%M')
    print(f'\ncaixa_loja.csv: {len(caixa)} pedidos | tipo depois do to_datetime: {sem_fuso.dtype}')
    for nome, quando in [('tz_localize(FUSO)', sem_fuso.dt.tz_localize(FUSO)),
                         ("tz_localize('UTC') e tz_convert(FUSO)", sem_fuso.dt.tz_localize('UTC').dt.tz_convert(FUSO))]:
        hora = quando.dt.hour
        fora = ((hora < ABRE) | (hora >= FECHA)).sum()
        muda = (quando.dt.strftime('%Y-%m-%d') != sem_fuso.dt.strftime('%Y-%m-%d')).sum()
        print(f'  {nome}: primeiro {quando.iloc[0]} | fora do horário da loja (9h às 20h): {fora} | mudam de dia: {muda}')


def jeito_calendario():
    caixa = ler_caixa()
    loja = caixa.groupby(dia(caixa['quando'])).size()
    cal = calendario()
    faltam = cal.difference(loja.index)
    print(f'loja com groupby: {len(loja)} dias | o semestre tem {len(cal)} dias | faltam {len(faltam)}')
    semana = pd.to_datetime(faltam).day_name().value_counts()
    print(f'  dias que faltam: {semana.get("Sunday", 0)} domingos e '
          f'{", ".join(d for d in faltam if pd.Timestamp(d).day_name() != "Sunday")}')
    completa = loja.reindex(cal, fill_value=0)
    print(f'  média de pedidos por dia, só nos dias da série do groupby: {loja.mean():.2f}')
    print(f'  média de pedidos por dia do semestre, com 0 nos dias que faltam: {completa.mean():.2f}')
    print(f'  média por dia aberto: {completa[completa.index.isin(loja.index)].mean():.2f} em {len(loja)} dias')

    site = ler_site()
    por_dia = site.set_index('quando').resample('D').size()
    print(f'\nsite com resample: {len(por_dia)} dias, nenhum faltando')
    print('  dias com menos pedidos:')
    for d, n in por_dia.nsmallest(3).items():
        print(f'    {d:%Y-%m-%d}: {n}')
    exp = ler('exportacoes_site.csv')
    print(f'  exportacoes_site.csv: {len(exp)} dias UTC, {(exp["status"] != "ok").sum()} com status falhou: '
          f'{", ".join(exp.loc[exp["status"] != "ok", "dia_utc"])}')
    for d, horas in dias_parciais(janela_que_falta()).items():
        print(f'    em São Paulo, {d}: faltam as horas das {horas}')


def montar_serie():
    caixa, site = ler_caixa(), ler_site()
    cal = calendario()
    loja = caixa.groupby(dia(caixa['quando'])).size().reindex(cal, fill_value=0)
    online = site.groupby(dia(site['quando'])).size().reindex(cal, fill_value=0)
    parciais = dias_parciais(janela_que_falta())
    abertos = set(caixa['data_hora'].str.slice(0, 10).map(lambda d: f'{d[6:]}-{d[3:5]}-{d[:2]}'))
    serie = pd.DataFrame({'dia': cal})
    serie['dia_semana'] = pd.to_datetime(serie['dia']).dt.dayofweek.map(
        dict(enumerate(['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom'])))
    serie['loja_aberta'] = serie['dia'].isin(abertos).map({True: 'sim', False: 'não'})
    serie['loja'] = loja.to_numpy()
    serie['site'] = pd.array(online.to_numpy(), dtype='Int64')
    serie['cobertura'] = serie['dia'].map(lambda d: 'parcial' if d in parciais else 'completa')
    serie.loc[serie['cobertura'] == 'parcial', 'site'] = pd.NA
    serie['total'] = serie['loja'] + serie['site']
    recebidos = {d: int(online[d]) for d in parciais}
    return serie, parciais, recebidos


def leia_me(serie, parciais, recebidos):
    fechados = serie.loc[serie['loja_aberta'] == 'não', 'dia']
    domingos = (serie.loc[serie['loja_aberta'] == 'não', 'dia_semana'] == 'dom').sum()
    linhas = [
        '# Série diária de pedidos da Loja Exemplo',
        '',
        f'Uma linha por dia de {INICIO} a {FIM}: {len(serie)} dias, sem dia faltando nem repetido.',
        '',
        '- **dia**: o dia no relógio de São Paulo (America/Sao_Paulo). O site manda a hora em UTC e ela foi '
        'convertida; o caixa da loja escreve a hora de São Paulo, sem fuso.',
        '- **loja**: pedidos do caixa. Vale 0 quando a loja estava fechada '
        f'({domingos} domingos e {", ".join(d for d in fechados if pd.Timestamp(d).dayofweek != 6)}), '
        'marcados em `loja_aberta`.',
        '- **site**: pedidos do site. Fica vazio quando a `cobertura` é `parcial`.',
        f'- **cobertura**: `completa` em {(serie["cobertura"] == "completa").sum()} dias. `parcial` quando a '
        'exportação do site falhou numa parte do dia:',
    ]
    for d, horas in parciais.items():
        linhas.append(f'  - {d}: faltam as horas das {horas}; chegaram {recebidos[d]} pedidos do site.')
    linhas += [
        '- **total**: loja + site. Fica vazio nos dias parciais.',
        '- Vazio quer dizer "não sei". Zero quer dizer "não teve pedido".',
        '',
        'Gerado por `python3 datas.py --jeito certo`.',
    ]
    return '\n'.join(linhas) + '\n'


def jeito_certo():
    serie, parciais, recebidos = montar_serie()
    serie.to_csv(AQUI / 'serie_diaria.csv', index=False)
    (AQUI / 'serie_diaria_LEIA-ME.md').write_text(leia_me(serie, parciais, recebidos), encoding='utf-8')
    print(f'serie_diaria.csv: {len(serie)} linhas x {serie.shape[1]} colunas | serie_diaria_LEIA-ME.md escrito')
    print(serie[serie['dia'].between('2026-04-03', '2026-04-11')].to_string(index=False))
    print()
    problemas = checar_serie.checar(serie, INICIO, FIM, medidas=['site', 'total'], cobertura='cobertura',
                                    sem_dado={'parcial'})
    print('checar_serie:', 'ok' if not problemas else '; '.join(problemas))
    total = serie.set_index('dia')['total']
    base = base_por_dia().reindex(calendario())
    com_dado = total.notna()
    print(f'dias com total: {com_dado.sum()} | iguais à base do financeiro: {(total[com_dado] == base[com_dado]).sum()}')
    loja = serie.set_index('dia')['loja']
    for d in parciais:
        print(f'dia parcial {d}: base {base[d]} | loja {loja[d]} + site recebido {recebidos[d]} = {loja[d] + recebidos[d]}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--jeito', required=True, choices=['ia', 'formato', 'fuso', 'calendario', 'certo'])
    jeito = ap.parse_args().jeito
    {'ia': jeito_ia, 'formato': jeito_formato, 'fuso': jeito_fuso, 'calendario': jeito_calendario,
     'certo': jeito_certo}[jeito]()
