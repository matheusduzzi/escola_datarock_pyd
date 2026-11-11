"""Fechamento do mês: faturamento dos pedidos entregues, por categoria.

Versão depois da aula «Depurar e tratar exceções».
- Pedido entregue sem valor (o caixa não anotou) fica fora da soma e é contado.
- Valor que não é número ou produto fora do cadastro é problema do arquivo: o programa
  lista todas as linhas com problema, não grava nada e termina com o código 1.
- Arquivo que não existe também termina com o código 1 e uma mensagem.
"""
import argparse
import csv
import logging
import sys
from pathlib import Path

PRODUTOS = Path(__file__).resolve().parent.parent / "dados" / "loja" / "produtos.csv"
log = logging.getLogger("fechamento")


class ArquivoComProblema(Exception):
    """O arquivo de pedidos tem linhas que o programa não sabe ler. Quem corrige é quem mandou o arquivo."""

    def __init__(self, caminho, problemas):
        super().__init__(f"{caminho}: {len(problemas)} linha(s) com problema")
        self.problemas = problemas


def ler_categorias(caminho):
    """Dicionário id_produto -> categoria, lido do cadastro de produtos."""
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return {linha["id_produto"]: linha["categoria"] for linha in csv.DictReader(arquivo)}


def ler_valor(texto):
    """Valor do pedido em reais. Vazio quer dizer que o caixa não anotou: retorna None."""
    if texto == "":
        return None
    return float(texto)


def somar_por_categoria(caminho_pedidos, categorias):
    """Retorna (totais por categoria, pedidos entregues sem valor). Levanta ArquivoComProblema."""
    totais = {}
    sem_valor = 0
    problemas = []
    with open(caminho_pedidos, encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            if linha["status"] != "entregue":
                continue
            onde = f"linha {leitor.line_num}, pedido {linha['id_pedido']}"
            try:
                valor = ler_valor(linha["valor"])
            except ValueError:
                problemas.append(f"{onde}: valor {linha['valor']!r} não é número no formato 1234.56")
                continue
            categoria = categorias.get(linha["id_produto"])
            if categoria is None:
                problemas.append(f"{onde}: produto {linha['id_produto']!r} não está em produtos.csv")
                continue
            if valor is None:
                sem_valor += 1
                continue
            totais[categoria] = totais.get(categoria, 0) + valor
    if problemas:
        raise ArquivoComProblema(caminho_pedidos, problemas)
    return totais, sem_valor


def gravar(totais, caminho):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo, lineterminator="\n")
        escritor.writerow(["categoria", "faturamento"])
        for categoria in sorted(totais):
            escritor.writerow([categoria, f"{totais[categoria]:.2f}"])


def main(argumentos=None):
    logging.basicConfig(format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Faturamento entregue por categoria.")
    parser.add_argument("--arquivo", default="pedidos-julho.csv", help="CSV de pedidos do mês")
    parser.add_argument("--saida", default="saida/fechamento.csv", help="CSV da tabela")
    args = parser.parse_args(argumentos)

    try:
        totais, sem_valor = somar_por_categoria(args.arquivo, ler_categorias(PRODUTOS))
    except FileNotFoundError as erro:
        log.error("não achei o arquivo %r. Rode o comando de dentro da pasta da aula.", erro.filename)
        return 1
    except ArquivoComProblema as erro:
        log.error("%s. Nada foi gravado.", erro)
        for problema in erro.problemas:
            log.error("  %s", problema)
        log.error("Peça o arquivo corrigido para quem mandou e rode de novo.")
        return 1

    print(f"Faturamento entregue de {args.arquivo}, em R$")
    for categoria in sorted(totais):
        print(f"{categoria:<10} {totais[categoria]:>10.2f}")
    print(f"Total: {sum(totais.values()):.2f}")
    print(f"Pedidos entregues sem valor anotado: {sem_valor}")
    gravar(totais, Path(args.saida))
    print(f"Tabela gravada em {args.saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
