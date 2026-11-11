"""Roda os testes contra cada defeito e diz quais testes pegaram. Aula «Escrever testes de dados e funções».

De dentro da pasta da aula:
    python3 rodar_defeitos.py              os testes da aula (test_tabela.py) contra D1 a D5
    python3 rodar_defeitos.py --exercicio  os seus testes (test_exercicio.py) contra E1 a E5

Primeiro roda os testes com as funções certas: todos têm que passar. Depois troca uma função por vez
pela versão com defeito. Sai com 0 se todo defeito fez algum teste falhar, com 1 se algum passou
sem ninguém ver, e com 2 se o pytest não está instalado ou se algum teste falha com as funções certas.
"""
import importlib.util
import re
import subprocess
import sys

import defeitos


def rodar(arquivo, codigo=None):
    comando = [sys.executable, '-m', 'pytest', arquivo, '-q', '-rf', '--tb=no', '-p', 'no:cacheprovider']
    if codigo:
        comando += ['--defeito', codigo]
    saida = subprocess.run(comando, capture_output=True, text=True).stdout
    falharam = re.findall(r'^FAILED \S+::(\w+)', saida, flags=re.M)
    contas = {tipo: int(n) for n, tipo in re.findall(r'(\d+) (passed|failed|skipped|error)', saida)}
    return falharam, contas


def main():
    if importlib.util.find_spec('pytest') is None:
        print('O pytest não está instalado nesse Python. Rode: python3 -m pip install pytest')
        return 2
    exercicio = '--exercicio' in sys.argv[1:]
    arquivo = 'test_exercicio.py' if exercicio else 'test_tabela.py'
    letra = 'E' if exercicio else 'D'

    falharam, contas = rodar(arquivo)
    escritos = contas.get('passed', 0) + contas.get('failed', 0)
    if falharam or contas.get('error'):
        print(f'Com as funções certas, {len(falharam)} teste(s) de {arquivo} falham: ' + ', '.join(falharam))
        print('Conserte esses testes antes de procurar defeitos. Rode: python3 -m pytest ' + arquivo)
        return 2
    print(f'{arquivo}: {escritos} testes passam com as funções certas'
          + (f', {contas["skipped"]} ainda por escrever' if contas.get('skipped') else ''))

    pegos = 0
    codigos = [c for c in defeitos.DEFEITOS if c.startswith(letra)]
    for codigo in codigos:
        nome, _, descricao = defeitos.DEFEITOS[codigo]
        falharam, _ = rodar(arquivo, codigo)
        pegos += bool(falharam)
        print(f'{codigo}  {nome}: {descricao}')
        if falharam:
            for teste in falharam:
                print(f'      falha  {teste}')
        else:
            print('      nenhum teste falha: o defeito passa sem ninguém ver')
    print(f'Defeitos pegos: {pegos} de {len(codigos)}')
    return 0 if pegos == len(codigos) else 1


if __name__ == '__main__':
    sys.exit(main())
