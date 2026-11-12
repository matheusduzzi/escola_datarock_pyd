"""Monta os arquivos de entrada da aula «Transformar com regras explícitas».

Lê a base da Loja Exemplo (../dados/loja) e os atletas do triatlo (../dados/triatlo) e escreve:

- pedidos_caixa.csv: a exportação do caixa do primeiro semestre, como saiu do sistema;
- fechamento_financeiro.csv: o fechamento de cada mês feito pelo financeiro, para comparar;
- inscricoes_2026.csv: a lista de inscrições de 2026 do triatlo, para o exercício.

Só usa a biblioteca padrão do Python e sempre escreve os mesmos arquivos.
"""
import csv
import random
from collections import defaultdict
from pathlib import Path

AQUI = Path(__file__).absolute().parent
LOJA = AQUI.parent / 'dados' / 'loja'
TRIATLO = AQUI.parent / 'dados' / 'triatlo'
DIAS_REENVIADOS = ['2026-03-14', '2026-05-08']
ANO_PROVA = 2026


def ler(caminho):
    with open(caminho, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def escrever(nome, colunas, linhas):
    with open(AQUI / nome, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=colunas, lineterminator='\n')
        w.writeheader()
        w.writerows(linhas)


def faixa(idade):
    if idade < 25:
        return '18-24'
    if idade >= 65:
        return '65+'
    base = idade // 5 * 5
    return f'{base}-{base + 4}'


def caixa(rnd):
    pedidos = ler(LOJA / 'pedidos.csv')
    jeitos = {'entregue': ['Entregue', 'ENTREGUE', 'entregue '], 'cancelado': ['Cancelado', ' cancelado']}
    linhas = []
    for p in pedidos:
        p = dict(p)
        if rnd.random() < 0.07:
            p['status'] = rnd.choice(jeitos[p['status']])
        linhas.append(p)
    colunas = list(pedidos[0].keys())
    # O caixa reenviou dois dias inteiros no fim da exportação: as mesmas linhas, iguais.
    reenvio = [dict(p) for p in linhas if p['data_pedido'] in DIAS_REENVIADOS]
    escrever('pedidos_caixa.csv', colunas, linhas + reenvio)
    return len(linhas), len(reenvio)


def fechamento():
    preco = {p['id_produto']: float(p['preco']) for p in ler(LOJA / 'produtos.csv')}
    meses = defaultdict(lambda: [0, 0.0])
    for p in ler(LOJA / 'pedidos.csv'):
        if p['status'] != 'entregue':
            continue
        # O financeiro fecha pela maquininha: ele tem o valor dos pedidos que o caixa não anotou.
        valor = float(p['valor']) if p['valor'] else preco[p['id_produto']] * int(p['quantidade'])
        m = meses[p['data_pedido'][:7]]
        m[0] += 1
        m[1] += valor
    linhas = [{'mes': k, 'pedidos_entregues': v[0], 'receita': f'{v[1]:.2f}'} for k, v in sorted(meses.items())]
    escrever('fechamento_financeiro.csv', ['mes', 'pedidos_entregues', 'receita'], linhas)


def inscricoes(rnd):
    atletas = ler(TRIATLO / 'atletas.csv')
    escolhidos = sorted(rnd.sample(atletas, 320), key=lambda a: int(a['id_atleta']))
    linhas = []
    for i, a in enumerate(escolhidos, start=1):
        idade = ANO_PROVA - int(a['ano_nascimento'])
        linhas.append({'id_inscricao': f'2026-{i:04d}', 'id_atleta': a['id_atleta'], 'sexo': a['sexo'],
                       'ano_nascimento': a['ano_nascimento'], 'categoria': a['sexo'] + faixa(idade),
                       'valor_pago': rnd.choice(['980.00', '1150.00']), 'cortesia': ''})
    def muda_faixa(l):
        idade = ANO_PROVA - int(l['ano_nascimento'])
        return faixa(idade) != faixa(idade - 1)

    borda = [i for i, l in enumerate(linhas) if muda_faixa(l)]
    rnd.shuffle(borda)
    ids = [i for i in range(len(linhas)) if i not in borda[:22]]
    rnd.shuffle(ids)
    grupos = {'cat_ano_passado': borda[:22], 'cat_texto': ids[0:18], 'sexo_texto': ids[18:32],
              'sexo_vazio': ids[32:41], 'ano_vazio': ids[41:47], 'cortesia': ids[47:54], 'sem_valor': ids[54:59]}
    for i in grupos['cat_ano_passado']:
        # Categoria pela idade de 2025: quem fez aniversário de faixa ainda marca a faixa antiga.
        l = linhas[i]
        l['categoria'] = l['sexo'] + faixa(ANO_PROVA - 1 - int(l['ano_nascimento']))
    for i in grupos['cat_texto']:
        l = linhas[i]
        l['categoria'] = rnd.choice([l['categoria'].lower(), ' ' + l['categoria'], l['categoria'] + ' '])
    for i in grupos['sexo_texto']:
        l = linhas[i]
        l['sexo'] = rnd.choice([l['sexo'].lower(), l['sexo'] + ' '])
    for i in grupos['sexo_vazio']:
        linhas[i]['sexo'] = ''
    for i in grupos['ano_vazio']:
        linhas[i]['ano_nascimento'] = ''
    for i in grupos['cortesia']:
        linhas[i]['cortesia'] = 'sim'
        linhas[i]['valor_pago'] = ''
    for i in grupos['sem_valor']:
        linhas[i]['valor_pago'] = ''
    # Três inscrições de atletas sem cadastro anterior, com menos de 18 anos no ano da prova.
    for j, (sexo, ano) in enumerate([('F', '2009'), ('M', '2010'), ('M', '2009')], start=1):
        idade = ANO_PROVA - int(ano)
        linhas.append({'id_inscricao': f'2026-{len(linhas) + 1:04d}', 'id_atleta': str(700 + j), 'sexo': sexo,
                       'ano_nascimento': ano, 'categoria': sexo + '18-24', 'valor_pago': '980.00', 'cortesia': ''})
    # O sistema exportou duas vezes as dez últimas inscrições do dia: as mesmas linhas, iguais.
    repetidas = [dict(l) for l in linhas[150:160]]
    colunas = ['id_inscricao', 'id_atleta', 'sexo', 'ano_nascimento', 'categoria', 'valor_pago', 'cortesia']
    escrever('inscricoes_2026.csv', colunas, linhas[:160] + repetidas + linhas[160:])
    return len(linhas), len(repetidas)


if __name__ == '__main__':
    rnd = random.Random(22)
    n_caixa, n_reenvio = caixa(rnd)
    fechamento()
    n_insc, n_rep = inscricoes(rnd)
    print(f'pedidos_caixa.csv: {n_caixa + n_reenvio} linhas ({n_reenvio} reenviadas) | '
          f'fechamento_financeiro.csv: 6 meses | inscricoes_2026.csv: {n_insc + n_rep} linhas')
