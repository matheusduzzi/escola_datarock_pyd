"""Os seus testes do exercício: o ler_dados com arquivos pequenos e o chamar sem rede.

Cada função abaixo tem o nome e, no comentário, o que o teste tem que mostrar. Troque o pytest.skip
pelo teste. Nenhum teste pode chamar a API, ler ../dados/triatlo nem gravar nesta pasta: use tmp_path
para os arquivos, mock.patch para o urlopen e a fixture api_falsa para o main.

Para rodar:
    python3 -m pytest -q test_exercicio.py
    python3 rodar_defeitos.py --exercicio
    python3 rodar_sozinho.py test_exercicio.py
"""
import sys
from unittest import mock

import pytest

import coletar
from coletar import chamar
from transformacoes import ler_dados


# ---------------------------------------------------------------- arquivos pequenos, em tmp_path

def test_le_os_arquivos_da_pasta_pedida(tmp_path):
    """Escreva em tmp_path os quatro arquivos que o ler_dados procura, com poucas linhas cada.
    O ler_dados(tmp_path) retorna as inscrições que você escreveu, e só elas."""
    pytest.skip('teste a escrever')


def test_2025_com_ponto_e_virgula(tmp_path):
    """O arquivo de 2025 usa ponto e vírgula. A inscrição de 2025 chega com cada coluna no lugar:
    o numero_peito dela é o que você escreveu no arquivo."""
    pytest.skip('teste a escrever')


def test_arquivo_que_falta_diz_qual(tmp_path):
    """Sem o edicoes.csv na pasta, o ler_dados para com FileNotFoundError, e a mensagem diz edicoes.csv."""
    pytest.skip('teste a escrever')


# ---------------------------------------------------------------- o chamar, com o urlopen trocado

def test_chamar_manda_o_token():
    """A chamada sai com o cabeçalho Authorization: Bearer seguido do token passado ao chamar."""
    pytest.skip('teste a escrever')


def test_chamar_tem_tempo_limite():
    """O urlopen recebe o tempo limite igual à espera passada ao chamar."""
    pytest.skip('teste a escrever')


# ---------------------------------------------------------------- o main, com a API falsa

def test_sem_token_nenhuma_chamada(api_falsa, tmp_path, monkeypatch):
    """Sem a variável API_TRIATLO_TOKEN, o main retorna 2, não faz nenhuma chamada e não grava nada."""
    pytest.skip('teste a escrever')
