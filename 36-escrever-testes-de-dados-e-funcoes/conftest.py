"""Configuração do pytest da aula «Escrever testes de dados e funções».

Acrescenta a opção --defeito. Com ela, antes de carregar os testes, o pytest troca uma função de
transformacoes.py pela versão com defeito do defeitos.py:
    python3 -m pytest --defeito D3

Também prepara os dados do triatlo uma vez só, para os testes que rodam nos dados de verdade.
"""
import pytest

_ativo = []


def pytest_addoption(parser):
    parser.addoption('--defeito', default=None,
                     help='troca uma função pela versão com defeito: D1 a D5 (aula) ou E1 a E5 (exercício)')


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


@pytest.fixture(scope='session')
def dados():
    """Inscrições, resultados da API e edições do triatlo, lidos de ../dados/triatlo."""
    import transformacoes
    return transformacoes.ler_dados()


@pytest.fixture(scope='session')
def tabela(dados):
    """A tabela montada com os dados do triatlo: uma linha por inscrição."""
    import transformacoes
    inscricoes, resultados, _ = dados
    return transformacoes.montar_tabela(inscricoes, resultados)
