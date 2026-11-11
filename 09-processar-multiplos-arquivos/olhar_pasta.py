"""Mostra, passo a passo, o caminho e a ordem dos arquivos da pasta exportacoes/.

    python3 olhar_pasta.py

Parte 1: o caminho que veio no script do Caio. Parte 2: caminho a partir do terminal e a partir
do programa. Parte 3: em que ordem os arquivos aparecem.
"""
import os
from pathlib import Path, PurePosixPath, PureWindowsPath

AQUI = Path(__file__).resolve().parent
MESES = {"janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7,
         "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}

print("== 1. O caminho do script do Caio")
caminho_do_caio = "C:\\Users\\caio\\Downloads\\exportacoes\\pedidos-online-julho.json"
try:
    open(caminho_do_caio, encoding="utf-8")
except FileNotFoundError as erro:
    print(type(erro).__name__, erro.strerror)
print("no Windows, as partes são:", PureWindowsPath(caminho_do_caio).parts)
print("no macOS e no Linux, as partes são:", PurePosixPath(caminho_do_caio).parts)

print("\n== 2. A partir do terminal ou a partir do programa")
os.chdir(AQUI)
print("terminal na pasta da aula, Path('exportacoes') existe?", Path("exportacoes").is_dir())
os.chdir(AQUI.parent)
print("terminal na pasta de cima, Path('exportacoes') existe?", Path("exportacoes").is_dir())
print("terminal na pasta de cima, AQUI / 'exportacoes' existe?", (AQUI / "exportacoes").is_dir())
os.chdir(AQUI)

print("\n== 3. A ordem dos arquivos")
nomes = [p.name for p in (AQUI / "exportacoes").iterdir()]
print("como a pasta entregou:", nomes)
print("sorted, pelo nome:", sorted(nomes))


def numero_do_mes(nome):
    mes = nome.removeprefix("pedidos-online-").removesuffix(".json")
    return MESES.get(mes, 99)  # nome fora do padrão vai para o fim


print("pelo número do mês:", sorted(nomes, key=numero_do_mes))
