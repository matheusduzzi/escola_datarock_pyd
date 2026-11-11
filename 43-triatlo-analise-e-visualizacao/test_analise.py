"""Os testes da análise. Cada um monta uma prova pequena, escrita à mão, e diz o que tem que sair.

Nenhum teste usa a base do triatlo. De dentro da pasta da aula:  python3 -m pytest -q test_analise.py
"""
import pandas as pd
import pytest

import analise

# O Matplotlib de algumas instalações avisa de funções antigas do pyparsing ao desenhar. O aviso não muda o resultado.
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

COLUNAS = ["edicao", "id_inscricao", "id_atleta", "categoria", "status"] + [f"{e}_s" for e in analise.ETAPAS] + ["oficial_s"]
V = None  # tempo vazio


def base(*linhas):
    """Cada linha: (edicao, id_inscricao, id_atleta, categoria, status, natacao, t1, ciclismo, t2, corrida, oficial)."""
    b = pd.DataFrame(linhas, columns=COLUNAS)
    for c in COLUNAS[5:]:
        b[c] = b[c].astype("Int64")
    return b


def edicoes(natacao=(3.8, 1.9), temperatura=(24, 24), observacao=("percurso completo", "percurso completo")):
    return pd.DataFrame({"edicao": [2024, 2025], "natacao_km": natacao, "ciclismo_km": [180, 180],
                         "corrida_km": [42.2, 42.2], "temperatura_max_c": temperatura,
                         "observacao": observacao}).set_index("edicao")


def concluiu(ed, i, nat=3600, t1=300, cic=21600, t2=300, cor=15000, atleta=None, categoria="M40-44"):
    partes = [nat, t1, cic, t2, cor]
    return (ed, f"{ed}-{i:04d}", atleta or i, categoria, "concluiu", *partes, sum(p for p in partes if p is not None))


def test_mediana_da_etapa_ignora_o_vazio_e_diz_quantos_entram():
    b = base(concluiu(2024, 1, t1=200), concluiu(2024, 2, t1=400), concluiu(2024, 3, t1=V),
             concluiu(2025, 4), concluiu(2025, 5))
    t1 = analise.etapas(b, edicoes()).loc["T1"]
    assert t1["mediana_2024"] == 5.0          # (200 + 400) / 2 s = 300 s; com zero no vazio daria 200 s
    assert t1["n_2024"] == 2 and t1["vazias_2024"] == 1


def test_etapa_com_distancia_diferente_nao_ganha_diferenca():
    b = base(concluiu(2024, 1, nat=4000), concluiu(2025, 2, nat=2000))
    tab = analise.etapas(b, edicoes(natacao=(3.8, 1.9)))
    assert tab.at["natação", "situacao"] == "não comparável"
    assert pd.isna(tab.at["natação", "diferenca"])
    assert tab.at["natação", "mediana_2025"] == pytest.approx(2000 / 60)  # o tempo aparece, a diferença não


def test_etapa_com_a_mesma_distancia_ganha_diferenca():
    b = base(concluiu(2024, 1, cor=15000), concluiu(2025, 2, cor=16200))
    tab = analise.etapas(b, edicoes(natacao=(3.8, 3.8)))
    assert tab.at["corrida", "situacao"] == "comparável"
    assert tab.at["corrida", "diferenca"] == pytest.approx(20.0)
    assert tab.at["natação", "situacao"] == "comparável"


def test_desistencia_divide_por_quem_largou():
    b = base(concluiu(2025, 1),
             (2025, "2025-0002", 2, "M40-44", "DNF", 3600, 300, V, V, V, V),
             (2025, "2025-0003", 3, "M40-44", "DSQ", 3600, 300, 21600, 300, 15000, V),
             (2025, "2025-0004", 4, "M40-44", "DNS", V, V, V, V, V, V),
             (2025, "2025-0005", 5, "M40-44", "sem resultado", V, V, V, V, V, V))
    d = analise.desistencia(b).loc[2025]
    assert (d["dnf"], d["largaram"]) == (1, 3)  # DNS e sem resultado ficam fora; DSQ largou e não é DNF
    assert d["pct"] == pytest.approx(100 / 3)


def test_onde_parou_e_a_primeira_etapa_vazia():
    b = base((2025, "2025-0001", 1, "M40-44", "DNF", 3600, 300, 21600, 300, V, V),
             (2025, "2025-0002", 2, "M40-44", "DNF", 3600, 300, V, V, V, V))
    assert list(analise.onde_parou(b)) == ["corrida", "ciclismo"]
    d = analise.desistencia(b).loc[2025]
    assert (d["corrida"], d["ciclismo"], d["natação"]) == (1, 1, 0)


def test_categoria_pequena_fica_marcada_e_fora_do_ranking():
    grande = [concluiu(2025, i, categoria="M40-44") for i in range(1, 21)]
    grande[0] = (2025, "2025-0001", 1, "M40-44", "DNF", 3600, 300, V, V, V, V)
    pequena = [(2025, "2025-0101", 101, "F55-59", "DNF", 3600, 300, V, V, V, V), concluiu(2025, 102, categoria="F55-59")]
    taxas = analise.taxa_por_categoria(base(*grande, *pequena), minimo=20)
    assert taxas.loc[(2025, "F55-59"), "pct"] == 50.0 and taxas.loc[(2025, "F55-59"), "pequeno"]
    assert not taxas.loc[(2025, "M40-44"), "pequeno"]
    assert list(analise.ranking(taxas, 2025).index) == ["M40-44"]  # 1 de 20 entra; 1 de 2 não


def test_condicao_diferente_entra_nas_limitacoes():
    b = base(concluiu(2024, 1), concluiu(2025, 2))
    taxas = analise.taxa_por_categoria(b)
    iguais = analise.limitacoes(b, edicoes(natacao=(3.8, 3.8)), taxas)
    quente = analise.limitacoes(b, edicoes(natacao=(3.8, 3.8), temperatura=(24, 31)), taxas)
    assert not any("condições mudaram" in item for item in iguais)
    assert any("24 °C" in item and "31 °C" in item for item in quente)


def test_mesmas_pessoas_pelo_id_atleta():
    b = base(concluiu(2024, 1, atleta=7, categoria="M40-44"), concluiu(2025, 1, atleta=8, categoria="M40-44"),
             concluiu(2024, 2, atleta=9, categoria="M40-44"), concluiu(2025, 2, atleta=9, categoria="M45-49"))
    # o id_inscricao termina igual (2024-0001 e 2025-0001), mas só o atleta 9 correu as duas
    assert analise.mesmas_pessoas(b) == {"nas_duas": 1, "mudaram": 1}


def test_relatorio_grava_as_limitacoes_e_nao_compara_a_natacao(tmp_path):
    b = base(concluiu(2024, 1, nat=4000), concluiu(2025, 2, nat=2000, cor=16200))
    hashes = analise.gerar(b, edicoes(temperatura=(24, 31)), tmp_path, {"nome": "teste.csv", "sha256": "0" * 64})
    texto = (tmp_path / "relatorio.md").read_text(encoding="utf-8")
    assert set(hashes) == {"relatorio.md", "figuras/etapas.png", "figuras/categorias.png"}
    assert "## Limitações" in texto and "A natação não é comparada" in texto
    assert "| natação | não comparável: 3,8 km em 2024, 1,9 km em 2025 | 66,7 (n=1) | 33,3 (n=1) |  |" in texto
