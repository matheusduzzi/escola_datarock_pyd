"""Monta os arquivos de entrada da aula «Converter e validar tipos».

Lê os atletas e os resultados de 2025 da competição de triatlo (../dados/triatlo) e escreve:

- formulario_2026.csv: as respostas do formulário de inscrição da edição 2026, como as pessoas digitaram;
- extrato_tesouraria.csv: o que o banco mostra de cada inscrição paga, para comparar;
- cronometragem_2025.csv: a planilha que o cronometrista digitou na prova de 2025, para o exercício.

Só usa a biblioteca padrão e sempre escreve os mesmos arquivos.
"""
import csv
import datetime as dt
import json
import random
from pathlib import Path

AQUI = Path(__file__).absolute().parent
TRIATLO = AQUI.parent / 'dados' / 'triatlo'
PROVA_2026 = dt.date(2026, 5, 24)
PROVA_2025 = dt.date(2025, 5, 25)
LARGADA_2025 = dt.datetime(2025, 5, 25, 6, 30)
RESPOSTAS = 480


def faixa(idade):
    if idade < 25:
        return '18-24'
    if idade >= 65:
        return '65+'
    base = idade // 5 * 5
    return f'{base}-{base + 4}'


def brl(valor, milhar=True, centavos=True, rs=False):
    inteiro = f'{int(valor):,}'.replace(',', '.') if milhar else str(int(valor))
    texto = inteiro + (',00' if centavos else '')
    return ('R$ ' if rs else '') + texto


def separar(rnd, ids, **grupos):
    """Sorteia, sem repetir, quais respostas recebem cada jeito de digitar."""
    ids = list(ids)
    rnd.shuffle(ids)
    saida, i = {}, 0
    for nome, n in grupos.items():
        for x in ids[i:i + n]:
            saida[x] = nome
        i += n
    return saida


def formulario(rnd):
    atletas = list(csv.DictReader(open(TRIATLO / 'atletas.csv', encoding='utf-8')))
    escolhidos = sorted(rnd.sample(atletas, RESPOSTAS), key=lambda a: int(a['id_atleta']))
    ids = list(range(1, RESPOSTAS + 1))
    canal = {i: 'site' for i in ids}
    for i in rnd.sample(ids, 96):
        canal[i] = 'app'
    site = [i for i in ids if canal[i] == 'site']
    # Respostas 1 e 2 ficam como o formulário espera: a primeira linha é o que a IA olha.
    meio = [i for i in site if i > 2]
    nasc_jeito = separar(rnd, meio, vazio=6, so_ano=5, inexistente=4, mes13=2, fora=3, sem_zero=12)
    cat_jeito = separar(rnd, meio, minuscula=8, espaco=7, desconhecida=5, vazio=4)
    val_jeito = separar(rnd, meio, vazio=5, isento=6, digitado_errado=2, por_extenso=1)
    formas_site = ['milhar', 'sem_milhar', 'inteiro', 'inteiro_milhar', 'rs']

    linhas, extrato = [], []
    for i, a in zip(ids, escolhidos):
        ano = int(a['ano_nascimento'])
        nasc = dt.date(ano, 1, 1) + dt.timedelta(days=rnd.randrange(365))
        if i == 1:
            nasc = nasc.replace(day=17)
        cat = a['sexo'] + faixa(PROVA_2026.year - ano)
        preco = 980 if rnd.random() < 0.45 else 1150

        # nascimento
        jeito = nasc_jeito.get(i)
        if canal[i] == 'app':
            t_nasc = nasc.isoformat()
        elif jeito == 'vazio':
            t_nasc = ''
        elif jeito == 'so_ano':
            t_nasc = str(ano)
        elif jeito == 'inexistente':
            t_nasc = rnd.choice(['31/02', '30/02', '31/04', '31/06']) + f'/{ano}'
        elif jeito == 'mes13':
            t_nasc = f'{nasc.day:02d}/13/{ano}'
        elif jeito == 'fora':
            t_nasc = nasc.strftime('%d/%m/') + rnd.choice(['2019', '2026', '1898'])
        elif jeito == 'sem_zero':
            t_nasc = f'{nasc.day}/{nasc.month}/{ano}'
        else:
            t_nasc = nasc.strftime('%d/%m/%Y')

        # categoria
        jeito = cat_jeito.get(i)
        if canal[i] == 'app' or jeito is None:
            t_cat = cat
        elif jeito == 'minuscula':
            t_cat = cat.lower()
        elif jeito == 'espaco':
            t_cat = rnd.choice([' ' + cat, cat + ' ', cat[0] + ' ' + cat[1:]])
        elif jeito == 'desconhecida':
            t_cat = rnd.choice(['Elite', 'Revezamento'])
        else:
            t_cat = ''

        # valor pago
        jeito = val_jeito.get(i)
        pago = preco
        if canal[i] == 'app':
            t_val = f'{preco}.00'
        elif jeito == 'vazio':
            t_val = ''
        elif jeito == 'isento':
            t_val, pago = 'isento', 0
        elif jeito == 'digitado_errado':
            t_val = brl(preco // 10, milhar=False)
        elif jeito == 'por_extenso':
            t_val = 'mil cento e cinquenta' if preco == 1150 else 'novecentos e oitenta'
        else:
            forma = formas_site[(i * 7) % len(formas_site)] if i > 2 else 'milhar'
            if forma == 'milhar':
                t_val = brl(preco)
            elif forma == 'sem_milhar':
                t_val = brl(preco, milhar=False)
            elif forma == 'inteiro':
                t_val = brl(preco, milhar=False, centavos=False)
            elif forma == 'inteiro_milhar':
                t_val = brl(preco, centavos=False)
            else:
                t_val = brl(preco, rs=True)
        linhas.append({'id_resposta': i, 'canal': canal[i], 'nascimento': t_nasc, 'categoria': t_cat,
                       'valor_pago': t_val})
        if pago:
            extrato.append({'id_resposta': i, 'valor': f'{pago:.2f}'})
    return linhas, extrato


def cronometragem(rnd):
    res = [r for r in json.load(open(TRIATLO / 'api_resultados.json', encoding='utf-8')) if r['edicao'] == 2025]
    res.sort(key=lambda r: r['numero_peito'])
    peitos = [r['numero_peito'] for r in res]
    p_jeito = separar(rnd, peitos[2:], zero_esquerda=6, decimal=8, sem_numero=2, vazio=2)
    s_jeito = separar(rnd, peitos[2:], maiuscula=10, espaco=3, minuscula=4)
    dnf = [r['numero_peito'] for r in res if r['status'] == 'DNF' and r['numero_peito'] not in s_jeito]
    for p in rnd.sample(dnf, 3):
        s_jeito[p] = 'desconhecido'
    concl = [r['numero_peito'] for r in res if r['status'] == 'concluiu' and r['numero_peito'] not in p_jeito
             and r['numero_peito'] not in s_jeito]
    nao = [r['numero_peito'] for r in res if r['status'] in ('DNF', 'DNS') and r['numero_peito'] not in s_jeito]
    t_jeito = separar(rnd, concl[2:], minuto_61=2, sem_segundos=3)
    z_jeito = separar(rnd, nao, zero=7, escrito=3)
    c_jeito = separar(rnd, [p for p in concl[2:] if p not in t_jeito], ano_trocado=2, inexistente=1)

    linhas = []
    for r in res:
        p = r['numero_peito']
        jeito = p_jeito.get(p)
        t_peito = {'zero_esquerda': f'{p:04d}', 'decimal': f'{p}.0', 'sem_numero': 's/n', 'vazio': ''}.get(jeito, str(p))
        st = r['status']
        jeito = s_jeito.get(p)
        if jeito == 'maiuscula':
            t_st = st.capitalize() if st == 'concluiu' else st.lower().capitalize()
        elif jeito == 'espaco':
            t_st = st + ' '
        elif jeito == 'minuscula':
            t_st = st.lower()
        elif jeito == 'desconhecido':
            t_st = 'abandonou'
        else:
            t_st = st
        tempo = r['tempo_oficial']
        t_tempo, t_cheg = '', ''
        if tempo:
            h, m, s = (int(x) for x in tempo.split(':'))
            cheg = LARGADA_2025 + dt.timedelta(hours=h, minutes=m, seconds=s)
            jeito = t_jeito.get(p)
            if jeito == 'minuto_61':
                t_tempo = f'{h}:{61}:{s:02d}'
            elif jeito == 'sem_segundos':
                t_tempo = f'{h}:{m:02d}'
            else:
                t_tempo = tempo
            jeito = c_jeito.get(p)
            if jeito == 'ano_trocado':
                t_cheg = cheg.strftime('%d/%m/2052 %H:%M')
            elif jeito == 'inexistente':
                t_cheg = cheg.strftime('31/04/%Y %H:%M')
            else:
                t_cheg = cheg.strftime('%d/%m/%Y %H:%M')
        else:
            jeito = z_jeito.get(p)
            if jeito == 'zero':
                t_tempo = '0:00:00'
            elif jeito == 'escrito':
                t_tempo = st
        linhas.append({'numero_peito': t_peito, 'status': t_st, 'tempo_oficial': t_tempo, 'chegada': t_cheg})
    return linhas


def gravar(nome, linhas):
    with open(AQUI / nome, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)


def main():
    rnd = random.Random(2126)
    linhas, extrato = formulario(rnd)
    gravar('formulario_2026.csv', linhas)
    gravar('extrato_tesouraria.csv', extrato)
    crono = cronometragem(rnd)
    gravar('cronometragem_2025.csv', crono)
    print(f'formulario_2026.csv: {len(linhas)} respostas | extrato_tesouraria.csv: {len(extrato)} pagamentos | '
          f'cronometragem_2025.csv: {len(crono)} atletas')


if __name__ == '__main__':
    main()
