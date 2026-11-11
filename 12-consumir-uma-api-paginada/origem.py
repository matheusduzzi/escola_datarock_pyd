"""Mostra de onde veio cada linha de uma inscrição, num arquivo gravado pelo coletar.py.

    python3 origem.py resultados-2025.json 2025-0228

Para cada linha daquela inscrição: a página, a posição e a chamada que trouxe a página.
"""
import json
import sys


def main():
    if len(sys.argv) != 3:
        print("uso: python3 origem.py ARQUIVO ID_INSCRICAO", file=sys.stderr)
        return 2
    arquivo, chave = sys.argv[1], sys.argv[2]
    with open(arquivo, encoding="utf-8") as f:
        dados = json.load(f)
    chamadas = {p["pagina"]: p["chamada"] for p in dados["coleta"]["paginas"]}
    achadas = [l for l in dados["linhas"] if l["id_inscricao"] == chave]
    print(f"{chave}: {len(achadas)} linha(s) em {arquivo}, coletado em {dados['coleta']['coletado_em']}")
    for linha in achadas:
        o = linha["origem"]
        print(f"  página {o['pagina']} posição {o['posicao']}: GET {chamadas[o['pagina']]}")
        print(f"    status {linha['status']}, tempo_oficial {linha['tempo_oficial']}")
    return 0 if achadas else 1


if __name__ == "__main__":
    sys.exit(main())
