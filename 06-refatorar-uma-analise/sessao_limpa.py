"""Roda um script ou um notebook do zero, duas vezes, e diz se as duas saídas batem.

Uso, de dentro da pasta da aula:

    python3 sessao_limpa.py relatorio.py
    python3 sessao_limpa.py relatorio.py --inicio 2026-04 --fim 2026-06
    python3 sessao_limpa.py faturamento-do-semestre.ipynb

O programa copia a pasta da aula e a pasta ../dados para uma pasta temporária, sem a
pasta saida/, sem __pycache__ e sem .ipynb_checkpoints. Lá, ele abre um Python novo,
que não herda nenhuma variável do seu terminal nem do seu notebook, e roda o arquivo.
Um notebook roda célula por célula, de cima para baixo, como "Restart" e "Run All".
Depois repete tudo numa segunda cópia e compara o que foi impresso e os arquivos
gravados em saida/.

Códigos de saída: 0 quando as duas execuções terminam bem e batem; 1 quando a
execução para com erro; 3 quando as duas terminam mas a saída muda de uma para outra.
"""
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

IGNORAR = shutil.ignore_patterns('saida', '__pycache__', '.ipynb_checkpoints')

# Roda as células de código na ordem do arquivo, num só espaço de nomes.
# A última linha de uma célula, se for uma expressão, é mostrada como no Jupyter.
EXECUTOR_NOTEBOOK = r'''
import ast, json, sys
nb = json.load(open(sys.argv[1], encoding="utf-8"))
espaco = {"__name__": "__main__", "display": print}
n = 0
for celula in nb["cells"]:
    if celula["cell_type"] != "code":
        continue
    n += 1
    fonte = "".join(celula["source"])
    salvo = celula.get("execution_count")
    print(f"== célula {n} (no arquivo estava In [{salvo if salvo is not None else ' '}])")
    try:
        arvore = ast.parse(fonte)
        ultima = None
        if arvore.body and isinstance(arvore.body[-1], ast.Expr):
            ultima = ast.Expression(arvore.body.pop().value)
        exec(compile(arvore, f"célula {n}", "exec"), espaco)
        if ultima is not None:
            valor = eval(compile(ultima, f"célula {n}", "eval"), espaco)
            if valor is not None:
                print(repr(valor))
    except Exception as erro:
        print(f"A célula {n} parou: {type(erro).__name__}: {erro}")
        sys.exit(1)
print(f"As {n} células rodaram de cima para baixo.")
'''


def copiar(aula, destino):
    kit = destino / 'kit'
    shutil.copytree(aula, kit / aula.name, ignore=IGNORAR)
    dados = aula.parent / 'dados'
    if dados.is_dir():
        shutil.copytree(dados, kit / 'dados', ignore=IGNORAR)
    return kit / aula.name


def rodar(arquivo, argumentos):
    aula = Path.cwd()
    with tempfile.TemporaryDirectory() as tmp:
        pasta = copiar(aula, Path(tmp))
        # -E ignora PYTHONPATH e afins: o import só funciona se o arquivo estiver na pasta.
        if arquivo.endswith('.ipynb'):
            cmd = [sys.executable, '-E', '-c', EXECUTOR_NOTEBOOK, arquivo]
        else:
            cmd = [sys.executable, '-E', arquivo, *argumentos]
        r = subprocess.run(cmd, cwd=pasta, capture_output=True, text=True)
        gravados = {}
        saida = pasta / 'saida'
        if saida.is_dir():
            for f in sorted(saida.rglob('*')):
                if f.is_file():
                    gravados[str(f.relative_to(pasta))] = hashlib.sha256(f.read_bytes()).hexdigest()
        return r.returncode, r.stdout, r.stderr, gravados


def main():
    if len(sys.argv) < 2:
        print('Uso: python3 sessao_limpa.py ARQUIVO [argumentos do arquivo]')
        return 2
    arquivo, argumentos = sys.argv[1], sys.argv[2:]
    if not Path(arquivo).is_file():
        print(f'Não achei {arquivo} nesta pasta. Rode de dentro da pasta da aula.')
        return 2
    print(f'Rodando {arquivo} num Python novo, numa cópia limpa da pasta.\n')
    execucoes = []
    for vez in (1, 2):
        codigo, out, err, gravados = rodar(arquivo, argumentos)
        if vez == 1:
            print(out, end='' if out.endswith('\n') or not out else '\n')
        if codigo != 0:
            if err:
                print(err.strip().splitlines()[-1])
            print(f'\nA execução {vez} parou com o código {codigo}.')
            return 1
        execucoes.append((out, gravados))
    (out1, grav1), (out2, grav2) = execucoes
    resumo = hashlib.sha256(out1.encode('utf-8')).hexdigest()[:12]
    for nome, sha in grav1.items():
        print(f'Gravou {nome} ({sha[:12]})')
    if out1 == out2 and grav1 == grav2:
        print(f'\nAs duas execuções terminaram bem e deram a mesma saída ({resumo}).')
        return 0
    print('\nAs duas execuções terminaram, mas a saída mudou de uma para a outra.')
    return 3


if __name__ == '__main__':
    sys.exit(main())
