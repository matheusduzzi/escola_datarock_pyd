"""Monta o histórico de itens vendidos no marketplace Vitrine Paulista, de janeiro de 2024 a junho de 2026.

Usa o catálogo de produtos de ../dados/loja/produtos.csv e as cidades da Loja Exemplo, e escreve
historico_itens.csv nesta pasta: uma linha por item de pedido, com 20 colunas, do jeito que o
marketplace exporta. O arquivo é grande (409.176 linhas, 131 MB) e por isso não vem pronto no kit.

Só usa a biblioteca padrão e sempre escreve o mesmo arquivo.
"""
import csv
import datetime as dt
import hashlib
import itertools
import random
from pathlib import Path

AQUI = Path(__file__).resolve().parent
LOJA = AQUI.parent / 'dados' / 'loja'
SAIDA = AQUI / 'historico_itens.csv'
INICIO, FIM = dt.date(2024, 1, 1), dt.date(2026, 6, 30)
PEDIDOS_POR_DIA = 230
N_CLIENTES = 60_000
CIDADES = [('Campinas', 60), ('Sorocaba', 35), ('Jundiaí', 30), ('Piracicaba', 28), ('Ribeirão Preto', 27),
           ('Santos', 25), ('Limeira', 20), ('Americana', 18), ('Indaiatuba', 18), ('Valinhos', 15),
           ('São Carlos', 21), ('Bauru', 22)]
LOJAS = ['Loja Exemplo'] + ['Loja parceira %03d' % i for i in range(1, 180)]
COLUNAS = ['id_item', 'id_pedido', 'data', 'hora', 'id_cliente', 'nome_cliente', 'cidade', 'loja',
           'id_produto', 'produto', 'categoria', 'quantidade', 'preco_unitario', 'desconto_pct', 'valor',
           'status', 'canal', 'cupom', 'navegador', 'pagina_origem']
NAVEGADORES = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
]
ORIGENS = ['busca', 'email', 'instagram', 'direto', 'parceiro', 'whatsapp']
CUPONS = ['', '', '', '', '', '', '', 'BEMVINDO10', 'FRETEGRATIS', 'VOLTA5']


def ler(nome):
    with open(LOJA / nome, encoding='utf-8') as f:
        return list(csv.DictReader(f))


def main():
    rng = random.Random(29)
    produtos = ler('produtos.csv')
    cidades, pesos = zip(*CIDADES)
    clientes = [(i, 'Cliente %06d' % i, rng.choices(cidades, weights=pesos)[0]) for i in range(1, N_CLIENTES + 1)]
    acum_cli = list(itertools.accumulate(rng.uniform(0.2, 3) for _ in clientes))
    acum_loja = list(itertools.accumulate(rng.uniform(0.1, 2) for _ in LOJAS))
    id_item = id_pedido = 0
    with open(SAIDA, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(COLUNAS)
        dia = INICIO
        while dia <= FIM:
            sazonal = 1.35 if dia.month in (11, 12) else (0.85 if dia.month in (2, 3) else 1.0)
            crescimento = 1 + 0.15 * (dia.year - 2024)
            n = int(PEDIDOS_POR_DIA * sazonal * crescimento * rng.uniform(0.8, 1.2))
            segundos = sorted(rng.randrange(86400) for _ in range(n))
            for s in segundos:
                id_pedido += 1
                c = rng.choices(clientes, cum_weights=acum_cli)[0]
                loja = rng.choices(LOJAS, cum_weights=acum_loja)[0]
                canal = rng.choice(['site', 'site', 'app'])
                status = rng.choices(['entregue', 'cancelado', 'devolvido'], weights=[88, 8, 4])[0]
                cupom = rng.choice(CUPONS)
                nav = rng.choice(NAVEGADORES)
                origem = 'https://vitrinepaulista.com.br/?utm_source=%s&utm_campaign=c%03d' % (rng.choice(ORIGENS), rng.randrange(120))
                hora = '%02d:%02d:%02d' % (s // 3600, s // 60 % 60, s % 60)
                for _ in range(rng.choices([1, 2, 3, 4], weights=[55, 25, 13, 7])[0]):
                    id_item += 1
                    p = rng.choice(produtos)
                    preco = float(p['preco'])
                    qtd = rng.choices([1, 2, 3, 4, 5], weights=[60, 22, 10, 5, 3])[0]
                    desconto = rng.choice([0, 0, 0, 5, 10, 15]) if cupom or rng.random() < 0.2 else 0
                    valor = round(qtd * preco * (100 - desconto) / 100, 2)
                    w.writerow([id_item, id_pedido, dia.isoformat(), hora, c[0], c[1], c[2],
                                loja, p['id_produto'], p['nome'], p['categoria'], qtd, '%.2f' % preco, desconto,
                                '%.2f' % valor, status, canal, cupom, nav, origem])
            dia += dt.timedelta(days=1)
    tamanho = SAIDA.stat().st_size
    sha = hashlib.sha256(SAIDA.read_bytes()).hexdigest()
    print(f'historico_itens.csv: {id_item} linhas | {len(COLUNAS)} colunas | {id_pedido} pedidos | '
          f'{tamanho / 1e6:.0f} MB em disco | sha256 {sha[:12]}')


if __name__ == '__main__':
    main()
