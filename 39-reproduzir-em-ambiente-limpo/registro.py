"""Segue o README de um projeto numa cópia limpa e escreve o registro de execução.

Uso, de dentro da pasta da aula, com o Python do ambiente do projeto:
    tempos-por-etapa/.venv/bin/python registro.py tempos-por-etapa
    tempos-por-etapa/.venv/bin/python registro.py tempos-por-etapa --como-windows
    tempos-por-etapa/.venv/bin/python registro.py tempos-por-etapa --salvar meu-registro.md
No Windows, o Python do ambiente fica em tempos-por-etapa\\.venv\\Scripts\\python.exe.

O programa lê o bloco de comandos da seção "## Como rodar" do README do projeto e:
- copia o projeto para uma pasta temporária, sem o que o .gitignore tira (é o que o Git levaria);
- no passo de criar o ambiente (-m venv), só anota: esse passo é seu, antes do registro;
- no passo do pip install -r ARQUIVO, compara o que está instalado nesse Python com o ARQUIVO;
- roda cada comando de Python na cópia, com o mesmo Python e as mesmas opções com que você chamou o registro;
- outro tipo de linha (cp, copy, cd) não roda: o registro avisa e não diz que reproduziu.
Com --como-windows, os comandos rodam com o open() lendo arquivos em cp1252, a página de código
que o Windows costuma usar em português, no lugar do UTF-8.

Só usa a biblioteca padrão. Não instala nada e não mexe na pasta do projeto.
Códigos de saída: 0 reproduziu; 1 algum passo falhou ou o ambiente não bate com a lista; 2 uso errado
(projeto, README ou seção "Como rodar" não encontrados).
"""
import argparse
import datetime
import fnmatch
import hashlib
import importlib.metadata as md
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Ferramentas de instalação que todo ambiente novo traz; não contam como pacote a mais.
FERRAMENTAS = {'pip', 'setuptools', 'wheel'}
SEMPRE_FORA = {'.git', '.venv', 'venv', '__pycache__'}

# Roda o comando com o open() lendo em cp1252 quando ninguém diz a codificação (imitação do Windows).
COMO_WINDOWS = r'''
import builtins, io, runpy, sys
_open = io.open
def _open_cp1252(arquivo, mode="r", buffering=-1, encoding=None, *args, **kwargs):
    if "b" not in mode and encoding is None:
        encoding = "cp1252"
    return _open(arquivo, mode, buffering, encoding, *args, **kwargs)
builtins.open = io.open = _open_cp1252
args = sys.argv[1:]
if args[0] == "-m":
    sys.argv = [args[1]] + args[2:]
    runpy.run_module(args[1], run_name="__main__", alter_sys=True)
else:
    sys.argv = args
    runpy.run_path(args[0], run_name="__main__")
'''


def normal(nome):
    return re.sub(r'[-_.]+', '-', nome).lower()


def ler_gitignore(projeto):
    arquivo = projeto / '.gitignore'
    if not arquivo.is_file():
        return []
    padroes = []
    for linha in arquivo.read_text(encoding='utf-8').splitlines():
        linha = linha.strip()
        if linha and not linha.startswith('#'):
            padroes.append(linha)
    return padroes


def ignorado(relativo, padroes):
    """Versão curta das regras do .gitignore: nome, pasta/ e curingas como *.csv."""
    partes = relativo.split('/')
    if any(p in SEMPRE_FORA for p in partes):
        return True
    fora = False
    for padrao in padroes:
        nega = padrao.startswith('!')
        padrao = padrao[1:] if nega else padrao
        so_pasta = padrao.endswith('/')
        padrao = padrao.strip('/')
        if '/' in padrao:
            bate = fnmatch.fnmatch(relativo, padrao) or relativo.startswith(padrao + '/')
        else:
            alvos = partes[:-1] if so_pasta else partes
            bate = any(fnmatch.fnmatch(p, padrao) for p in alvos)
        if bate:
            fora = not nega
    return fora


def copia_limpa(projeto, destino):
    padroes = ler_gitignore(projeto)
    levados, deixados = [], []
    for item in sorted(projeto.rglob('*')):
        if not item.is_file():
            continue
        relativo = item.relative_to(projeto).as_posix()
        if ignorado(relativo, padroes):
            if not any(p in SEMPRE_FORA for p in relativo.split('/')):
                deixados.append(relativo)
            continue
        alvo = destino / relativo
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, alvo)
        levados.append(relativo)
    return levados, deixados


def comandos_do_readme(projeto):
    readme = projeto / 'README.md'
    if not readme.is_file():
        return None
    texto = readme.read_text(encoding='utf-8')
    secao = re.search(r'^## Como rodar\s*$(.*?)(?=^## |\Z)', texto, flags=re.M | re.S)
    if not secao:
        return None
    bloco = re.search(r'```[a-z]*\n(.*?)```', secao.group(1), flags=re.S)
    if not bloco:
        return None
    return [l.strip() for l in bloco.group(1).splitlines() if l.strip() and not l.strip().startswith('#')]


def eh_python(palavra):
    nome = re.split(r'[\\/]', palavra)[-1].lower()
    return re.fullmatch(r'(python(3(\.\d+)?)?|py)(\.exe)?', nome) is not None


def opcoes_do_python():
    """As opções com que este Python foi chamado, para os comandos rodarem do mesmo jeito."""
    f = sys.flags
    if f.isolated:
        opcoes = ['-I']
    else:
        opcoes = (['-E'] if f.ignore_environment else []) + (['-s'] if f.no_user_site else [])
    return opcoes + (['-S'] if f.no_site else [])


def ler_lista(arquivo, vistos=None):
    """Nome e versão pedida de cada linha. Aceita comentário e -r outro-arquivo."""
    vistos = vistos if vistos is not None else set()
    vistos.add(arquivo.resolve())
    pedidos, cabecalho = {}, ''
    for linha in arquivo.read_text(encoding='utf-8').splitlines():
        if not cabecalho and linha.startswith('#'):
            cabecalho = linha.lstrip('# ').strip()
        linha = linha.split('#', 1)[0].strip()
        if not linha:
            continue
        if linha.startswith(('-r ', '--requirement ')):
            outro = arquivo.parent / linha.split(None, 1)[1]
            if outro.resolve() not in vistos:
                pedidos.update(ler_lista(outro, vistos)[0])
            continue
        m = re.match(r'([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*([^;]*)', linha)
        if m:
            pedidos[normal(m.group(1))] = m.group(2).strip()
    return pedidos, cabecalho


def versao_tupla(v):
    return tuple(int(x) for x in re.findall(r'\d+', v.split('+')[0])[:4])


def atende(instalada, pedido):
    """Confere versão contra ==, !=, >=, <=, > e <, separados por vírgula."""
    for parte in filter(None, (p.strip() for p in pedido.split(','))):
        m = re.match(r'(==|!=|>=|<=|>|<|~=)\s*(\S+)', parte)
        if not m:
            continue
        op, alvo = m.groups()
        if op == '==':
            if alvo.endswith('.*'):
                if versao_tupla(instalada)[:len(versao_tupla(alvo))] != versao_tupla(alvo):
                    return False
            elif instalada != alvo:
                return False
            continue
        a, b = versao_tupla(instalada), versao_tupla(alvo)
        n = max(len(a), len(b))
        a, b = a + (0,) * (n - len(a)), b + (0,) * (n - len(b))
        if not {'!=': a != b, '>=': a >= b, '<=': a <= b, '>': a > b, '<': a < b, '~=': a >= b}[op]:
            return False
    return True


def instalados():
    dists = {}
    for d in md.distributions():
        nome = d.metadata.get('Name')
        if nome and normal(nome) not in dists:
            dists[normal(nome)] = d.version
    return dists


def conferir_lista(arquivo):
    pedidos, cabecalho = ler_lista(arquivo)
    dists = instalados()
    certos, diferentes, faltando = [], [], []
    for nome, pedido in sorted(pedidos.items()):
        if nome not in dists:
            faltando.append(f'{nome} {pedido}'.strip())
        elif pedido and not atende(dists[nome], pedido):
            diferentes.append(f'{nome}: pedido {pedido}, instalado {dists[nome]}')
        else:
            certos.append(nome)
    a_mais = sorted(n for n in dists if n not in pedidos and n not in FERRAMENTAS)
    linhas = []
    if cabecalho:
        linhas.append(f'   cabeçalho da lista: {cabecalho}')
    linhas.append(f'   na lista: {len(pedidos)} | instalados como pedido: {len(certos)} | '
                  f'diferentes: {len(diferentes)} | faltando: {len(faltando)}')
    linhas += [f'   diferente: {x}' for x in diferentes]
    linhas += [f'   faltando: {x}' for x in faltando]
    if a_mais:
        exemplo = ', '.join(a_mais[:6]) + (', ...' if len(a_mais) > 6 else '')
        linhas.append(f'   fora da lista, nesse Python: {len(a_mais)} ({exemplo})')
    else:
        linhas.append('   fora da lista, nesse Python: nenhum')
    return not (diferentes or faltando or a_mais), linhas


def rodar(palavras, copia, como_windows):
    base = [sys.executable] + opcoes_do_python()
    if como_windows:
        base += ['-X', 'utf8=0', '-c', COMO_WINDOWS]
    env = dict(os.environ, PYTHONIOENCODING='utf-8', COLUMNS='100')
    r = subprocess.run(base + palavras[1:], cwd=copia, env=env, capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    texto = (r.stdout + r.stderr).rstrip()
    for caminho in sorted({str(copia), str(copia.resolve())}, key=len, reverse=True):
        texto = texto.replace(caminho, '<cópia>')
    return r.returncode, texto.splitlines()


def gerados(copia, levados):
    novos = []
    for item in sorted(copia.rglob('*')):
        relativo = item.relative_to(copia).as_posix()
        if item.is_file() and relativo not in levados and '__pycache__' not in relativo \
                and '.pytest_cache' not in relativo:
            sha = hashlib.sha256(item.read_bytes()).hexdigest()[:12]
            novos.append(f'   {relativo} (sha256 {sha}...)')
    return novos


def codificacao(como_windows):
    if como_windows:
        return 'cp1252 (imitando o Windows em português)'
    if sys.flags.utf8_mode:
        return 'UTF-8 (modo UTF-8 do Python)'
    import locale
    return locale.getpreferredencoding(False)


def main():
    parser = argparse.ArgumentParser(description='Segue o README de um projeto numa cópia limpa.')
    parser.add_argument('projeto', help='pasta do projeto, a que tem o README.md')
    parser.add_argument('--como-windows', action='store_true',
                        help='roda os comandos com o open() lendo em cp1252, como no Windows')
    parser.add_argument('--salvar', metavar='ARQUIVO', help='grava o registro também nesse arquivo')
    args = parser.parse_args()

    projeto = Path(args.projeto).resolve()
    if not projeto.is_dir():
        print(f'não achei a pasta do projeto: {args.projeto}')
        return 2
    comandos = comandos_do_readme(projeto)
    if not comandos:
        print(f'não achei um bloco de comandos na seção "## Como rodar" de {args.projeto}/README.md')
        return 2

    saida = [f'Registro de execução: {projeto.name}',
             f'data: {datetime.datetime.now():%Y-%m-%d %H:%M}',
             f'sistema: {platform.system()} {platform.machine()} | Python {platform.python_version()}',
             f'open() sem encoding lê em: {codificacao(args.como_windows)}']
    falhas = 0
    with tempfile.TemporaryDirectory() as tmp:
        copia = Path(tmp) / projeto.name
        copia.mkdir()
        levados, deixados = copia_limpa(projeto, copia)
        saida.append(f'cópia limpa: {len(levados)} arquivos')
        if deixados:
            saida.append(f'   ficaram fora pelo .gitignore: {", ".join(deixados)}')
        for n, linha in enumerate(comandos, 1):
            try:
                palavras = shlex.split(linha, posix=os.name != 'nt')
            except ValueError:
                palavras = linha.split()
            saida.append(f'passo {n}: {linha}')
            if not palavras or not eh_python(palavras[0]):
                saida.append('   não rodei: não é um comando de Python. Os passos seguintes rodaram sem ele.')
                falhas += 1
                continue
            if '-m' in palavras and palavras[palavras.index('-m') + 1:][:1] == ['venv']:
                saida.append('   seu, antes do registro: o registro roda com o Python desse ambiente')
                continue
            if palavras[1:4] == ['-m', 'pip', 'install']:
                if '-r' not in palavras:
                    saida.append('   não confiro: o pip install não aponta para um arquivo com -r')
                    falhas += 1
                    continue
                lista = projeto / palavras[palavras.index('-r') + 1]
                if not lista.is_file():
                    saida.append(f'   o README manda instalar {lista.name}, e o arquivo não existe no projeto')
                    falhas += 1
                    continue
                bate, linhas = conferir_lista(lista)
                saida += linhas
                saida.append('   ok: o ambiente é o da lista' if bate else '   o ambiente não bate com a lista')
                falhas += 0 if bate else 1
                continue
            codigo, linhas = rodar(palavras, copia, args.como_windows)
            saida.append(f'   código de saída: {codigo}')
            mostrar = linhas if len(linhas) <= 8 else ['   ...'] + linhas[-6:]
            saida += [l if l.startswith('   ...') else f'   | {l}' for l in mostrar]
            falhas += 1 if codigo else 0
        novos = gerados(copia, levados)
        if novos:
            saida.append('arquivos gerados na cópia:')
            saida += novos
    if falhas:
        saida.append(f'resultado: não reproduziu ({falhas} passo{"s" if falhas > 1 else ""} com problema)')
    else:
        saida.append('resultado: reproduziu')
    texto = '\n'.join(saida)
    print(texto)
    if args.salvar:
        Path(args.salvar).write_text('```text\n' + texto + '\n```\n', encoding='utf-8')
        print(f'registro gravado em {args.salvar}')
    return 1 if falhas else 0


if __name__ == '__main__':
    sys.exit(main())
