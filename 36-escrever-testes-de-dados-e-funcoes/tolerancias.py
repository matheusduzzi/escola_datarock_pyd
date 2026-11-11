"""Três jeitos de comparar o mesmo ritmo. Aula «Escrever testes de dados e funções».

Este arquivo não começa com test_, então o pytest não roda ele junto com os outros.
Para rodar, diga o nome:
    python3 -m pytest tolerancias.py
Dois dos três testes falham de propósito com a função certa. A aula explica por quê.
"""
import pandas as pd
import pytest

from transformacoes import montar_tabela, ritmo_natacao

EDICOES = pd.DataFrame({'edicao': [2024, 2025], 'natacao_km': [3.8, 1.9], 'corrida_km': [42.2, 42.2]})
INSCRICAO = pd.DataFrame([{'id_inscricao': '2024-0002', 'id_atleta': 2, 'numero_peito': 102,
                           'categoria': 'M55-59', 'equipe': None}])
RESULTADO = [{'edicao': 2024, 'id_inscricao': '2024-0002', 'numero_peito': 102, 'status': 'concluiu',
              'parciais': {'natacao': '1:14:19', 't1': '0:05:10', 'ciclismo': '6:02:35', 't2': '0:05:30',
                           'corrida': '4:45:44'}, 'tempo_oficial': '12:13:18'}]


def ritmo():
    return ritmo_natacao(montar_tabela(INSCRICAO, RESULTADO), EDICOES).iloc[0]


def test_igual():
    assert ritmo() == 1.96


def test_approx_sem_tolerancia():
    assert ritmo() == pytest.approx(1.96)


def test_approx_larga():
    assert ritmo() == pytest.approx(1.96, abs=0.05)
