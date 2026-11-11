"""Os testes do exercício. Complete cada um; hoje todos falham de propósito.

Para rodar, de dentro da pasta da aula:
    python3 -m pytest -q test_recuperados.py

base_pequena() monta uma base de quatro inscrições com as funções do integrar.py, sem a API e
sem os arquivos do triatlo. recuperado() monta um resultado no formato da API. Use as duas e
escreva o resultado esperado à mão, a partir das regras do enunciado.
"""
import pandas as pd
import pytest

import integrar
from recuperados import juntar_recuperados

COMPLETO = {"natacao": "1:00:00", "t1": "0:05:00", "ciclismo": "5:00:00", "t2": "0:05:00", "corrida": "4:00:00"}


def recuperado(id_inscricao, status="concluiu", oficial="10:10:00", **trocas):
    """Um resultado no formato da API. Por padrão, quem concluiu com as cinco parciais."""
    return {"edicao": int(id_inscricao[:4]), "id_inscricao": id_inscricao, "numero_peito": 101,
            "status": status, "parciais": dict(COMPLETO, **trocas), "tempo_oficial": oficial}


def base_pequena():
    """2024-0001 concluiu, 2024-0002 DNF, 2025-0001 e 2025-0002 sem resultado."""
    inscricoes = pd.DataFrame({"id_inscricao": ["2024-0001", "2024-0002", "2025-0001", "2025-0002"],
                               "id_atleta": [1, 2, 3, 4], "numero_peito": [101, 102, 101, 102],
                               "categoria": ["M45-49", "F40-44", "M30-34", "F18-24"], "equipe": [None] * 4,
                               "edicao": [2024, 2024, 2025, 2025]})
    atletas = pd.DataFrame({"id_atleta": [1, 2, 3, 4], "sexo": ["M", "F", "M", "F"]})
    resultados, _ = integrar.unificar_resultados([
        dict(recuperado("2024-0001"), origem={"pagina": 1, "posicao": 1}),
        dict(recuperado("2024-0002", status="DNF", oficial=None, t2=None, corrida=None),
             origem={"pagina": 1, "posicao": 2})])
    return integrar.montar_base(inscricoes, atletas, resultados)


def test_preenche_quem_estava_sem_resultado():
    """Regra 1: 2025-0001 sai de "sem resultado" com o status e os tempos do recuperado,
    fonte_resultado "recuperados", copias 1, parciais_vazias certo e origem vazia. Nenhuma pendência."""
    pytest.fail("escreva este teste")


def test_igual_ao_que_a_base_tem_nao_muda_nada():
    """Regra 2: um recuperado igual ao 2024-0001 da base não muda a base e não vira pendência."""
    pytest.fail("escreva este teste")


def test_diferente_do_que_a_base_tem_vira_pendencia():
    """Regra 3: um recuperado que diz DNF para o 2024-0001 não troca a linha da base."""
    pytest.fail("escreva este teste")


def test_inscricao_que_nao_existe_vira_pendencia():
    """Regra 4: 2025-0999 não entra na base, que continua com quatro linhas."""
    pytest.fail("escreva este teste")


def test_copia_identica_conta_uma_vez_e_duas_versoes_param():
    """Regra 5: duas cópias iguais preenchem com copias 2; duas versões diferentes não preenchem."""
    pytest.fail("escreva este teste")


def test_recuperado_que_quebra_uma_regra_nao_entra():
    """Regra 6: um "concluiu" sem tempo oficial deixa a inscrição "sem resultado" e diz qual regra quebrou."""
    pytest.fail("escreva este teste")


def test_a_base_que_entrou_nao_muda():
    """Regra 7: depois de juntar, a base que você passou continua igual a uma cópia feita antes."""
    pytest.fail("escreva este teste")
