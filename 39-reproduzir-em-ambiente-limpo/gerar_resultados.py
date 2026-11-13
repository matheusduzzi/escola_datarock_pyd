"""Gera tempos-por-etapa/dados/resultados.csv, os resultados da prova de triatlo de longa distância do curso.

Uso, de dentro da pasta da aula:  python3 gerar_resultados.py
Só usa a biblioteca padrão. A sequência de sorteios é fixa: rodar de novo grava o mesmo arquivo, byte a byte.
"""
import csv
import random
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parent / "tempos-por-etapa" / "dados" / "resultados.csv"
CATEGORIAS = [("Júnior", 8, 0.97), ("Adulto", 14, 1.0), ("Master", 12, 1.04), ("Sênior", 6, 1.12)]
ETAPAS = [("natacao_s", 3600, 5000), ("t1_s", 240, 520), ("ciclismo_s", 18500, 23500),
          ("t2_s", 180, 420), ("corrida_s", 12600, 19800)]


def main():
    sorteio = random.Random(39)
    linhas = []
    n = 0
    for categoria, quantos, ritmo in CATEGORIAS:
        for _ in range(quantos):
            n += 1
            sorte = sorteio.random()
            status = "DNS" if sorte < 0.05 else "DNF" if sorte < 0.15 else "terminou"
            # DNF: para depois da natação, do ciclismo ou da T2; as parciais seguintes ficam vazias.
            ate = len(ETAPAS) if status == "terminou" else 0 if status == "DNS" else sorteio.choice([1, 3, 4])
            tempos = []
            for i, (_, minimo, maximo) in enumerate(ETAPAS):
                valor = round(sorteio.uniform(minimo, maximo) * ritmo)
                tempos.append(str(valor) if i < ate else "")
            linhas.append([f"T{n:03d}", categoria, status] + tempos)
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    with open(ARQUIVO, "w", encoding="utf-8", newline="") as saida:
        escritor = csv.writer(saida, lineterminator="\n")
        escritor.writerow(["id_atleta", "categoria", "status"] + [nome for nome, _, _ in ETAPAS])
        escritor.writerows(linhas)
    print(f"{len(linhas)} atletas gravados em {ARQUIVO.relative_to(ARQUIVO.parent.parent.parent)}")


if __name__ == "__main__":
    main()
