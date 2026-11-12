"""Gera revisada/api_resultados.json: os resultados do triatlo depois da revisão da cronometragem.

    python3 gerar_revisada.py

Parte de ../dados/triatlo/api_resultados.json e muda só o que a cronometragem revisou em 2025.
Sempre escreve o mesmo arquivo. Para servir os dados revisados, de dentro desta pasta:

    python3 api_revisada.py
"""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ORIGEM = AQUI.parent / "dados" / "triatlo" / "api_resultados.json"
DESTINO = AQUI / "revisada" / "api_resultados.json"

# O que a cronometragem revisou em 2025, inscrição por inscrição.
CORRECOES = {
    # o chip da corrida foi lido de novo: 1 min 30 s a mais
    "2025-0007": {"parciais": {"corrida": "4:45:27"}, "tempo_oficial": "11:29:50"},
    # a primeira transição tinha 5 min a mais; a inscrição vem duas vezes na API, e as duas mudam
    "2025-0228": {"parciais": {"t1": "0:04:55"}, "tempo_oficial": "9:29:49"},
    # desclassificação depois do recurso de outra equipe
    "2025-0350": {"status": "DSQ", "tempo_oficial": None, "motivo": "atalho na corrida"},
}
CANCELADAS = {"2025-0384"}  # inscrição cancelada: sai da lista


def revisar(resultados):
    revisados = []
    for item in resultados:
        if item["edicao"] != 2025:
            revisados.append(item)
            continue
        if item["id_inscricao"] in CANCELADAS:
            continue
        novo = json.loads(json.dumps(item))
        for campo, valor in CORRECOES.get(item["id_inscricao"], {}).items():
            if campo == "parciais":
                novo["parciais"].update(valor)
            else:
                novo[campo] = valor
        revisados.append(novo)
    return revisados


def main():
    resultados = json.loads(ORIGEM.read_text(encoding="utf-8"))
    revisados = revisar(resultados)
    DESTINO.parent.mkdir(exist_ok=True)
    DESTINO.write_text(json.dumps(revisados, ensure_ascii=False), encoding="utf-8")
    de_2025 = [r for r in revisados if r["edicao"] == 2025]
    print(f"gravei {DESTINO.relative_to(AQUI)}: {len(revisados)} resultados, {len(de_2025)} de 2025")


if __name__ == "__main__":
    main()
