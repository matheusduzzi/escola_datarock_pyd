"""Mostra o que um arquivo de requisitos traz para o seu Python.

Uso, de dentro da pasta da aula:
    python3 arvore.py requisitos-do-caio.txt
    python3 arvore.py requisitos-do-caio.txt --travar
    python3 arvore.py requisitos-do-caio.txt --ambiente
    python3 arvore.py requisitos-do-caio.txt --imports ..

Sem opção, lista cada pacote da árvore: o que você declarou e o que veio junto,
com a versão instalada, o Python que o pacote pede e a licença que ele declara.
--travar imprime a árvore inteira no formato nome==versão.
--ambiente compara a árvore com tudo o que está instalado nesse Python.
--imports lê os .py das pastas indicadas e diz, para cada import de fora da
biblioteca padrão, se o pacote está declarado, se só vem junto com outro ou se falta.
Ele não entra em venv (pasta com pyvenv.cfg), em site-packages nem em pasta oculta, como a .venv.

Só usa a biblioteca padrão. Lê o que está instalado; não instala nada.
Códigos de saída: 0 tudo certo; 1 pacote faltando, versão diferente da pedida com == ou import sem declarar;
2 arquivo não encontrado ou uso errado.
"""
import argparse
import importlib.metadata as md
import importlib.util
import platform
import re
import sys
import sysconfig
from pathlib import Path


def normal(nome):
    return re.sub(r'[-_.]+', '-', nome).lower()


def ler_requisitos(arquivo, vistos=None):
    """Lê nomes e versões pedidas. Aceita comentários e a linha -r outro-arquivo.txt."""
    vistos = vistos if vistos is not None else set()
    arquivo = Path(arquivo)
    if not arquivo.is_file():
        print(f'arquivo não encontrado: {arquivo}')
        sys.exit(2)
    vistos.add(arquivo.resolve())
    pedidos = []
    for linha in arquivo.read_text(encoding='utf-8').splitlines():
        linha = linha.split('#', 1)[0].strip()
        if not linha:
            continue
        if linha.startswith(('-r ', '--requirement ')):
            outro = arquivo.parent / linha.split(None, 1)[1]
            if outro.resolve() not in vistos:
                pedidos += ler_requisitos(outro, vistos)
            continue
        m = re.match(r'([A-Za-z0-9][A-Za-z0-9._-]*)\s*(\[[^\]]*\])?\s*([^;]*)', linha)
        if m:
            pedidos.append((normal(m.group(1)), m.group(3).strip()))
    return pedidos


AMBIENTE = {
    'python_version': '.'.join(platform.python_version_tuple()[:2]),
    'python_full_version': platform.python_version(),
    'sys_platform': sys.platform,
    'platform_system': platform.system(),
    'platform_machine': platform.machine(),
    'os_name': __import__('os').name,
    'implementation_name': sys.implementation.name,
    'platform_python_implementation': platform.python_implementation(),
}
VERSOES = {'python_version', 'python_full_version'}


def comparar(var, op, valor):
    atual = AMBIENTE.get(var, '')
    if var in VERSOES:
        def tupla(v):
            return tuple(int(x) for x in re.findall(r'\d+', v)[:3])
        a, b = tupla(atual), tupla(valor)
        n = max(len(a), len(b))
        a, b = a + (0,) * (n - len(a)), b + (0,) * (n - len(b))
    else:
        a, b = atual, valor
    return {'==': a == b, '!=': a != b, '<': a < b, '<=': a <= b, '>': a > b, '>=': a >= b,
            'in': str(a) in str(b), 'not in': str(a) not in str(b)}.get(op, False)


def marcador_vale(marcador):
    """Avalia o marcador de ambiente de uma dependência (python_version < "3.11" e parecidos)."""
    if not marcador:
        return True
    if 'extra' in marcador:
        return False
    padrao = r'(\w+)\s*(==|!=|<=|>=|<|>|not in|in)\s*["\']([^"\']*)["\']'
    expr = re.sub(padrao, lambda m: ' V ' if comparar(*m.groups()) else ' F ', marcador)
    expr = expr.replace('(', ' ( ').replace(')', ' ) ')
    if set(expr.split()) - {'V', 'F', 'and', 'or', '(', ')'}:
        return True  # marcador que o arvore.py não conhece: mostra o pacote
    # sem eval: resolve cada parêntese de dentro para fora
    expr = ' '.join(expr.split())
    while '(' in expr:
        expr = re.sub(r'\(([^()]*)\)', lambda m: ' ' + avaliar(m.group(1)) + ' ', expr)
    return avaliar(expr) == 'V'


def avaliar(expr):
    """Avalia uma sequência de V e F ligada por and/or (and antes de or)."""
    partes = [p for p in expr.split(' or ')]
    return 'V' if any(all(t == 'V' for t in p.split() if t != 'and') for p in partes) else 'F'


def instalados():
    """Um pacote por nome, o primeiro que o Python acha (o mesmo que o import usaria)."""
    dists = {}
    for d in md.distributions():
        nome = d.metadata.get('Name')
        if nome and normal(nome) not in dists:
            dists[normal(nome)] = d
    return dists


def licenca(d):
    meta = d.metadata
    expr = meta.get('License-Expression')
    if expr:
        return expr
    texto = (meta.get('License') or '').strip()
    if texto and '\n' not in texto and len(texto) <= 40 and texto.upper() != 'UNKNOWN':
        return texto
    classes = [c.split(' :: ')[-1] for c in meta.get_all('Classifier') or [] if c.startswith('License ::')]
    return ', '.join(classes) if classes else '(não declarada)'


def dependencias(d):
    for req in d.requires or []:
        texto, _, marcador = req.partition(';')
        m = re.match(r'\s*([A-Za-z0-9][A-Za-z0-9._-]*)', texto)
        if m and marcador_vale(marcador.strip()):
            yield normal(m.group(1))


def arvore(pedidos, dists):
    """Percorre a árvore. Retorna {nome: quem trouxe primeiro} e a lista de faltantes."""
    veio_por, faltando = {}, []
    fila = [(nome, None) for nome, _ in pedidos]
    while fila:
        nome, pai = fila.pop(0)
        if nome in veio_por:
            continue
        if nome not in dists:
            if (nome, pai) not in faltando:
                faltando.append((nome, pai))
            continue
        veio_por[nome] = pai
        fila += [(filho, nome) for filho in dependencias(dists[nome])]
    return veio_por, faltando


def mostrar(pedidos, dists, veio_por, faltando):
    declarados = [n for n, _ in pedidos]
    print(f'Python {platform.python_version()} ({sys.platform}) | declarados: {len(declarados)}')
    linhas = [('pacote', 'versão', 'pede Python', 'licença', 'veio por')]
    for nome in sorted(veio_por, key=lambda n: (n not in declarados, n)):
        d = dists[nome]
        pede = (d.metadata.get('Requires-Python') or '-').replace(' ', '')
        linhas.append((nome, d.version, pede, licenca(d), 'declarado' if nome in declarados else veio_por[nome]))
    linhas += [(nome, 'FALTANDO', '', '', pai or 'declarado') for nome, pai in faltando]
    larguras = [max(len(l[i]) for l in linhas) + 2 for i in range(4)]
    for l in linhas:
        print(''.join(c.ljust(w) for c, w in zip(l, larguras)) + l[4])
    vieram = len(veio_por) - len([n for n in declarados if n in veio_por])
    print(f'na árvore: {len(veio_por)} pacotes ({len(declarados)} declarados, {vieram} vieram junto)')
    diferentes = [(nome, pedido) for nome, pedido in pedidos if pedido.startswith('==')
                  and nome in dists and dists[nome].version != pedido[2:].strip()]
    for nome, pedido in diferentes:
        print(f'versão diferente da pedida: {nome} instalado {dists[nome].version}, pedido {pedido}')
    if faltando:
        print(f'faltando: {len(faltando)} ({", ".join(n for n, _ in faltando)})')
    return bool(diferentes)


def mapa_modulos(dists):
    """Nome do import -> nome do pacote instalado (dotenv -> python-dotenv)."""
    mapa = {}
    for nome, d in dists.items():
        topo = d.read_text('top_level.txt')
        mods = topo.split() if topo else []
        if not mods:
            for f in d.files or []:
                partes = Path(str(f)).parts
                if partes and not partes[0].endswith(('.dist-info', '.egg-info', '.data')) and partes[0] != '..':
                    mods.append(partes[0][:-3] if partes[0].endswith('.py') else partes[0])
        for mod in mods:
            mapa.setdefault(mod, nome)
    return mapa


def da_biblioteca_padrao(mod):
    if mod in sys.builtin_module_names:
        return True
    try:
        spec = importlib.util.find_spec(mod)
    except (ImportError, ValueError):
        return False
    if spec is None:
        return False
    origem = spec.origin or (list(spec.submodule_search_locations or [''])[0])
    if origem in ('built-in', 'frozen'):
        return True
    padrao = [sysconfig.get_paths()['stdlib'], sysconfig.get_paths()['platstdlib']]
    return any(origem.startswith(p) for p in padrao) and 'site-packages' not in origem


def pasta_de_ambiente(pasta):
    """Pasta que não é código do projeto: oculta (.venv, .git), cache, site-packages ou um venv (tem pyvenv.cfg)."""
    return (pasta.name.startswith('.') or pasta.name in ('__pycache__', 'site-packages')
            or (pasta / 'pyvenv.cfg').is_file())


def arquivos_do_projeto(raiz):
    """Os .py abaixo de raiz, sem entrar em pasta de ambiente. Um venv dentro do kit fica de fora."""
    for item in sorted(raiz.iterdir()):
        if item.is_dir():
            if not pasta_de_ambiente(item):
                yield from arquivos_do_projeto(item)
        elif item.suffix == '.py':
            yield item


def ler_imports(pastas):
    usos, locais = {}, set()
    arquivos = []
    for pasta in pastas:
        p = Path(pasta)
        if not p.exists():
            print(f'pasta não encontrada: {p}')
            sys.exit(2)
        arquivos += [p] if p.is_file() else sorted(arquivos_do_projeto(p))
    for f in arquivos:
        locais.add(f.stem)
        locais.update(parte for parte in f.parent.parts)
        texto = f.read_text(encoding='utf-8', errors='ignore')
        for m in re.finditer(r'^\s*(?:from\s+([A-Za-z_]\w*)[\w.]*\s+import\b|import\s+([A-Za-z_]\w*))', texto, re.M):
            mod = m.group(1) or m.group(2)
            usos.setdefault(mod, set()).add(f)
    return usos, locais


def checar_imports(pedidos, dists, veio_por, pastas):
    usos, locais = ler_imports(pastas)
    mapa = mapa_modulos(dists)
    declarados = {n for n, _ in pedidos}
    base = Path(pastas[0]).resolve() if len(pastas) == 1 and Path(pastas[0]).is_dir() else Path.cwd()
    sem_declarar = 0
    print(f'{"import":<14}{"pacote":<18}{"situação":<34}onde')
    for mod in sorted(usos):
        if da_biblioteca_padrao(mod):
            continue
        pacote = mapa.get(mod)
        if pacote is None and mod in locais:
            continue
        lugares = sorted({str(f.resolve().relative_to(base)) if base in f.resolve().parents else str(f)
                          for f in usos[mod]})
        onde = lugares[0] + (f' e mais {len(lugares) - 1}' if len(lugares) > 1 else '')
        if pacote is None:
            situacao = 'não instalado'
            sem_declarar += 1
        elif pacote in declarados:
            situacao = 'declarado'
        elif pacote in veio_por:
            situacao = f'sem declarar, vem com {veio_por[pacote]}'
            sem_declarar += 1
        else:
            situacao = 'sem declarar, instalado à parte'
            sem_declarar += 1
        print(f'{mod:<14}{pacote or "?":<18}{situacao:<34}{onde}')
    print(f'imports de fora da biblioteca padrão sem declarar: {sem_declarar}')
    return sem_declarar


def main():
    p = argparse.ArgumentParser(description='Mostra a árvore de dependências de um arquivo de requisitos.')
    p.add_argument('requisitos', help='arquivo de requisitos, como requisitos-do-caio.txt')
    modo = p.add_mutually_exclusive_group()
    modo.add_argument('--travar', action='store_true', help='imprime a árvore no formato nome==versão')
    modo.add_argument('--ambiente', action='store_true', help='compara a árvore com tudo o que está instalado')
    modo.add_argument('--imports', nargs='+', metavar='PASTA', help='pastas com os .py do projeto')
    a = p.parse_args()

    pedidos = ler_requisitos(a.requisitos)
    if not pedidos:
        print(f'nenhum pacote em {a.requisitos}')
        sys.exit(2)
    dists = instalados()
    veio_por, faltando = arvore(pedidos, dists)

    if a.travar:
        print(f'# árvore de {Path(a.requisitos).name} no Python {platform.python_version()} ({sys.platform})')
        for nome in sorted(veio_por):
            print(f'{nome}=={dists[nome].version}')
        if faltando:
            print(f'# faltando: {", ".join(n for n, _ in faltando)}')
        sys.exit(1 if faltando else 0)
    if a.ambiente:
        fora = sorted(n for n in dists if n not in veio_por)
        print(f'pacotes instalados nesse Python: {len(dists)}')
        print(f'na árvore de {Path(a.requisitos).name}: {len(veio_por)}')
        print(f'fora da árvore: {len(fora)}' + (f' (por exemplo: {", ".join(fora[:6])})' if fora else ''))
        sys.exit(1 if faltando else 0)
    if a.imports:
        sys.exit(1 if checar_imports(pedidos, dists, veio_por, a.imports) or faltando else 0)
    diferente = mostrar(pedidos, dists, veio_por, faltando)
    sys.exit(1 if faltando or diferente else 0)


if __name__ == '__main__':
    main()
