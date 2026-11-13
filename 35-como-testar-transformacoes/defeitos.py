"""Versões com defeito das regras de regras.py. Aula «Como testar transformações».

Cada defeito é um erro que alguém poderia fazer de verdade: a função roda, não dá erro e retorna
um resultado que parece certo. O sondar.py troca a regra certa por uma dessas versões e roda o plano
de testes da aula, para ver quais testes pegam o defeito.

D1 a D7 são das três regras da aula. E1 a E6 são das duas regras do exercício.
"""
import regras
from regras import ETAPAS

_segundos_certo = regras.segundos  # a versão certa, para os defeitos que só mudam um pedaço


# ---------------------------------------------------------------- defeitos das regras da aula

def d1_segundos(texto):
    if texto is None:
        return 0  # o vazio vira zero
    return _segundos_certo(texto)


def d2_segundos(texto):
    if texto is None:
        return None
    _segundos_certo(texto)  # o formato continua sendo checado
    h = int(texto[0])  # a hora é só o primeiro caractere
    m, s = (int(p) for p in texto.split(':')[1:])
    return h * 3600 + m * 60 + s


def d3_categoria(sexo, ano_nascimento, edicao):
    idade = int(edicao) - int(ano_nascimento) - 1  # "a pessoa pode não ter feito aniversário"
    return sexo + regras.faixa_idade(idade)


def d4_faixa_idade(idade):
    if idade < 18:
        raise ValueError(f'idade abaixo de 18 anos: {idade}')
    if idade < 25:
        return '18-24'
    if idade > 65:  # o 65 ficou de fora do 65+
        return '65+'
    base = idade // 5 * 5
    return f'{base}-{base + 4}'


def d5_soma_parciais(parciais):
    valores = [regras.segundos(parciais[etapa]) for etapa in ETAPAS]
    return sum(v for v in valores if v is not None)  # soma o que tem


def d6_soma_parciais(parciais):
    valores = [regras.segundos(parciais[etapa]) for etapa in ['natacao', 't1', 'ciclismo', 'corrida']]
    if any(v is None for v in valores):  # a T2 ficou fora da lista
        return None
    return sum(valores)


def d7_faixa_idade(idade):
    if idade <= 18:  # quem tem 18 anos fica de fora
        raise ValueError(f'idade abaixo de 18 anos: {idade}')
    if idade < 25:
        return '18-24'
    if idade >= 65:
        return '65+'
    base = idade // 5 * 5
    return f'{base}-{base + 4}'


# ---------------------------------------------------------------- defeitos das regras do exercício

def e1_consolidar(resultados):
    vistos = {}
    for r in resultados:
        vistos[(r['edicao'], r['id_inscricao'])] = r  # versão diferente: fica a última, sem aviso
    return list(vistos.values())


def e2_consolidar(resultados):
    vistos = {}
    for r in resultados:
        vistos.setdefault(r['numero_peito'], r)  # a chave é o número de peito
    return list(vistos.values())


def _juntar(inscricoes, resultados, tirar_repetidas=True, so_com_resultado=False,
            vazio='sem resultado', checar_sobra=True):
    unicas = {}
    for n, i in enumerate(inscricoes):
        chave = (int(i['id_inscricao'][:4]), i['id_inscricao'])
        if tirar_repetidas:
            unicas.setdefault(chave, i)
        else:
            unicas[(chave, n)] = i
    por_chave = {(r['edicao'], r['id_inscricao']): r for r in regras.consolidar(resultados)}
    chaves = {k if tirar_repetidas else k[0] for k in unicas}
    sobra = sorted(set(por_chave) - chaves)
    if checar_sobra and sobra:
        raise regras.ResultadoSemInscricao(f'{len(sobra)} resultado(s) sem inscrição')
    linhas = []
    for k, i in unicas.items():
        edicao, ident = k if tirar_repetidas else k[0]
        r = por_chave.get((edicao, ident))
        if r is None and so_com_resultado:
            continue
        linhas.append({'edicao': edicao, 'id_inscricao': ident, 'id_atleta': int(i['id_atleta']),
                       'categoria': i['categoria'], 'status': r['status'] if r else vazio,
                       'tempo_oficial': r['tempo_oficial'] if r else None})
    return linhas


def e3_juntar(inscricoes, resultados):
    return _juntar(inscricoes, resultados, so_com_resultado=True)  # só inscrição com resultado


def e4_juntar(inscricoes, resultados):
    return _juntar(inscricoes, resultados, tirar_repetidas=False)  # linha repetida conta duas vezes


def e5_juntar(inscricoes, resultados):
    return _juntar(inscricoes, resultados, vazio='DNS')  # sem resultado vira DNS


def e6_juntar(inscricoes, resultados):
    return _juntar(inscricoes, resultados, checar_sobra=False)  # resultado sem inscrição some calado


# código: (regra trocada, versão com defeito, o que está errado)
DEFEITOS = {
    'D1': ('segundos', d1_segundos, 'o vazio vira zero'),
    'D2': ('segundos', d2_segundos, 'a hora é lida só pelo primeiro caractere do texto'),
    'D3': ('categoria', d3_categoria, 'a idade desconta um ano, "porque a pessoa pode não ter feito aniversário"'),
    'D4': ('faixa_idade', d4_faixa_idade, 'quem tem 65 anos não entra no 65+'),
    'D5': ('soma_parciais', d5_soma_parciais, 'soma as parciais que tem e ignora as vazias'),
    'D6': ('soma_parciais', d6_soma_parciais, 'a T2 ficou fora da soma'),
    'D7': ('faixa_idade', d7_faixa_idade, 'quem tem 18 anos é recusado'),
    'E1': ('consolidar', e1_consolidar, 'com duas versões diferentes do mesmo resultado, fica a última, sem aviso'),
    'E2': ('consolidar', e2_consolidar, 'a chave das cópias é o número de peito, e não a edição com a inscrição'),
    'E3': ('juntar', e3_juntar, 'só entram as inscrições que têm resultado'),
    'E4': ('juntar', e4_juntar, 'a linha de inscrição repetida conta duas vezes'),
    'E5': ('juntar', e5_juntar, 'a inscrição sem resultado ganha o status DNS'),
    'E6': ('juntar', e6_juntar, 'o resultado sem inscrição some sem aviso'),
}
