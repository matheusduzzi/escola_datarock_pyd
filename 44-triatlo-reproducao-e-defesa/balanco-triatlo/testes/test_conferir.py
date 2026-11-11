"""Os testes do conferir.py. Cada um monta uma pasta pequena no tmp_path e diz o que tem que sair.

De dentro da pasta do projeto:  python3 -m pytest -q testes
"""
import conferir


def pasta_com_saida(tmp_path):
    for c in conferir.ARQUIVOS:
        (tmp_path / c).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / c).write_bytes(c.encode("utf-8"))
    return tmp_path


def test_arquivos_iguais_reproduzem(tmp_path):
    pasta = pasta_com_saida(tmp_path)
    assert conferir.gravar(pasta) == []
    iguais, linhas, total = conferir.comparar(pasta)
    assert (iguais, total) == (4, 4)


def test_um_byte_diferente_aparece_com_o_nome_do_arquivo(tmp_path):
    pasta = pasta_com_saida(tmp_path)
    conferir.gravar(pasta)
    (pasta / "saida/relatorio/relatorio.md").write_bytes(b"outra coisa")
    iguais, linhas, total = conferir.comparar(pasta)
    assert iguais == 3
    assert [l.split()[1] for l in linhas if l.startswith("diferente")] == ["saida/relatorio/relatorio.md"]


def test_arquivo_faltando_nao_conta_como_igual(tmp_path):
    pasta = pasta_com_saida(tmp_path)
    conferir.gravar(pasta)
    (pasta / "saida/base_triatlo.csv").unlink()
    iguais, linhas, total = conferir.comparar(pasta)
    assert iguais == 3 and "faltando   saida/base_triatlo.csv" in linhas


def test_gravar_sem_um_arquivo_nao_grava_o_esperado(tmp_path):
    pasta = pasta_com_saida(tmp_path)
    (pasta / "saida/relatorio/figuras/etapas.png").unlink()
    assert conferir.gravar(pasta) == ["saida/relatorio/figuras/etapas.png"]
    assert not (pasta / conferir.ESPERADO).exists()
