"""Os testes da integração do triatlo. Não usam a API nem os arquivos do triatlo.

Para rodar, de dentro da pasta do projeto:
    python3 -m pytest -q testes

Cada teste monta uma competição de três ou quatro inscrições, com o resultado que esperamos
escrito à mão a partir do contrato da aula 41. Os arquivos que um teste precisa ficam na
pasta temporária do pytest (tmp_path), nunca na pasta do projeto.
"""
import pandas as pd
import pytest

import coletar
import integrar
import rodar
from integrar import (AtletaSemCadastro, InscricaoConflitante, ResultadoConflitante, ResultadoSemInscricao,
                      conferir, ler_inscricoes, montar_base, unificar_resultados)

COMPLETO = {"natacao": "1:00:00", "t1": "0:05:00", "ciclismo": "5:00:00", "t2": "0:05:00", "corrida": "4:00:00"}


def resultado(id_inscricao, status="concluiu", oficial="10:10:00", pagina=1, posicao=1, **trocas):
    """Um resultado no formato da API. Por padrão, quem concluiu com as cinco parciais."""
    parciais = dict(COMPLETO, **trocas)
    return {"edicao": int(id_inscricao[:4]), "id_inscricao": id_inscricao, "numero_peito": 101,
            "status": status, "parciais": parciais, "tempo_oficial": oficial,
            "origem": {"pagina": pagina, "posicao": posicao}}


def pasta_com_arquivos(tmp_path, linhas_2025="2025-0001;2;101;F40-44;\n2025-0002;3;102;M30-34;Equipe Serra\n"):
    (tmp_path / "inscricoes_2024.csv").write_text(
        "id_inscricao,id_atleta,numero_peito,categoria,equipe\n2024-0001,1,101,M45-49,\n2024-0002,2,102,F40-44,\n",
        encoding="utf-8")
    (tmp_path / "inscricoes_2025.csv").write_text(
        "id_inscricao;id_atleta;numero_peito;categoria;equipe\n" + linhas_2025, encoding="utf-8")
    (tmp_path / "atletas.csv").write_text(
        "id_atleta,nome,sexo,ano_nascimento,uf\n1,A,M,1977,SP\n2,B,F,1982,PR\n3,C,M,1993,SC\n", encoding="utf-8")
    return tmp_path


def base_de(tmp_path, resultados):
    pasta = pasta_com_arquivos(tmp_path)
    inscricoes, _ = ler_inscricoes(pasta)
    unificados, _ = unificar_resultados(resultados)
    return montar_base(inscricoes, integrar.ler_atletas(pasta), unificados)


QUATRO = [resultado("2024-0001"), resultado("2024-0002", oficial="11:00:00", corrida="4:50:00"),
          resultado("2025-0001", status="DNF", oficial=None, t2=None, corrida=None),
          resultado("2025-0002", status="DNS", oficial=None, natacao=None, t1=None, ciclismo=None, t2=None,
                    corrida=None)]


# ---------------------------------------------------------------- arquivos

def test_inscricao_repetida_identica_conta_uma_vez(tmp_path):
    pasta = pasta_com_arquivos(tmp_path, "2025-0001;2;101;F40-44;\n2025-0001;2;101;F40-44;\n")
    inscricoes, contagem = ler_inscricoes(pasta)
    assert list(inscricoes["id_inscricao"]) == ["2024-0001", "2024-0002", "2025-0001"]
    assert contagem["inscricoes_2025.csv"] == {"linhas": 2, "repetidas": 1, "inscricoes": 1}


def test_inscricao_com_duas_versoes_para(tmp_path):
    pasta = pasta_com_arquivos(tmp_path, "2025-0001;2;101;F40-44;\n2025-0001;2;101;F45-49;\n")
    with pytest.raises(InscricaoConflitante, match="2025-0001"):
        ler_inscricoes(pasta)


# ---------------------------------------------------------------- resultados repetidos

def test_copia_identica_em_outra_pagina_conta_uma_vez():
    linhas = [resultado("2024-0001", pagina=1, posicao=47), resultado("2024-0002", pagina=1, posicao=48),
              resultado("2024-0001", pagina=2, posicao=11)]
    unificados, repetidos = unificar_resultados(linhas)
    assert list(unificados["id_inscricao"]) == ["2024-0001", "2024-0002"]
    assert repetidos == {"2024-0001": [{"pagina": 1, "posicao": 47}, {"pagina": 2, "posicao": 11}]}
    primeira = unificados.iloc[0]
    assert (primeira["origem_pagina"], primeira["origem_posicao"], primeira["copias"]) == (1, 47, 2)


def test_duas_versoes_do_resultado_param():
    linhas = [resultado("2025-0001"), resultado("2025-0001", oficial="10:12:00", pagina=2)]
    with pytest.raises(ResultadoConflitante, match="2025-0001"):
        unificar_resultados(linhas)


# ---------------------------------------------------------------- a base

def test_inscricao_sem_resultado_fica_com_nome(tmp_path):
    base = base_de(tmp_path, QUATRO[:3])  # 2025-0002 sem resultado
    linha = base.set_index("id_inscricao").loc["2025-0002"]
    assert linha["status"] == "sem resultado"
    assert linha[integrar.TEMPOS].isna().all()
    assert (len(base), linha["copias"], linha["parciais_vazias"]) == (4, 0, 5)


def test_resultado_sem_inscricao_para(tmp_path):
    with pytest.raises(ResultadoSemInscricao, match="2025-0999"):
        base_de(tmp_path, QUATRO + [resultado("2025-0999")])


def test_atleta_fora_do_cadastro_para(tmp_path):
    pasta = pasta_com_arquivos(tmp_path, "2025-0001;9;101;F40-44;\n")
    inscricoes, _ = ler_inscricoes(pasta)
    unificados, _ = unificar_resultados([])
    with pytest.raises(AtletaSemCadastro, match="9"):
        montar_base(inscricoes, integrar.ler_atletas(pasta), unificados)


def test_parcial_vazia_continua_vazia(tmp_path):
    base = base_de(tmp_path, [resultado("2024-0001", oficial="10:10:00", t1=None)] + QUATRO[1:])
    linha = base.set_index("id_inscricao").loc["2024-0001"]
    assert pd.isna(linha["t1_s"])                        # vazio, e não zero
    assert linha["oficial_s"] == 10 * 3600 + 10 * 60     # o tempo oficial fica como veio
    assert linha["parciais_vazias"] == 1
    assert str(base["t1_s"].dtype) == "Int64"


# ---------------------------------------------------------------- as regras do contrato

def test_base_boa_passa_nas_regras(tmp_path):
    assert conferir(base_de(tmp_path, QUATRO)) == []


QUEBRAS = {
    "DNS e sem resultado não têm parcial": ("2025-0002", {"natacao_s": 3600}),
    "só quem concluiu tem tempo oficial": ("2025-0001", {"oficial_s": 36000}),
    "quem concluiu tem tempo oficial": ("2024-0001", {"oficial_s": pd.NA}),
    "cinco parciais somam o tempo oficial": ("2024-0002", {"oficial_s": 39000}),
    "DNF não tem parcial depois de uma etapa vazia": ("2025-0001", {"t1_s": pd.NA}),
    "nenhum tempo zero ou negativo": ("2024-0001", {"t1_s": 0, "oficial_s": 36300}),
    "sexo do cadastro igual à letra da categoria": ("2024-0002", {"sexo": "M"}),
    "uma linha por inscrição": ("2024-0001", {"id_inscricao": "2024-0002"}),
    "edição igual ao começo do id_inscricao": ("2024-0001", {"edicao": 2025}),
    "status conhecido": ("2025-0002", {"status": "desistiu"}),
}


@pytest.mark.parametrize("regra", list(QUEBRAS))
def test_conferir_acusa_a_regra_quebrada(tmp_path, regra):
    base = base_de(tmp_path, QUATRO)
    id_inscricao, trocas = QUEBRAS[regra]
    linha = base.index[base["id_inscricao"] == id_inscricao][0]
    for coluna, valor in trocas.items():
        base.loc[linha, coluna] = valor
    problemas = conferir(base)
    assert [p.split(":")[0] for p in problemas] == [regra]


# ---------------------------------------------------------------- o rodar.py grava só se passou

@pytest.fixture
def sem_api(tmp_path, monkeypatch):
    """Troca a coleta pela lista que o teste escolher e aponta os arquivos para a pasta do teste."""
    dados = tmp_path / "dados"
    dados.mkdir()
    monkeypatch.setattr(integrar, "DADOS", pasta_com_arquivos(dados))
    monkeypatch.setenv("API_TRIATLO_TOKEN", "kit-local")
    respostas = {}

    def coleta_falsa(endereco, token, filtros, por_pagina=100, espera=10, mostrar=print, falhas=None, **outros):
        linhas = [r for r in respostas["linhas"] if str(r["edicao"]) == filtros["edicao"]]
        return linhas, {"linhas": len(linhas), "total_paginas": 1, "total_api": len(linhas)}

    monkeypatch.setattr(coletar, "coletar", coleta_falsa)
    return respostas


def test_rodar_grava_quando_tudo_passa(sem_api, tmp_path, capsys):
    sem_api["linhas"] = QUATRO
    assert rodar.main(["--saida", str(tmp_path / "saida")]) == 0
    gravada = integrar.ler_base(tmp_path / "saida" / "base_triatlo.csv")
    assert list(gravada["status"]) == ["concluiu", "concluiu", "DNF", "DNS"]
    assert gravada["t2_s"].isna().sum() == 2 and str(gravada["t2_s"].dtype) == "Int64"


def test_rodar_nao_grava_quando_uma_regra_quebra(sem_api, tmp_path, capsys):
    dns_com_parcial = resultado("2025-0002", status="DNS", oficial=None, t1=None, ciclismo=None, t2=None, corrida=None)
    sem_api["linhas"] = QUATRO[:3] + [dns_com_parcial]  # o DNS chegou com a natação
    assert rodar.main(["--saida", str(tmp_path / "saida")]) == 1
    assert not (tmp_path / "saida").exists()
    assert "DNS e sem resultado não têm parcial: 1 inscrição(ões), ex.: 2025-0002" in capsys.readouterr().out
