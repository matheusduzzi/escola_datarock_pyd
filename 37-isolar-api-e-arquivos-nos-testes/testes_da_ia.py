"""Os primeiros testes da coleta, do jeito que a IA escreveu. A seção 1 da aula mostra o que dá errado.

Eles chamam a API de verdade, leem os arquivos do triatlo e gravam na pasta da aula.
O nome não começa com test_, então o pytest só roda se você disser o nome:
    python3 -m pytest -q testes_da_ia.py --com-rede
    python3 -m pytest -q testes_da_ia.py
"""
import os
import sys

import coletar
from transformacoes import ler_dados


def test_coleta_de_2025():
    linhas, _ = coletar.coletar('http://127.0.0.1:8765', 'kit-local', {'edicao': '2025'})
    assert len(linhas) == 462


def test_main_grava_o_arquivo():
    os.environ['API_TRIATLO_TOKEN'] = 'kit-local'
    sys.argv = ['coletar.py', '--edicao', '2025']
    assert coletar.main() == 0
    assert os.path.exists('resultados-2025.json')


def test_inscricoes_das_duas_edicoes():
    inscricoes, _, _ = ler_dados()
    assert len(inscricoes) == 883
