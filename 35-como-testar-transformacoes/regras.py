"""As regras de transformação do projeto do triatlo. Aula «Como testar transformações».

São as regras que o relatório da prova usa. Cada função diz no comentário o que promete:
é isso que o plano de testes vai cobrar.

Para usar no Python, de dentro da pasta da aula:
    from regras import segundos, categoria, soma_parciais, consolidar, juntar, ler_dados

Os dados vêm de ../dados/triatlo. Só usa a biblioteca padrão.
"""
import csv
import json
from pathlib import Path

DADOS = Path('..') / 'dados' / 'triatlo'
ETAPAS = ['natacao', 't1', 'ciclismo', 't2', 'corrida']
FAIXAS = ['18-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65+']


class ResultadoDuplicado(ValueError):
    """A API mandou duas versões diferentes do mesmo resultado."""


class ResultadoSemInscricao(ValueError):
    """A API mandou o resultado de uma inscrição que não está nos arquivos de inscrição."""


# ---------------------------------------------------------------- regra 1: tempo em segundos

def segundos(texto):
    """'1:14:19' vira 4459 (1 h, 14 min e 19 s).

    Vazio (None) continua vazio: tempo que não existe não é zero.
    Texto fora do formato H:MM:SS, ou com minuto ou segundo acima de 59, para com ValueError.
    """
    if texto is None:
        return None
    partes = texto.split(':')
    if (len(partes) != 3 or not all(p.isdigit() for p in partes)
            or len(partes[1]) != 2 or len(partes[2]) != 2):
        raise ValueError(f'tempo fora do formato H:MM:SS: {texto!r}')
    h, m, s = (int(p) for p in partes)
    if m > 59 or s > 59:
        raise ValueError(f'minuto ou segundo acima de 59: {texto!r}')
    return h * 3600 + m * 60 + s


def texto_do_tempo(seg):
    """O caminho de volta: 4459 vira '1:14:19'. Vazio continua vazio."""
    if seg is None:
        return None
    return f'{seg // 3600}:{seg % 3600 // 60:02d}:{seg % 60:02d}'


# ---------------------------------------------------------------- regra 2: categoria

def faixa_idade(idade):
    """Faixa de 5 em 5 anos, com 18-24 na primeira e 65+ na última.

    A prova só aceita atletas com 18 anos ou mais no ano da prova: abaixo disso, ValueError.
    """
    if idade < 18:
        raise ValueError(f'idade abaixo de 18 anos: {idade}')
    if idade < 25:
        return '18-24'
    if idade >= 65:
        return '65+'
    base = idade // 5 * 5
    return f'{base}-{base + 4}'


def categoria(sexo, ano_nascimento, edicao):
    """Sexo mais faixa de idade no ano da prova: ('F', 1985, 2025) vira 'F40-44'.

    A idade é a do ano da prova (edição menos ano de nascimento), sem olhar o dia do aniversário.
    """
    if sexo not in ('F', 'M'):
        raise ValueError(f'sexo fora de F e M: {sexo!r}')
    return sexo + faixa_idade(int(edicao) - int(ano_nascimento))


# ---------------------------------------------------------------- regra 3: soma das parciais

def soma_parciais(parciais):
    """Soma, em segundos, das cinco parciais (natação, T1, ciclismo, T2, corrida).

    Se alguma parcial está vazia, a soma fica vazia (None): não dá para somar o que não foi medido.
    """
    valores = [segundos(parciais[etapa]) for etapa in ETAPAS]
    if any(v is None for v in valores):
        return None
    return sum(valores)


# ---------------------------------------------------------------- regras do exercício

def consolidar(resultados):
    """Um resultado por (edicao, id_inscricao), na ordem em que chegaram.

    Cópia idêntica de um resultado sai. Duas versões diferentes do mesmo resultado param com
    ResultadoDuplicado: o programa não escolhe uma delas sozinho.
    """
    vistos = {}
    for r in resultados:
        chave = (r['edicao'], r['id_inscricao'])
        if chave in vistos:
            if vistos[chave] != r:
                raise ResultadoDuplicado(f'duas versões diferentes do resultado {chave[1]} ({chave[0]})')
            continue
        vistos[chave] = r
    return list(vistos.values())


def juntar(inscricoes, resultados):
    """Uma linha por inscrição, com o status e o tempo oficial do resultado.

    Linha de inscrição repetida, idêntica, conta uma vez só. Inscrição sem resultado fica com o
    status 'sem resultado' (não é DNS: DNS é o status que a organização deu; aqui o arquivo não tem
    resultado nenhum). Resultado de uma inscrição
    que não existe para com ResultadoSemInscricao.
    """
    unicas = {}
    for i in inscricoes:
        chave = (int(i['id_inscricao'][:4]), i['id_inscricao'])
        if chave in unicas and unicas[chave] != i:
            raise ValueError(f'duas linhas diferentes para a inscrição {chave[1]}')
        unicas.setdefault(chave, i)
    por_chave = {(r['edicao'], r['id_inscricao']): r for r in consolidar(resultados)}
    sobra = sorted(set(por_chave) - set(unicas))
    if sobra:
        raise ResultadoSemInscricao(f'{len(sobra)} resultado(s) sem inscrição: ' +
                                    ', '.join(f'{i} ({e})' for e, i in sobra))
    linhas = []
    for (edicao, ident), i in unicas.items():
        r = por_chave.get((edicao, ident))
        linhas.append({'edicao': edicao, 'id_inscricao': ident, 'id_atleta': int(i['id_atleta']),
                       'categoria': i['categoria'],
                       'status': r['status'] if r else 'sem resultado',
                       'tempo_oficial': r['tempo_oficial'] if r else None})
    return linhas


# ---------------------------------------------------------------- leitura dos arquivos

def ler_dados(pasta=DADOS):
    """Atletas, inscrições das duas edições e resultados da API, como vêm nos arquivos."""
    pasta = Path(pasta)
    nomes = ['atletas.csv', 'inscricoes_2024.csv', 'inscricoes_2025.csv', 'api_resultados.json']
    for nome in nomes:
        if not (pasta / nome).is_file():
            raise FileNotFoundError(f'arquivo não encontrado: {pasta / nome}. '
                                    'Rode de dentro da pasta da aula, no kit do curso.')
    with open(pasta / 'atletas.csv', encoding='utf-8', newline='') as f:
        atletas = list(csv.DictReader(f))
    inscricoes = []
    for nome, sep in (('inscricoes_2024.csv', ','), ('inscricoes_2025.csv', ';')):
        with open(pasta / nome, encoding='utf-8', newline='') as f:
            inscricoes += list(csv.DictReader(f, delimiter=sep))
    resultados = json.loads((pasta / 'api_resultados.json').read_text(encoding='utf-8'))
    return atletas, inscricoes, resultados
