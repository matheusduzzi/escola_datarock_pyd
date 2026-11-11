"""Os seus testes do exercício: melhor_por_atleta e ritmo_corrida.

Cada função abaixo tem o nome e, no comentário, o que o teste tem que mostrar. Troque o pytest.skip
pelo teste. Use entradas pequenas escritas à mão, como as de test_tabela.py, ou a fixture tabela,
que traz os dados do triatlo. Escreva o esperado a partir da promessa da função e de contas à mão,
nunca rodando a função e copiando o que apareceu.

Para rodar:
    python3 -m pytest test_exercicio.py
    python3 -m pytest test_exercicio.py --defeito E1
    python3 rodar_defeitos.py --exercicio
"""
import pandas as pd
import pytest

from transformacoes import melhor_por_atleta, montar_tabela, ritmo_corrida

EDICOES = pd.DataFrame({'edicao': [2024, 2025], 'natacao_km': [3.8, 1.9], 'corrida_km': [42.2, 42.2]})


# ---------------------------------------------------------------- regra de negócio

def test_melhor_fica_com_o_menor_tempo():
    """Um atleta que concluiu as duas edições fica com o menor tempo oficial e com a edição desse tempo."""
    pytest.skip('teste a escrever')


def test_quem_nao_concluiu_fica_fora():
    """Atleta que só tem DNF, DNS ou DSQ não aparece. Quem concluiu uma edição tem concluidas igual a 1."""
    pytest.skip('teste a escrever')


def test_ritmo_so_de_quem_concluiu():
    """DNF, DSQ e DNS ficam fora do ritmo da corrida, mesmo com a parcial da corrida preenchida."""
    pytest.skip('teste a escrever')


# ---------------------------------------------------------------- chave

def test_uma_linha_por_atleta_nos_dados(tabela):
    """Nos dados do triatlo: nenhum id_atleta repetido, e uma linha para cada atleta que concluiu."""
    pytest.skip('teste a escrever')


def test_mesmo_peito_atletas_diferentes():
    """Dois atletas diferentes que usaram o mesmo número de peito, um em cada edição, saem em duas linhas."""
    pytest.skip('teste a escrever')


# ---------------------------------------------------------------- tipos

def test_tipos_do_melhor(tabela):
    """Todas as colunas de melhor_por_atleta são int64, como a função promete."""
    pytest.skip('teste a escrever')


# ---------------------------------------------------------------- conta com decimais

def test_ritmo_corrida_exemplo():
    """Uma corrida de tempo conhecido dá o ritmo que você calculou à mão, com uma tolerância que você escolheu."""
    pytest.skip('teste a escrever')
