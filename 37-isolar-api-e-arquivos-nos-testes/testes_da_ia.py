"""Os primeiros testes da coleta, do jeito que a IA escreveu. A seção 1 da aula mostra o que dá errado.

Eles chamam a API de verdade, leem os arquivos do triatlo e gravam na pasta da aula.
O nome não começa com test_, então o pytest só roda se você disser o nome:
    python3 -m pytest -q testes_da_ia.py --com-rede --tb=no -rN
    python3 -m pytest -q testes_da_ia.py
"""
import os
import sys
from pathlib import Path

import coletar
from transformacoes import ler_dados

BASE_URL = coletar.ENDERECO_PADRAO  # o servidor local do kit
RAIZ_DO_KIT = Path(__file__).resolve().parent.parent


def test_coleta_de_2025():
    linhas, _ = coletar.coletar(BASE_URL, 'kit-local', {'edicao': '2025'})
    assert len(linhas) == 462


def test_main_grava_o_arquivo():
    os.environ['API_TRIATLO_TOKEN'] = 'kit-local'
    sys.argv = ['coletar.py', '--edicao', '2025']
    assert coletar.main() == 0
    assert os.path.exists('resultados-2025.json')


def test_inscricoes_das_duas_edicoes():
    inscricoes, _, _ = ler_dados(RAIZ_DO_KIT / 'dados' / 'triatlo')
    assert len(inscricoes) == 883
