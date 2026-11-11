"""Configuração do pytest da aula «Isolar API e arquivos nos testes».

Três coisas valem para todos os testes desta pasta:

1. A guarda de rede (fixture sem_rede, automática). Se um teste tentar abrir qualquer conexão,
   até com a API do seu computador, ele para na hora com RedeNoTeste e diz o endereço.
   A guarda vale para as conexões que o Python abre; ela não vê um programa externo rodado pelo teste.
   Para ver o que acontecia antes da guarda: python3 -m pytest --com-rede
2. A fixture api_falsa. Troca a função chamar do coletar.py por uma que responde com os arquivos
   gravados em respostas/ e anota cada chamada.
3. A opção --defeito, que troca uma função pela versão com defeito do defeitos.py:
   python3 -m pytest --defeito D1
"""
import copy
import json
import socket
import urllib.parse
from pathlib import Path

import pytest

RESPOSTAS = Path(__file__).resolve().parent / 'respostas'
_ativo = []


class RedeNoTeste(RuntimeError):
    """Um teste tentou abrir uma conexão de rede."""


def pytest_addoption(parser):
    parser.addoption('--com-rede', action='store_true', help='desliga a guarda de rede')
    parser.addoption('--defeito', default=None,
                     help='troca uma função pela versão com defeito: D1 a D3 (aula) ou E1 a E5 (exercício)')


def pytest_configure(config):
    codigo = config.getoption('--defeito')
    if codigo is None:
        return
    import defeitos
    if codigo not in defeitos.DEFEITOS:
        raise pytest.UsageError(f'defeito {codigo!r} não existe. Os que existem: ' + ', '.join(defeitos.DEFEITOS))
    _ativo.append(defeitos.ativar(codigo))


def pytest_terminal_summary(terminalreporter):
    if _ativo:
        terminalreporter.write_line(f'defeito ativo: {_ativo[0]}')


@pytest.fixture(autouse=True)
def sem_rede(request, monkeypatch):
    """Faz qualquer conexão de rede, e até a busca do endereço pelo nome, parar o teste com RedeNoTeste."""
    if request.config.getoption('--com-rede'):
        return

    def sem_nome(host, port, *args, **kwargs):
        raise RedeNoTeste(f'conexão bloqueada no teste: {host}:{port}')

    def sem_conexao(self, endereco, *args, **kwargs):
        onde = ':'.join(map(str, endereco)) if isinstance(endereco, tuple) else endereco
        raise RedeNoTeste(f'conexão bloqueada no teste: {onde}')

    monkeypatch.setattr(socket, 'getaddrinfo', sem_nome)
    monkeypatch.setattr(socket.socket, 'connect', sem_conexao)
    monkeypatch.setattr(socket.socket, 'connect_ex', sem_conexao)


class ApiFalsa:
    """Responde no lugar da API, com as respostas gravadas em respostas/. Anota cada chamada."""

    def __init__(self):
        self.respostas = {}  # chamada -> (código, corpo)
        self.chamadas = []

    def gravada(self, nome):
        """Passa a responder com respostas/<nome>.json, na chamada que está escrita no arquivo."""
        r = json.loads((RESPOSTAS / f'{nome}.json').read_text(encoding='utf-8'))
        self.respostas[r['chamada']] = (r['codigo'], r['corpo'])
        return r['corpo']

    def chamar(self, endereco, token, rota, parametros, espera):
        """Mesmos argumentos e mesmo retorno do chamar do coletar.py, sem rede."""
        caminho = rota + '?' + urllib.parse.urlencode(parametros)
        self.chamadas.append(caminho)
        if caminho not in self.respostas:
            raise AssertionError(f'não tem resposta preparada para {caminho}')
        codigo, corpo = self.respostas[caminho]
        return codigo, copy.deepcopy(corpo), caminho


@pytest.fixture
def api_falsa(monkeypatch):
    """A API falsa já com as 3 páginas dos desclassificados, no lugar do coletar.chamar."""
    import coletar
    falsa = ApiFalsa()
    for pagina in (1, 2, 3):
        falsa.gravada(f'dsq-pagina-{pagina}')
    monkeypatch.setattr(coletar, 'chamar', falsa.chamar)
    return falsa
