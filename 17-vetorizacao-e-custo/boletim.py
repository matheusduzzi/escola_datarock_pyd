"""O programa do boletim, etapa por etapa, com o tempo de cada uma.

Etapas: ler o arquivo, converter as parciais de texto para segundos, fazer as contas e
escrever o CSV do boletim. As contas existem em duas versões, com loop e com array;
o resto é igual nas duas.
    python3 boletim.py
"""
import csv
import io
import json
import statistics

import numpy as np

import cronometro
import parciais


def ler():
    return json.loads(parciais.ARQUIVO.read_text(encoding="utf-8"))


def converter(itens):
    vistos, linhas = set(), []
    for item in itens:
        if item["id_inscricao"] in vistos:
            continue
        vistos.add(item["id_inscricao"])
        if item["status"] != "concluiu" or None in item["parciais"].values():
            continue
        linhas.append((item["edicao"], item["numero_peito"],
                       [parciais.segundos(item["parciais"][e]) for e in parciais.ETAPAS]))
    return linhas


def contas_com_loop(linhas):
    total = []
    for _, _, tempos in linhas:
        soma = 0.0
        for parcial in tempos:
            soma += parcial
        total.append(soma)
    mediana = statistics.median(total)
    return [(t - mediana) / 60 for t in total]


def contas_com_array(linhas):
    tempos = np.array([t for _, _, t in linhas])
    total = tempos.sum(axis=1)
    return ((total - np.median(total)) / 60).tolist()


def escrever(linhas, minutos):
    saida = io.StringIO()
    w = csv.writer(saida)
    w.writerow(["edicao", "peito", "minutos_da_mediana"])
    for (edicao, peito, _), m in zip(linhas, minutos):
        w.writerow([edicao, peito, f"{m:.1f}"])
    return saida.getvalue()


def main():
    itens = ler()
    linhas = converter(itens)
    loop, array = contas_com_loop(linhas), contas_com_array(linhas)
    iguais = escrever(linhas, loop) == escrever(linhas, array)
    etapas = [("ler o arquivo", lambda: ler()),
              ("converter as parciais", lambda: converter(itens)),
              ("contas com loop", lambda: contas_com_loop(linhas)),
              ("contas com array", lambda: contas_com_array(linhas)),
              ("escrever o CSV", lambda: escrever(linhas, loop))]
    t = {nome: cronometro.medir(f) for nome, f in etapas}
    print(f"Resultados no arquivo: {len(itens)} | atletas no boletim: {len(linhas)} | CSV igual nas duas versões: {iguais}")
    print()
    print(f"{'etapa':<24}{'tempo':>10}")
    for nome, _ in etapas:
        print(f"{nome:<24}{cronometro.texto(t[nome]):>10}")
    resto = t["ler o arquivo"] + t["converter as parciais"] + t["escrever o CSV"]
    com_loop, com_array = resto + t["contas com loop"], resto + t["contas com array"]
    print()
    print(f"programa inteiro com loop:  {cronometro.texto(com_loop)}")
    print(f"programa inteiro com array: {cronometro.texto(com_array)}")
    print(f"as contas são {t['contas com loop'] / com_loop:.0%} do programa com loop")
    print(f"o programa inteiro ficou {com_loop / com_array:.2f} vezes mais rápido")


if __name__ == "__main__":
    main()
