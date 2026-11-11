"""Monta os arquivos da aula a partir dos pedidos da Loja Exemplo (../dados/loja/pedidos.csv).

Escreve quatro arquivos nesta pasta:
- caixa_loja.csv: os pedidos do caixa da loja física, com a hora do relógio da loja, sem fuso;
- site_pedidos.csv: os pedidos do site, com a hora em UTC, como a plataforma exporta;
- exportacoes_site.csv: o registro das exportações diárias do site, um dia UTC por linha;
- entregas.csv: as entregas da transportadora, usado no exercício.

Só usa a biblioteca padrão e sempre escreve os mesmos arquivos.
"""
import csv
import datetime as dt
import random
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PEDIDOS = AQUI.parent / 'dados' / 'loja' / 'pedidos.csv'
SP = dt.timezone(dt.timedelta(hours=-3))  # São Paulo em 2026: sem horário de verão
FECHADA = {dt.date(2026, 1, 1), dt.date(2026, 4, 3), dt.date(2026, 4, 21), dt.date(2026, 5, 1)}
EXPORTACAO_QUE_FALHOU = dt.date(2026, 4, 10)
INICIO_TRANSPORTADORA = dt.date(2026, 2, 1)
PESO_HORA_SITE = [1, .5, .3, .2, .2, .3, .6, 1, 1.5, 2, 2.2, 2.3, 2.5, 2.3, 2.2, 2.2, 2.3, 2.5, 3, 3.5, 3.8, 3.6, 3, 2]
PESO_HORA_ENTREGA = {h: p for h, p in zip(range(8, 22), [1, 2, 3, 3, 2, 2, 3, 3, 3, 2, 2, 1.5, 1, 1])}


def loja_aberta(dia):
    return dia.weekday() != 6 and dia not in FECHADA


def escrever(nome, cabecalho, linhas):
    with open(AQUI / nome, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(cabecalho)
        w.writerows(linhas)


def main():
    rng = random.Random(28)
    with open(PEDIDOS, encoding='utf-8') as f:
        pedidos = sorted(csv.DictReader(f), key=lambda p: int(p['id_pedido']))

    caixa, site, entregas = [], [], []
    for p in pedidos:
        dia = dt.date.fromisoformat(p['data_pedido'])
        minuto, segundo = rng.randrange(60), rng.randrange(60)
        if loja_aberta(dia) and rng.random() < 0.35:
            hora = rng.randrange(9, 20)
            local = dt.datetime.combine(dia, dt.time(hora, minuto))
            caixa.append((local, p['id_pedido'], local.strftime('%d/%m/%Y %H:%M'), p['valor']))
        else:
            hora = rng.choices(range(24), PESO_HORA_SITE)[0]
            local = dt.datetime.combine(dia, dt.time(hora, minuto, segundo), tzinfo=SP)
            utc = local.astimezone(dt.timezone.utc)
            site.append((utc, p['id_pedido'], utc.strftime('%Y-%m-%dT%H:%M:%SZ'), p['valor']))
        if p['status'] == 'entregue':
            chega = dia + dt.timedelta(days=rng.choice([1, 1, 2, 2, 2, 3, 3, 4]))
            if chega.weekday() == 6:
                chega += dt.timedelta(days=1)
            hora = rng.choices(list(PESO_HORA_ENTREGA), list(PESO_HORA_ENTREGA.values()))[0]
            local = dt.datetime.combine(chega, dt.time(hora, rng.randrange(60)), tzinfo=SP)
            if chega >= INICIO_TRANSPORTADORA:
                if rng.random() < 0.4:
                    texto = local.astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                else:
                    texto = local.strftime('%Y-%m-%dT%H:%M:%S-03:00')
                entregas.append((local, p['id_pedido'], texto))

    exportado = [s for s in site if s[0].date() != EXPORTACAO_QUE_FALHOU]
    por_dia = {}
    for s in site:
        por_dia[s[0].date()] = por_dia.get(s[0].date(), 0) + 1
    exportacoes = []
    dia = dt.date(2026, 1, 1)
    while dia <= dt.date(2026, 7, 1):
        falhou = dia == EXPORTACAO_QUE_FALHOU
        exportacoes.append((dia.isoformat(), 'falhou' if falhou else 'ok', 0 if falhou else por_dia.get(dia, 0)))
        dia += dt.timedelta(days=1)

    escrever('caixa_loja.csv', ['id_pedido', 'data_hora', 'valor'], [c[1:] for c in sorted(caixa)])
    escrever('site_pedidos.csv', ['id_pedido', 'criado_em', 'valor'], [s[1:] for s in sorted(exportado)])
    escrever('exportacoes_site.csv', ['dia_utc', 'status', 'linhas'], exportacoes)
    escrever('entregas.csv', ['id_pedido', 'entregue_em'], [e[1:] for e in sorted(entregas)])
    print(f'caixa_loja.csv: {len(caixa)} pedidos | site_pedidos.csv: {len(exportado)} pedidos | '
          f'exportacoes_site.csv: {len(exportacoes)} dias | entregas.csv: {len(entregas)} entregas')


if __name__ == '__main__':
    main()
