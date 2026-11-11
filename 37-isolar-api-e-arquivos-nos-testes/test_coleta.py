"""Os testes da coleta da aula 12, sem a API e sem os arquivos do triatlo.

Para rodar, de dentro da pasta da aula:
    python3 -m pytest -q test_coleta.py
"""
import json
import sys
import urllib.error
from io import BytesIO
from pathlib import Path
from unittest import mock

import pytest

import coletar
from coletar import ApiForaDoAr, ColetaIncompleta, chamar
RESPOSTAS = Path(__file__).resolve().parent / 'respostas'
PAGINA = '/v1/resultados?status=DSQ&pagina={}&por_pagina=3'


def sem_tela(texto):
    """Engole o que o coletar mostraria na tela."""


# ---------------------------------------------------------------- a coleta com a API falsa

def test_coleta_junta_as_tres_paginas(api_falsa):
    linhas, resumo = coletar.coletar('http://api', 'kit-local', {'status': 'DSQ'}, por_pagina=3, mostrar=sem_tela)
    assert api_falsa.chamadas == [PAGINA.format(1), PAGINA.format(2), PAGINA.format(3)]
    assert (resumo['total_api'], len(linhas)) == (7, 7)  # 3 + 3 + 1
    assert linhas[6]['id_inscricao'] == '2025-0273'
    assert linhas[6]['origem'] == {'pagina': 3, 'posicao': 1}


def test_pagina_curta_para(api_falsa):
    _, corpo = api_falsa.respostas[PAGINA.format(2)]
    corpo['itens'].pop()  # a página 2 chega com 2 itens, e não 3
    with pytest.raises(ColetaIncompleta, match='a página 2 trouxe 2 itens'):
        coletar.coletar('http://api', 'kit-local', {'status': 'DSQ'}, por_pagina=3, mostrar=sem_tela)


def test_total_que_muda_no_meio_para(api_falsa):
    _, corpo = api_falsa.respostas[PAGINA.format(3)]
    corpo['total'] = 8  # um desclassificado entrou depois da página 1
    with pytest.raises(ColetaIncompleta, match='o total mudou'):
        coletar.coletar('http://api', 'kit-local', {'status': 'DSQ'}, por_pagina=3, mostrar=sem_tela)


def test_sem_token_para_na_primeira_pagina(api_falsa):
    api_falsa.gravada('sem-token')  # a resposta 401 de verdade, gravada da API
    with pytest.raises(ColetaIncompleta, match='respondeu 401'):
        coletar.coletar('http://api', '', {'status': 'DSQ'}, por_pagina=3, mostrar=sem_tela)
    assert api_falsa.chamadas == [PAGINA.format(1)]


# ---------------------------------------------------------------- o main grava na pasta do teste

def pagina_unica_2025():
    """Uma página com os 3 primeiros desclassificados de 2025, montada com os itens gravados."""
    itens = []
    for pagina in (1, 2, 3):
        gravada = json.loads((RESPOSTAS / f'dsq-pagina-{pagina}.json').read_text(encoding='utf-8'))
        itens += [i for i in gravada['corpo']['itens'] if i['edicao'] == 2025]
    return {'pagina': 1, 'por_pagina': 3, 'total': 3, 'total_paginas': 1, 'itens': itens[:3]}


@pytest.fixture
def rodar_main(api_falsa, tmp_path, monkeypatch):
    """Prepara o main para rodar dentro da pasta temporária do teste, com o token e a página única."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('API_TRIATLO_TOKEN', 'kit-local')
    monkeypatch.setattr(sys, 'argv', ['coletar.py', '--edicao', '2025', '--por-pagina', '3'])
    corpo = pagina_unica_2025()
    api_falsa.respostas = {'/v1/resultados?edicao=2025&pagina=1&por_pagina=3': (200, corpo)}
    return corpo


def test_main_grava_quando_bate(rodar_main, tmp_path, capsys):
    assert coletar.main() == 0
    assert [p.name for p in tmp_path.iterdir()] == ['resultados-2025.json']  # e nenhum .tmp sobrando
    gravado = json.loads((tmp_path / 'resultados-2025.json').read_text(encoding='utf-8'))
    assert [l['id_inscricao'] for l in gravado['linhas']] == ['2025-0043', '2025-0104', '2025-0132']
    assert 'gravei resultados-2025.json: 3 linhas' in capsys.readouterr().out


def test_main_nao_grava_quando_falta_linha(rodar_main, tmp_path, capsys):
    rodar_main['itens'].pop()  # chegaram 2 das 3 linhas
    assert coletar.main() == 1
    assert list(tmp_path.iterdir()) == []
    assert 'Nada foi gravado' in capsys.readouterr().err


# ---------------------------------------------------------------- o chamar, com o urlopen trocado

def test_chamar_le_a_resposta():
    resposta = mock.MagicMock()
    resposta.read.return_value = b'{"total": 7}'
    resposta.getcode.return_value = 200
    with mock.patch('urllib.request.urlopen', return_value=resposta) as urlopen:
        codigo, corpo, caminho = chamar('http://api', 'kit-local', '/v1/resultados', {'status': 'DSQ'}, 10)
    assert (codigo, corpo, caminho) == (200, {'total': 7}, '/v1/resultados?status=DSQ')
    urlopen.assert_called_once()
    pedido = urlopen.call_args.args[0]
    assert pedido.full_url == 'http://api/v1/resultados?status=DSQ'


def test_chamar_le_o_corpo_do_erro():
    erro = urllib.error.HTTPError('http://api/v1/resultados', 401, 'Unauthorized', {},
                                  BytesIO(b'{"erro": "token_ausente_ou_invalido"}'))
    with mock.patch('urllib.request.urlopen', side_effect=erro):
        codigo, corpo, _ = chamar('http://api', '', '/v1/resultados', {}, 10)
    assert (codigo, corpo) == (401, {'erro': 'token_ausente_ou_invalido'})


def test_chamar_sem_resposta_vira_api_fora_do_ar():
    recusada = urllib.error.URLError(ConnectionRefusedError(61, 'Connection refused'))
    with mock.patch('urllib.request.urlopen', side_effect=recusada):
        with pytest.raises(ApiForaDoAr, match='a API não respondeu em http://api'):
            chamar('http://api', 'kit-local', '/v1/resultados', {}, 10)
