"""Relatório de faturamento do semestre: roda do zero com um comando.

    python3 relatorio.py
    python3 relatorio.py --inicio 2026-04 --fim 2026-06
"""
import argparse
import re
from pathlib import Path

import faturamento

# A pasta de dados fica ao lado da pasta da aula, no kit. O caminho parte deste
# arquivo, e não da pasta em que o terminal está.
PASTA_DADOS = Path(__file__).resolve().parent.parent / "dados" / "loja"
MES = re.compile(r"\d{4}-\d{2}")


def main(argumentos=None):
    parser = argparse.ArgumentParser(description="Faturamento entregue por mês e categoria.")
    parser.add_argument("--inicio", default="2026-01", help="primeiro mês, AAAA-MM")
    parser.add_argument("--fim", default="2026-06", help="último mês, AAAA-MM")
    parser.add_argument("--saida", default="saida/faturamento.csv", help="arquivo CSV da tabela")
    args = parser.parse_args(argumentos)
    for nome in ("inicio", "fim"):
        if not MES.fullmatch(getattr(args, nome)):
            parser.error(f"--{nome} precisa ser AAAA-MM, por exemplo 2026-01")
    if args.inicio > args.fim:
        parser.error("--inicio vem depois de --fim")

    pedidos, produtos = faturamento.ler_base(PASTA_DADOS)
    base = faturamento.entregues_com_categoria(pedidos, produtos)
    base = faturamento.no_periodo(base, args.inicio, args.fim)
    tabela = faturamento.por_mes_e_categoria(base)

    saida = Path(args.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(saida)

    print(f"Faturamento entregue de {args.inicio} a {args.fim}, em R$")
    print(tabela.to_string())
    print("Total:", round(tabela.sum().sum(), 2))
    print("Pedidos entregues sem valor anotado:", int(base["valor"].isna().sum()))
    print("Tabela gravada em", saida)


if __name__ == "__main__":
    main()
