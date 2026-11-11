"""Compara o que o balanço gravou em saida/ com os hashes de esperado.sha256.

De dentro da pasta do projeto, depois do balanco.py:
    python3 conferir.py             # compara
    python3 conferir.py --gravar    # grava esperado.sha256 com os arquivos de agora

O esperado.sha256 tem uma linha por arquivo, no formato do sha256sum e do shasum -a 256:
o hash, dois espaços e o caminho. Só use --gravar quando souber por que os bytes mudaram.

Código de saída:
  0  todos os arquivos iguais ao esperado
  1  algum arquivo diferente ou faltando (com --gravar: faltou arquivo e nada foi gravado)
  2  não achei o esperado.sha256
"""
import argparse
import hashlib
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ESPERADO = "esperado.sha256"
ARQUIVOS = ["saida/base_triatlo.csv", "saida/relatorio/relatorio.md",
            "saida/relatorio/figuras/etapas.png", "saida/relatorio/figuras/categorias.png"]


def sha256(caminho):
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def ler_esperado(arquivo):
    esperado = {}
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        if linha.strip():
            h, caminho = linha.split(None, 1)
            esperado[caminho.strip()] = h
    return esperado


def comparar(pasta=None):
    """Retorna (iguais, linhas da tela, total). Arquivo faltando conta como diferente."""
    pasta = Path(pasta or AQUI)
    esperado = ler_esperado(pasta / ESPERADO)
    linhas, iguais = [], 0
    for caminho, h in esperado.items():
        arquivo = pasta / caminho
        if not arquivo.is_file():
            linhas.append(f"faltando   {caminho}")
            continue
        saiu = sha256(arquivo)
        if saiu == h:
            iguais += 1
            linhas.append(f"igual      {caminho}")
        else:
            linhas.append(f"diferente  {caminho} (esperado {h[:12]}, saiu {saiu[:12]})")
    return iguais, linhas, len(esperado)


def gravar(pasta=None):
    pasta = Path(pasta or AQUI)
    faltando = [c for c in ARQUIVOS if not (pasta / c).is_file()]
    if faltando:
        return faltando
    with open(pasta / ESPERADO, "w", encoding="utf-8", newline="\n") as f:
        for c in ARQUIVOS:
            f.write(f"{sha256(pasta / c)}  {c}\n")
    return []


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--gravar", action="store_true", help="grava esperado.sha256 com os arquivos de agora")
    a = ap.parse_args(argv)
    if a.gravar:
        faltando = gravar()
        if faltando:
            print("ERROR faltam arquivos, rode o balanco.py antes: " + ", ".join(faltando) + ". Nada foi gravado.")
            return 1
        print(f"gravei {ESPERADO} com {len(ARQUIVOS)} arquivos")
        return 0
    if not (AQUI / ESPERADO).is_file():
        print(f"ERROR não achei {ESPERADO} na pasta do projeto")
        return 2
    iguais, linhas, total = comparar()
    print("\n".join(linhas))
    if iguais == total:
        print(f"{iguais} de {total} iguais: reproduziu")
        return 0
    print(f"{iguais} de {total} iguais: não reproduziu")
    return 1


if __name__ == "__main__":
    sys.exit(main())
