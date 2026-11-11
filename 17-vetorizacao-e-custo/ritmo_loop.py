"""O ritmo de cada atleta de 2025, em minutos por km, na natação, no ciclismo e na corrida.

É o programa que vai para o boletim de 2025, escrito com loop.
    python3 ritmo_loop.py            # os 5 primeiros atletas e o total de linhas
    python3 ritmo_loop.py --etapas   # o tempo de cada etapa do programa

As funções podem ser importadas: ler(), converter(itens), ritmo_com_loop(lista),
escrever(linhas, ritmos) e distancias(edicao).
"""
import argparse
import csv
import io
import json

import cronometro
import parciais

EDICAO = 2025
EDICOES = parciais.ARQUIVO.parent / "edicoes.csv"


def distancias(edicao=EDICAO):
    with open(EDICOES, encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            if int(linha["edicao"]) == edicao:
                return [float(linha["natacao_km"]), float(linha["ciclismo_km"]), float(linha["corrida_km"])]
    raise SystemExit(f"Edição {edicao} não está em {EDICOES.name}")


KM = distancias()


def ler():
    return json.loads(parciais.ARQUIVO.read_text(encoding="utf-8"))


def converter(itens):
    """Quem concluiu 2025 com as cinco parciais, sem resultado repetido: (peito, [5 parciais em segundos])."""
    vistos, linhas = set(), []
    for item in itens:
        if item["id_inscricao"] in vistos:
            continue
        vistos.add(item["id_inscricao"])
        if item["edicao"] != EDICAO or item["status"] != "concluiu" or None in item["parciais"].values():
            continue
        linhas.append((item["numero_peito"], [parciais.segundos(item["parciais"][e]) for e in parciais.ETAPAS]))
    return linhas


def ritmo_com_loop(lista):
    """lista: uma lista de 5 parciais em segundos por atleta. Retorna [natação, ciclismo, corrida] em min/km."""
    ritmos = []
    for tempos in lista:
        natacao, _, ciclismo, _, corrida = tempos
        ritmos.append([natacao / 60 / KM[0], ciclismo / 60 / KM[1], corrida / 60 / KM[2]])
    return ritmos


def escrever(linhas, ritmos):
    saida = io.StringIO()
    w = csv.writer(saida)
    w.writerow(["peito", "natacao_min_km", "ciclismo_min_km", "corrida_min_km"])
    for (peito, _), r in zip(linhas, ritmos):
        w.writerow([peito] + [f"{x:.2f}" for x in r])
    return saida.getvalue()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--etapas", action="store_true")
    args = p.parse_args()
    itens = ler()
    linhas = converter(itens)
    lista = [t for _, t in linhas]
    ritmos = ritmo_com_loop(lista)
    if not args.etapas:
        print(f"Distâncias de {EDICAO} (km): {KM}")
        print(f"Atletas no boletim: {len(linhas)}")
        print(escrever(linhas[:5], ritmos[:5]), end="")
        return
    etapas = [("ler o arquivo", lambda: ler()), ("converter as parciais", lambda: converter(itens)),
              ("ritmo com loop", lambda: ritmo_com_loop(lista)), ("escrever o CSV", lambda: escrever(linhas, ritmos))]
    t = {nome: cronometro.medir(f) for nome, f in etapas}
    for nome, _ in etapas:
        print(f"{nome:<24}{cronometro.texto(t[nome]):>10}")
    print(f"{'programa inteiro':<24}{cronometro.texto(sum(t.values())):>10}")


if __name__ == "__main__":
    main()
