"""Testes do cálculo. Rode da pasta do projeto: python3 -m pytest -q testes"""
import math

import pandas as pd

from tempos import calculo, leitura


def linha(id_atleta, categoria, status, natacao, t1, ciclismo, t2, corrida):
    return dict(id_atleta=id_atleta, categoria=categoria, status=status, natacao_s=natacao,
                t1_s=t1, ciclismo_s=ciclismo, t2_s=t2, corrida_s=corrida)


def test_total_soma_etapas_e_transicoes():
    tabela = pd.DataFrame([linha("A1", "Adulto", "terminou", 3600, 300, 18000, 240, 12000)])
    assert calculo.com_total(tabela)["total_s"].iloc[0] == 34140


def test_parcial_vazia_nao_vira_zero():
    tabela = pd.DataFrame([linha("A2", "Adulto", "DNF", 3700, 310, float("nan"), float("nan"), float("nan"))])
    assert math.isnan(calculo.com_total(tabela)["total_s"].iloc[0])


def test_so_quem_terminou_entra():
    tabela = pd.DataFrame([
        linha("A1", "Adulto", "terminou", 3600, 300, 18000, 240, 12000),
        linha("A2", "Adulto", "DNF", 3000, 300, 17000, float("nan"), float("nan")),
        linha("A3", "Adulto", "DNS", float("nan"), float("nan"), float("nan"), float("nan"), float("nan")),
    ])
    resumo = calculo.por_categoria(tabela, ["Adulto"])
    assert resumo.loc["Adulto", "atletas"] == 1
    assert resumo.loc["Adulto", "natacao"] == 3600


def test_relatorio_tem_todas_as_categorias():
    resultados = leitura.ler_resultados()
    tabela = calculo.por_categoria(resultados, leitura.ler_categorias())
    assert list(tabela.index) == ["Júnior", "Adulto", "Master", "Sênior"]
    assert tabela["atletas"].sum() == (resultados["status"] == "terminou").sum()


def test_tem_nao_terminaram():
    resultados = leitura.ler_resultados()
    tabela = calculo.por_categoria(resultados, leitura.ler_categorias())
    assert "nao_terminaram" in tabela.columns
