"""O esqueleto dos testes do exercício. Cada teste tem o nome e o que tem que mostrar; você escreve o corpo.

Monte bases pequenas à mão, como em test_analise.py (dá para importar a função base e a concluiu de lá).
De dentro da pasta da aula:  python3 -m pytest -q test_faixas.py
"""
import pytest

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


def test_faixa_sai_da_categoria():
    """M50-54 e F65+ ficam em '50 ou mais'; M45-49 e F18-24 ficam em 'até 49'. Com corte=60, M55-59 fica em 'até 59'."""
    pytest.fail("escreva este teste")


def test_dnf_divide_por_quem_largou():
    """Num grupo com um concluiu, um DNF, um DSQ e um DNS, dnf=1, largaram=3 e dnf_pct é 33,3."""
    pytest.fail("escreva este teste")


def test_dnf_corrida_conta_so_quem_parou_na_corrida():
    """Um DNF sem tempo de ciclismo e outro sem tempo de corrida: dnf=2 e dnf_corrida=1."""
    pytest.fail("escreva este teste")


def test_corrida_mediana_so_de_quem_concluiu():
    """Um DSQ com corrida de 1000 min e um concluiu com corrida vazia não entram: a mediana é a dos outros concluintes."""
    pytest.fail("escreva este teste")
