"""Roda os testes numa cópia desta pasta, longe do resto do kit. Aula «Isolar API e arquivos nos testes».

De dentro da pasta da aula:
    python3 rodar_sozinho.py                  roda test_coleta.py
    python3 rodar_sozinho.py test_exercicio.py

A cópia vai para uma pasta temporária, sem ../dados e sem ../api. Se um teste ainda depender da API,
dos arquivos do triatlo ou de algum arquivo fora da pasta, ele falha lá. No fim, o programa diz se algum
teste criou ou mudou arquivo na própria pasta dos testes.
Sai com o código do pytest, ou com 2 se o pytest não está instalado.
"""
import hashlib
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
IGNORAR = shutil.ignore_patterns('__pycache__', '.pytest_cache')


def retrato(pasta):
    """O conteúdo de cada arquivo da pasta, para comparar antes e depois."""
    return {str(p.relative_to(pasta)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(pasta.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


def main():
    if importlib.util.find_spec('pytest') is None:
        print('O pytest não está instalado nesse Python. Rode: python3 -m pip install pytest')
        return 2
    arquivo = sys.argv[1] if len(sys.argv) > 1 else 'test_coleta.py'
    with tempfile.TemporaryDirectory() as tmp:
        copia = Path(tmp) / 'sozinha'
        shutil.copytree(AQUI, copia, ignore=IGNORAR)
        print(f'pasta copiada sozinha, sem ../dados e sem ../api: {len(retrato(copia))} arquivos')
        antes = retrato(copia)
        r = subprocess.run([sys.executable, '-B', '-m', 'pytest', '-q', '-p', 'no:cacheprovider', '--tb=no', '-rf', arquivo],
                           cwd=copia, capture_output=True, text=True)
        print(r.stdout.rstrip())
        depois = retrato(copia)
    mudaram = sorted(k for k in antes.keys() | depois.keys() if antes.get(k) != depois.get(k))
    print('arquivos que os testes criaram ou mudaram na pasta: ' + (', '.join(mudaram) if mudaram else 'nenhum'))
    return r.returncode


if __name__ == '__main__':
    sys.exit(main())
