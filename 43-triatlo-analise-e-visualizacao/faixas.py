"""O exercício: comparar dois grupos de idade nas duas edições, para a pergunta da Lívia.

Você escreve a função comparar_faixas. Depois, de dentro da pasta da aula:
    python3 faixas.py
    python3 -m pytest -q test_faixas.py
"""
import sys

import pandas as pd

import analise


def faixa(categoria, corte=50):
    """'M55-59' vira '50 ou mais' e 'F45-49' vira 'até 49', com corte=50. A idade é o número que vem depois da letra."""
    raise NotImplementedError("escreva a função faixa")


def comparar_faixas(base, corte=50):
    """Uma linha por grupo e edição, com o índice (grupo, edicao) e estas colunas:

    largaram          quem largou: concluiu, DNF ou DSQ
    dnf               quantos DNF
    dnf_pct           dnf dividido por largaram, em %
    dnf_corrida       quantos DNF pararam na corrida (use analise.onde_parou)
    concluiram        quantos concluíram e têm tempo de corrida
    corrida_mediana   mediana da corrida de quem concluiu, em minutos, sem tempo vazio
    """
    raise NotImplementedError("escreva a função comparar_faixas")


def main():
    base = analise.ler_base()
    try:
        tabela = comparar_faixas(base)
    except NotImplementedError as erro:
        print(f"ERROR {erro}", file=sys.stderr)
        return 1
    pd.set_option("display.width", 120)
    print(tabela.round(1).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
