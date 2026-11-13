"""Roda o plano de testes da aula contra as regras certas ou contra uma versão com defeito.

Uso, de dentro da pasta da aula:
    python3 sondar.py                    roda o plano contra regras.py (todas devem passar)
    python3 sondar.py --defeito D3       troca uma regra pela versão com defeito e roda o plano
    python3 sondar.py --caio             roda só os três testes do Caio
    python3 sondar.py --matriz           quais tipos de teste pegam cada defeito, de D1 a D7
    python3 sondar.py --defeitos         lista os defeitos, de D1 a D7 e de E1 a E6

Cada teste do plano tem um tipo: exemplo (conhecido), invariante ou fronteira. Os invariantes rodam
nos dados de verdade do triatlo, em ../dados/triatlo. Sai com código 1 se algum teste falhar e com 2
se os dados não forem achados ou o defeito não existir.
Não usa biblioteca de testes: a próxima aula escreve esses testes no pytest.
"""
import argparse
import contextlib
import sys

import defeitos
import regras

TIPOS = ['exemplo', 'invariante', 'fronteira']
_dados = {}


def dados():
    if not _dados:
        atletas, inscricoes, resultados = regras.ler_dados()
        _dados.update(atletas={a['id_atleta']: a for a in atletas}, inscricoes=inscricoes,
                      resultados=resultados)
    return _dados


def resultados_unicos():
    vistos = {}
    for r in dados()['resultados']:
        vistos.setdefault((r['edicao'], r['id_inscricao']), r)
    return list(vistos.values())


def inscricoes_unicas():
    vistos = {}
    for i in dados()['inscricoes']:
        vistos.setdefault(i['id_inscricao'], i)
    return list(vistos.values())


PARCIAIS_2024_0002 = {'natacao': '1:14:19', 't1': '0:05:10', 'ciclismo': '6:02:35', 't2': '0:05:30',
                      'corrida': '4:45:44'}


def igual(chamada, esperado):
    """Teste de resultado: a chamada retorna exatamente o esperado."""
    def teste():
        obtido = chamada()
        return obtido == esperado, f'retornou {obtido!r}'
    return teste


def para_com(chamada, erro):
    """Teste de recusa: a chamada para com o erro esperado."""
    def teste():
        try:
            obtido = chamada()
        except erro:
            return True, ''
        return False, f'não parou; retornou {obtido!r}'
    return teste


# ---------------------------------------------------------------- invariantes nos dados do triatlo

def inv_vazio_continua_vazio():
    textos = [t for r in resultados_unicos() for t in r['parciais'].values()]
    vazios = sum(t is None for t in textos)
    saem = sum(regras.segundos(t) is None for t in textos)
    return saem == vazios, f'{len(textos)} parciais, {vazios} vazias na entrada, {saem} vazias na saída'


def inv_ida_e_volta():
    textos = [t for r in resultados_unicos() for t in list(r['parciais'].values()) + [r['tempo_oficial']]
              if t is not None]
    diferentes = [t for t in textos if regras.texto_do_tempo(regras.segundos(t)) != t]
    return not diferentes, (f'{len(textos)} tempos, {len(diferentes)} diferentes na volta'
                            + (f' (ex.: {diferentes[0]})' if diferentes else ''))


def inv_categoria_do_arquivo():
    atletas = dados()['atletas']
    insc = inscricoes_unicas()
    idades = [int(i['id_inscricao'][:4]) - int(atletas[i['id_atleta']]['ano_nascimento']) for i in insc]
    iguais = sum(regras.categoria(atletas[i['id_atleta']]['sexo'], atletas[i['id_atleta']]['ano_nascimento'],
                                  i['id_inscricao'][:4]) == i['categoria'] for i in insc)
    return iguais == len(insc), f'{iguais} de {len(insc)} iguais ao arquivo (idades de {min(idades)} a {max(idades)})'


def inv_categoria_valida():
    atletas = dados()['atletas']
    validas = {s + f for s in 'FM' for f in regras.FAIXAS}
    cats = [regras.categoria(atletas[i['id_atleta']]['sexo'], atletas[i['id_atleta']]['ano_nascimento'],
                             i['id_inscricao'][:4]) for i in inscricoes_unicas()]
    fora = sorted(set(cats) - validas)
    return not fora, f'{len(cats)} categorias calculadas, {len(fora)} fora das 20' + (f': {fora}' if fora else '')


def inv_soma_igual_oficial():
    completos = [r for r in resultados_unicos()
                 if r['status'] == 'concluiu' and all(v is not None for v in r['parciais'].values())]
    batem = sum(regras.soma_parciais(r['parciais']) == regras.segundos(r['tempo_oficial']) for r in completos)
    return batem == len(completos), f'{batem} de {len(completos)} concluintes com as cinco parciais'


def inv_soma_vazia_com_parcial_vazia():
    com_vazio = [r for r in resultados_unicos() if any(v is None for v in r['parciais'].values())]
    vazias = sum(regras.soma_parciais(r['parciais']) is None for r in com_vazio)
    return vazias == len(com_vazio), f'{vazias} de {len(com_vazio)} resultados com parcial vazia ficam sem soma'


# ---------------------------------------------------------------- o plano da aula

PLANO = [
    # (regra, tipo, descrição, teste, do Caio?)
    ('segundos', 'exemplo', "segundos('1:14:19') == 4459", igual(lambda: regras.segundos('1:14:19'), 4459), True),
    ('segundos', 'exemplo', "segundos('0:05:10') == 310", igual(lambda: regras.segundos('0:05:10'), 310), False),
    ('segundos', 'invariante', 'parcial vazia continua vazia, nos resultados da API', inv_vazio_continua_vazio, False),
    ('segundos', 'invariante', 'ida e volta: o texto do tempo em segundos é o texto de antes', inv_ida_e_volta, False),
    ('segundos', 'fronteira', 'segundos(None) é None, e não 0', igual(lambda: regras.segundos(None), None), False),
    ('segundos', 'fronteira', "segundos('0:00:00') == 0", igual(lambda: regras.segundos('0:00:00'), 0), False),
    ('segundos', 'fronteira', "segundos('10:00:00') == 36000 (hora com dois dígitos)",
     igual(lambda: regras.segundos('10:00:00'), 36000), False),
    ('segundos', 'fronteira', "segundos('1:60:00') para com ValueError",
     para_com(lambda: regras.segundos('1:60:00'), ValueError), False),
    ('categoria', 'exemplo', "categoria('M', 1978, 2024) == 'M45-49' (46 anos)",
     igual(lambda: regras.categoria('M', 1978, 2024), 'M45-49'), True),
    ('categoria', 'exemplo', "categoria('F', 1994, 2025) == 'F30-34' (31 anos)",
     igual(lambda: regras.categoria('F', 1994, 2025), 'F30-34'), False),
    ('categoria', 'invariante', 'categoria calculada igual à do arquivo de inscrições', inv_categoria_do_arquivo, False),
    ('categoria', 'invariante', 'toda categoria calculada é F ou M mais uma das 10 faixas', inv_categoria_valida, False),
    ('categoria', 'fronteira', "categoria('F', 2001, 2025) == 'F18-24' (24 anos)",
     igual(lambda: regras.categoria('F', 2001, 2025), 'F18-24'), False),
    ('categoria', 'fronteira', "categoria('F', 2000, 2025) == 'F25-29' (25 anos)",
     igual(lambda: regras.categoria('F', 2000, 2025), 'F25-29'), False),
    ('categoria', 'fronteira', "categoria('M', 1986, 2025) == 'M35-39' (39 anos)",
     igual(lambda: regras.categoria('M', 1986, 2025), 'M35-39'), False),
    ('categoria', 'fronteira', "categoria('M', 1985, 2025) == 'M40-44' (40 anos)",
     igual(lambda: regras.categoria('M', 1985, 2025), 'M40-44'), False),
    ('categoria', 'fronteira', "categoria('M', 1961, 2025) == 'M60-64' (64 anos)",
     igual(lambda: regras.categoria('M', 1961, 2025), 'M60-64'), False),
    ('categoria', 'fronteira', "categoria('M', 1960, 2025) == 'M65+' (65 anos)",
     igual(lambda: regras.categoria('M', 1960, 2025), 'M65+'), False),
    ('categoria', 'fronteira', "categoria('F', 2007, 2025) == 'F18-24' (18 anos)",
     igual(lambda: regras.categoria('F', 2007, 2025), 'F18-24'), False),
    ('categoria', 'fronteira', "categoria('F', 2008, 2025) para com ValueError (17 anos)",
     para_com(lambda: regras.categoria('F', 2008, 2025), ValueError), False),
    ('soma_parciais', 'exemplo', 'soma das parciais da inscrição 2024-0002 == 43998 (12:13:18)',
     igual(lambda: regras.soma_parciais(PARCIAIS_2024_0002), 43998), True),
    ('soma_parciais', 'invariante', 'soma das cinco parciais igual ao tempo oficial', inv_soma_igual_oficial, False),
    ('soma_parciais', 'invariante', 'resultado com parcial vazia fica sem soma', inv_soma_vazia_com_parcial_vazia, False),
    ('soma_parciais', 'fronteira', 'uma parcial vazia (T1) deixa a soma vazia',
     igual(lambda: regras.soma_parciais({**PARCIAIS_2024_0002, 't1': None}), None), False),
    ('soma_parciais', 'fronteira', 'as cinco parciais vazias (DNS) deixam a soma vazia',
     igual(lambda: regras.soma_parciais(dict.fromkeys(regras.ETAPAS)), None), False),
]


@contextlib.contextmanager
def com_defeito(codigo):
    if codigo is None:
        yield
        return
    nome, versao, _ = defeitos.DEFEITOS[codigo]
    certa = getattr(regras, nome)
    setattr(regras, nome, versao)
    try:
        yield
    finally:
        setattr(regras, nome, certa)


def rodar(codigo=None, so_caio=False):
    saida = []
    with com_defeito(codigo):
        for regra, tipo, descricao, teste, caio in PLANO:
            if so_caio and not caio:
                continue
            try:
                passou, detalhe = teste()
            except Exception as e:  # o defeito pode quebrar a regra no meio
                passou, detalhe = False, f'erro {type(e).__name__}: {e}'
            saida.append((regra, tipo, descricao, passou, detalhe))
    return saida


def mostrar(saida, titulo):
    print(titulo)
    for regra, tipo, descricao, passou, detalhe in saida:
        marca = 'ok    ' if passou else 'FALHOU'
        extra = f'  [{detalhe}]' if detalhe and (not passou or tipo == 'invariante') else ''
        print(f'{marca}  {tipo:<10}  {descricao}{extra}')
    falhas = sum(not s[3] for s in saida)
    print(f'{len(saida) - falhas} de {len(saida)} passaram')
    return falhas


def matriz():
    linhas = {t: [] for t in TIPOS}
    linhas['caio'] = []
    codigos = [c for c in defeitos.DEFEITOS if c.startswith('D')]
    for c in codigos:
        saida = rodar(c)
        for t in TIPOS:
            linhas[t].append(sum(1 for s in saida if s[1] == t and not s[3]))
        linhas['caio'].append(sum(1 for s in rodar(c, so_caio=True) if not s[3]))
    contagem = {t: sum(1 for p in PLANO if p[1] == t) for t in TIPOS}
    print('Quantos testes de cada tipo falham com cada defeito (0 = o defeito passa sem ninguém ver)')
    print(f'{"tipo de teste":<24}' + ''.join(f'{c:>5}' for c in codigos) + '   defeitos pegos')
    for t, rotulo in [('exemplo', f'exemplos ({contagem["exemplo"]})'),
                      ('invariante', f'invariantes ({contagem["invariante"]})'),
                      ('fronteira', f'fronteiras ({contagem["fronteira"]})'),
                      ('caio', 'só os 3 do Caio')]:
        pegos = sum(1 for n in linhas[t] if n)
        print(f'{rotulo:<24}' + ''.join(f'{n:>5}' for n in linhas[t]) + f'   {pegos} de {len(codigos)}')
    todos = [sum(linhas[t][k] for t in TIPOS) for k in range(len(codigos))]
    print(f'{"plano inteiro":<24}' + ''.join(f'{n:>5}' for n in todos)
          + f'   {sum(1 for n in todos if n)} de {len(codigos)}')


def main(argv=None):
    p = argparse.ArgumentParser(description='Roda o plano de testes da aula.')
    g = p.add_mutually_exclusive_group()
    g.add_argument('--defeito', help='troca uma regra pela versão com defeito (D1 a D7)')
    g.add_argument('--caio', action='store_true', help='roda só os três testes do Caio')
    g.add_argument('--matriz', action='store_true', help='quais tipos de teste pegam cada defeito')
    g.add_argument('--defeitos', action='store_true', help='lista os defeitos')
    a = p.parse_args(argv)
    if a.defeitos:
        for c, (nome, _, texto) in defeitos.DEFEITOS.items():
            print(f'{c}  {nome:<14} {texto}')
        return 0
    if a.defeito and a.defeito.upper() not in defeitos.DEFEITOS:
        print(f'defeito {a.defeito!r} não existe. Veja a lista com: python3 sondar.py --defeitos')
        return 2
    codigo = a.defeito.upper() if a.defeito else None
    if codigo and codigo.startswith('E'):
        print(f'{codigo} é um defeito do exercício: o plano da aula não cobre consolidar nem juntar. '
              'O plano dessas regras é o que você escreve.')
        return 2
    try:
        dados()  # para antes de rodar se os arquivos não estão em ../dados/triatlo
        if a.matriz:
            matriz()
            return 0
        if a.caio:
            return 1 if mostrar(rodar(so_caio=True), 'Os três testes do Caio, contra regras.py') else 0
        titulo = (f'Plano da aula com o defeito {codigo} ({defeitos.DEFEITOS[codigo][2]})' if codigo
                  else 'Plano da aula, contra regras.py')
        return 1 if mostrar(rodar(codigo), titulo) else 0
    except FileNotFoundError as e:
        print(e)
        return 2


if __name__ == '__main__':
    sys.exit(main())
