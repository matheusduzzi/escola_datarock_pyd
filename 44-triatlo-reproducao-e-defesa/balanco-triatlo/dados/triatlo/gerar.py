"""Gera os dados da competição de triatlo do projeto final de Python para dados.

Só biblioteca padrão. Rodar duas vezes dá os mesmos arquivos, byte a byte.

    python3 gerar.py                  # escreve nesta pasta
    python3 gerar.py --saida /tmp/x   # escreve em outra pasta

Arquivos: edicoes.csv, atletas.csv, inscricoes_2024.csv (vírgula), inscricoes_2025.csv
(ponto e vírgula, outra origem) e api_resultados.json (servido por ../../api/servidor.py).

O que os dados têm de propósito: largada sem chegada (DNF), inscrito que não largou (DNS),
desclassificado (DSQ), parcial que o chip não marcou com tempo oficial presente, inscrito sem
nenhum resultado na API, resultado repetido na API, linha repetida no arquivo de inscrições e
natação reduzida em 2025.
"""
import argparse
import csv
import json
import random
from pathlib import Path

SEMENTE = 20260
EDICOES = [
    {'edicao': 2024, 'data_prova': '2024-05-26', 'natacao_km': '3.8', 'ciclismo_km': '180', 'corrida_km': '42.2',
     'temperatura_max_c': '24', 'observacao': 'percurso completo'},
    {'edicao': 2025, 'data_prova': '2025-05-25', 'natacao_km': '1.9', 'ciclismo_km': '180', 'corrida_km': '42.2',
     'temperatura_max_c': '31', 'observacao': 'natação reduzida por correnteza; corrida com calor'},
]
INSCRITOS = {2024: 420, 2025: 460}
EM_DUAS = 180
TOTAL_ATLETAS = INSCRITOS[2024] + INSCRITOS[2025] - EM_DUAS
# Quantidades plantadas por edição
PLANTADOS = {
    2024: {'dns': 12, 'dnf': 31, 'dsq': 3, 'parcial_vazia': 5, 'sem_resultado': 3, 'repetido_api': 2, 'repetido_inscricao': 0},
    2025: {'dns': 15, 'dnf': 44, 'dsq': 4, 'parcial_vazia': 6, 'sem_resultado': 4, 'repetido_api': 6, 'repetido_inscricao': 3},
}
ETAPAS = ['natacao', 't1', 'ciclismo', 't2', 'corrida']


def hms(seg):
    return f'{seg // 3600}:{seg % 3600 // 60:02d}:{seg % 60:02d}'


def limitado(rnd, desvio, limite=2.0):
    """Sorteio normal cortado em +-limite desvios, para não nascer tempo impossível."""
    return max(-limite, min(limite, rnd.gauss(0, 1))) * desvio


def faixa(idade):
    if idade < 25:
        return '18-24'
    if idade >= 65:
        return '65+'
    base = idade // 5 * 5
    return f'{base}-{base + 4}'


def gerar(saida):
    rnd = random.Random(SEMENTE)
    saida.mkdir(parents=True, exist_ok=True)

    atletas = []
    for i in range(1, TOTAL_ATLETAS + 1):
        atletas.append({'id_atleta': i, 'nome': f'Atleta {i:04d}', 'sexo': 'F' if rnd.random() < 0.27 else 'M',
                        'ano_nascimento': rnd.randint(1958, 2005), 'uf': rnd.choice(['SP', 'SP', 'SP', 'RJ', 'MG', 'PR', 'SC', 'RS', 'BA', 'PE'])})
    ids = [a['id_atleta'] for a in atletas]
    ids_2024 = ids[:INSCRITOS[2024]]
    duas = rnd.sample(ids_2024, EM_DUAS)
    ids_2025 = sorted(duas + ids[INSCRITOS[2024]:])
    por_id = {a['id_atleta']: a for a in atletas}

    inscricoes, resultados = {}, []
    for ed, lista in ((2024, ids_2024), (2025, ids_2025)):
        p = PLANTADOS[ed]
        linhas = []
        for n, ida in enumerate(lista, start=1):
            a = por_id[ida]
            linhas.append({'id_inscricao': f'{ed}-{n:04d}', 'id_atleta': ida, 'numero_peito': 100 + n,
                           'categoria': a['sexo'] + faixa(ed - a['ano_nascimento']),
                           'equipe': rnd.choice(['', '', '', 'Equipe Litoral', 'Equipe Serra', 'Clube Exemplo'])})
        inscricoes[ed] = linhas
        codigos = [l['id_inscricao'] for l in linhas]
        sorteio = rnd.sample(codigos, p['dns'] + p['dnf'] + p['dsq'] + p['parcial_vazia'] + p['sem_resultado'])
        i = 0
        grupos = {}
        for nome in ('dns', 'dnf', 'dsq', 'parcial_vazia', 'sem_resultado'):
            grupos[nome] = set(sorteio[i:i + p[nome]])
            i += p[nome]
        natacao_curta = EDICOES[[e['edicao'] for e in EDICOES].index(ed)]['natacao_km'] == '1.9'
        calor = ed == 2025
        itens = []
        for l in linhas:
            cod = l['id_inscricao']
            if cod in grupos['sem_resultado']:
                continue
            forca = max(-1.4, min(2.5, rnd.gauss(0.2, 0.9)))
            nat = int((1900 if natacao_curta else 4200) * (1 + 0.18 * forca + limitado(rnd, 0.06)))
            t1 = rnd.randint(180, 600)
            cic = int(21000 * (1 + 0.13 * forca + limitado(rnd, 0.05)))
            t2 = rnd.randint(120, 480)
            cor = int(15500 * (1 + 0.17 * forca + limitado(rnd, 0.07)) * (1.06 if calor else 1.0))
            tempos = dict(zip(ETAPAS, [nat, t1, cic, t2, cor]))
            item = {'edicao': ed, 'id_inscricao': cod, 'numero_peito': l['numero_peito'], 'status': 'concluiu',
                    'parciais': {e: hms(t) for e, t in tempos.items()}, 'tempo_oficial': hms(sum(tempos.values()))}
            if cod in grupos['dns']:
                item.update(status='DNS', parciais={e: None for e in ETAPAS}, tempo_oficial=None)
            elif cod in grupos['dnf']:
                parou = rnd.choice(['ciclismo', 'ciclismo', 'corrida', 'corrida', 'corrida'])
                k = ETAPAS.index(parou)
                item.update(status='DNF', parciais={e: (hms(tempos[e]) if j < k else None) for j, e in enumerate(ETAPAS)},
                            tempo_oficial=None)
            elif cod in grupos['dsq']:
                item.update(status='DSQ', tempo_oficial=None, motivo='vácuo no ciclismo' if rnd.random() < 0.7 else 'descarte fora da área')
            elif cod in grupos['parcial_vazia']:
                item['parciais'][rnd.choice(['t1', 't2'])] = None
            itens.append(item)
        # resultado repetido: mesmo item duas vezes, em lugares diferentes da lista (cai em páginas diferentes)
        for item in rnd.sample([x for x in itens if x['status'] == 'concluiu'], p['repetido_api']):
            itens.insert(min(len(itens), itens.index(item) + 50 + rnd.randint(0, 20)), json.loads(json.dumps(item)))
        resultados += itens
        # linha repetida no arquivo de inscrições
        for l in rnd.sample(linhas, p['repetido_inscricao']):
            linhas.insert(linhas.index(l) + 1, dict(l))

    with open(saida / 'edicoes.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(EDICOES[0]))
        w.writeheader()
        w.writerows(EDICOES)
    with open(saida / 'atletas.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(atletas[0]))
        w.writeheader()
        w.writerows(atletas)
    for ed, sep in ((2024, ','), (2025, ';')):
        with open(saida / f'inscricoes_{ed}.csv', 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(inscricoes[ed][0]), delimiter=sep)
            w.writeheader()
            w.writerows(inscricoes[ed])
    (saida / 'api_resultados.json').write_text(json.dumps(resultados, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    resumo = {ed: sum(1 for r in resultados if r['edicao'] == ed) for ed in INSCRITOS}
    print(f"atletas={len(atletas)} inscricoes_2024={len(inscricoes[2024])} inscricoes_2025={len(inscricoes[2025])} "
          f"resultados_2024={resumo[2024]} resultados_2025={resumo[2025]} em_duas_edicoes={EM_DUAS}")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--saida', default=str(Path(__file__).resolve().parent))
    gerar(Path(ap.parse_args().saida))
