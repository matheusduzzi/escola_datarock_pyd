"""Gera o recuperados.json do exercício: os resultados que a cronometragem achou depois da prova.

Só biblioteca padrão. Rodar duas vezes dá o mesmo arquivo, byte a byte.

    python3 gerar.py                  # escreve nesta pasta
    python3 gerar.py --saida /tmp/x   # escreve em outra pasta
    python3 gerar.py --dados outra    # lê os arquivos de inscrição de outra pasta

Os números de peito vêm dos arquivos de inscrição do kit, em ../../dados/triatlo/.
Os tempos estão escritos abaixo, um resultado por linha, no formato da API.
"""
import argparse
import csv
import json
from pathlib import Path

DADOS = Path(__file__).resolve().parent.parent.parent / "dados" / "triatlo"
ETAPAS = ["natacao", "t1", "ciclismo", "t2", "corrida"]

# id_inscricao, status, cinco parciais (None = o chip não marcou ou a etapa não aconteceu),
# e quanto o tempo oficial passa da soma das parciais, em segundos (None = sem tempo oficial)
RESULTADOS = [
    ("2024-0126", "concluiu", ["1:15:02", "0:05:41", "6:01:30", "0:04:58", "4:40:11"], 0),
    ("2024-0168", "DNS", [None, None, None, None, None], None),
    ("2024-0180", "DNF", ["1:22:10", "0:06:02", None, None, None], None),
    ("2025-0234", "concluiu", ["0:36:48", "0:04:20", "5:58:41", None, "4:51:09"], 5 * 60 + 12),
    ("2025-0235", "DNF", ["0:35:40", "0:04:31", "6:20:05", "0:06:10", None], None),
    ("2025-0235", "DNF", ["0:35:40", "0:04:31", "6:20:05", "0:06:10", None], None),
    ("2025-0383", "concluiu", ["0:31:15", "0:03:58", "5:41:22", "0:04:05", "4:12:40"], 10 * 60),
    ("2025-0101", "DNF", None, None),   # a API já mandou este; aqui ele vem como DNF
    ("2025-0200", None, None, None),    # a API já mandou este; aqui ele vem igual
    ("2025-0999", "concluiu", ["0:33:10", "0:04:02", "5:50:09", "0:03:51", "4:20:33"], 0),
]


def segundos(texto):
    h, m, s = (int(p) for p in texto.split(":"))
    return h * 3600 + m * 60 + s


def hms(total):
    return f"{total // 3600}:{total % 3600 // 60:02d}:{total % 60:02d}"


def peitos(dados):
    saida = {}
    for nome, sep in [("inscricoes_2024.csv", ","), ("inscricoes_2025.csv", ";")]:
        with open(dados / nome, encoding="utf-8", newline="") as f:
            for linha in csv.DictReader(f, delimiter=sep):
                saida[linha["id_inscricao"]] = int(linha["numero_peito"])
    return saida


def da_api(dados, id_inscricao):
    itens = json.loads((dados / "api_resultados.json").read_text(encoding="utf-8"))
    return next(r for r in itens if r["id_inscricao"] == id_inscricao)


def montar(dados=DADOS):
    peito = peitos(dados)
    saida = []
    for id_inscricao, status, parciais, a_mais in RESULTADOS:
        if parciais is None:  # um resultado que a API já mandou
            r = dict(da_api(dados, id_inscricao))
            if status == "DNF":
                r.update(status="DNF", parciais=dict(r["parciais"], corrida=None), tempo_oficial=None)
            saida.append(r)
            continue
        r = {"edicao": int(id_inscricao[:4]), "id_inscricao": id_inscricao,
             "numero_peito": peito.get(id_inscricao, 999), "status": status,
             "parciais": dict(zip(ETAPAS, parciais)), "tempo_oficial": None}
        if a_mais is not None:
            r["tempo_oficial"] = hms(sum(segundos(p) for p in parciais if p) + a_mais)
        saida.append(r)
    return saida


def main():
    ap = argparse.ArgumentParser(description="Gera o recuperados.json do exercício")
    ap.add_argument("--saida", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--dados", default=str(DADOS))
    a = ap.parse_args()
    pasta = Path(a.saida)
    pasta.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(montar(Path(a.dados)), ensure_ascii=False, indent=1) + "\n"
    (pasta / "recuperados.json").write_text(texto, encoding="utf-8")
    print(f"gravei {pasta / 'recuperados.json'}")


if __name__ == "__main__":
    main()
