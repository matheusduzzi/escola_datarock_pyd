"""Os testes da aula «Escrever testes de dados e funções».

Rodar de dentro da pasta da aula:
    python3 -m pytest
Cada bloco testa uma coisa: regra de negócio, chave, tipos e conta com decimais.
Os esperados saem das promessas no comentário de cada função, de contas à mão e do relatório da aula 34.
"""
import pandas as pd
import pytest

from transformacoes import (ResultadoDuplicado, ResultadoSemInscricao, montar_tabela, ritmo_natacao,
                            taxa_conclusao)

EDICOES = pd.DataFrame({'edicao': [2024, 2025], 'natacao_km': [3.8, 1.9], 'corrida_km': [42.2, 42.2]})


def inscricao(ident, atleta=1, peito=101):
    return {'id_inscricao': ident, 'id_atleta': atleta, 'numero_peito': peito, 'categoria': 'M45-49',
            'equipe': None}


def resultado(ident, status='concluiu', natacao='1:14:19', t1='0:05:10', oficial='12:13:18'):
    parciais = {'natacao': natacao, 't1': t1, 'ciclismo': '6:02:35', 't2': '0:05:30', 'corrida': '4:45:44'}
    return {'edicao': int(ident[:4]), 'id_inscricao': ident, 'numero_peito': 101, 'status': status,
            'parciais': parciais, 'tempo_oficial': oficial}


# ---------------------------------------------------------------- regra de negócio

def test_taxa_conta_so_quem_largou():
    tabela = pd.DataFrame({'edicao': [2025] * 6,
                           'status': ['concluiu', 'concluiu', 'DNF', 'DSQ', 'DNS', 'sem resultado']})
    linha = taxa_conclusao(tabela).loc[2025]
    assert linha['inscritos'] == 6
    assert linha['largaram'] == 4  # concluiu, concluiu, DNF e DSQ
    assert linha['concluiram'] == 2
    assert linha['taxa_pct'] == pytest.approx(50.0)


def test_taxa_sem_ninguem_largando_fica_vazia():
    tabela = pd.DataFrame({'edicao': [2025, 2025], 'status': ['DNS', 'sem resultado']})
    linha = taxa_conclusao(tabela).loc[2025]
    assert linha['largaram'] == 0
    assert pd.isna(linha['taxa_pct'])


def test_taxa_de_2025_igual_a_do_relatorio(tabela):
    linha = taxa_conclusao(tabela).loc[2025]
    assert (linha['concluiram'], linha['largaram']) == (393, 441)
    assert linha['taxa_pct'] == pytest.approx(89.1, abs=0.05)  # o relatório mostra uma casa: 89,1%


# ---------------------------------------------------------------- chave

def test_repetida_e_copia_contam_uma_vez():
    inscricoes = pd.DataFrame([inscricao('2025-0001'), inscricao('2025-0001'), inscricao('2025-0002', 2, 102)])
    resultados = [resultado('2025-0001'), resultado('2025-0001'), resultado('2025-0002')]
    t = montar_tabela(inscricoes, resultados)
    assert list(t['id_inscricao']) == ['2025-0001', '2025-0002']


def test_duas_versoes_do_mesmo_resultado_param():
    inscricoes = pd.DataFrame([inscricao('2025-0001')])
    resultados = [resultado('2025-0001'), resultado('2025-0001', status='DNF', oficial=None)]
    with pytest.raises(ResultadoDuplicado):
        montar_tabela(inscricoes, resultados)


def test_resultado_sem_inscricao_para():
    inscricoes = pd.DataFrame([inscricao('2025-0001')])
    resultados = [resultado('2025-0001'), resultado('2025-0002')]
    with pytest.raises(ResultadoSemInscricao, match='2025-0002'):
        montar_tabela(inscricoes, resultados)


def test_uma_linha_por_inscricao_nos_dados(tabela, dados):
    inscricoes, _, _ = dados
    assert len(tabela) == len(inscricoes.drop_duplicates()) == 880
    assert not tabela.duplicated(['edicao', 'id_inscricao']).any()


# ---------------------------------------------------------------- tipos

TIPOS = {'edicao': 'int64', 'id_atleta': 'int64', 'numero_peito': 'int64',
         'natacao_s': 'Int64', 't1_s': 'Int64', 'ciclismo_s': 'Int64', 't2_s': 'Int64',
         'corrida_s': 'Int64', 'oficial_s': 'Int64'}


def test_tipos_da_tabela(tabela):
    assert {coluna: str(tabela[coluna].dtype) for coluna in TIPOS} == TIPOS
    for coluna in ['id_inscricao', 'categoria', 'status']:
        assert pd.api.types.is_string_dtype(tabela[coluna]), coluna


def test_tempo_vazio_continua_vazio():
    inscricoes = pd.DataFrame([inscricao('2024-0001')])
    t = montar_tabela(inscricoes, [resultado('2024-0001', t1=None)])
    assert t.loc[0, 't1_s'] is pd.NA
    assert t.loc[0, 'natacao_s'] == 4459


# ---------------------------------------------------------------- conta com decimais

def test_ritmo_natacao_2024():
    t = montar_tabela(pd.DataFrame([inscricao('2024-0002')]), [resultado('2024-0002', natacao='1:14:19')])
    # à mão: 74,32 minutos em 3,8 km, que são 38 trechos de 100 m: 1,956 min por 100 m
    assert ritmo_natacao(t, EDICOES).iloc[0] == pytest.approx(1.96, abs=0.005)


def test_ritmo_natacao_2025():
    t = montar_tabela(pd.DataFrame([inscricao('2025-0002')]), [resultado('2025-0002', natacao='0:33:20')])
    # à mão: 33,33 minutos em 1,9 km, que são 19 trechos de 100 m: 1,754 min por 100 m
    assert ritmo_natacao(t, EDICOES).iloc[0] == pytest.approx(1.75, abs=0.005)


def test_sem_natacao_fica_fora_do_ritmo():
    t = montar_tabela(pd.DataFrame([inscricao('2025-0001'), inscricao('2025-0002', 2, 102)]),
                      [resultado('2025-0001', status='DNS', natacao=None, oficial=None), resultado('2025-0002')])
    assert list(ritmo_natacao(t, EDICOES).index) == [1]
