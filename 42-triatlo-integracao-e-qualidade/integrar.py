"""A integração do projeto do triatlo: arquivos de inscrição, cadastro de atletas e resultados da API.

As funções seguem o contrato da aula 41, «Triatlo: briefing e contrato»:
- o grão da base é a inscrição: uma linha por id_inscricao;
- linha repetida idêntica conta uma vez; duas versões diferentes da mesma coisa param a integração;
- inscrição sem resultado fica com o status "sem resultado", sem sumir no merge;
- parcial vazia continua vazia: tempo que não existe não vira zero;
- o tempo total é o tempo oficial, nunca a soma das parciais.

Para usar no Python, de dentro da pasta da aula:
    from integrar import ler_inscricoes, ler_atletas, unificar_resultados, montar_base, conferir

O rodar.py usa estas funções na ordem. Os testes ficam em test_integrar.py.
"""
import json
from pathlib import Path

import pandas as pd

DADOS = Path(__file__).resolve().parent.parent / "dados" / "triatlo"
ETAPAS = ["natacao", "t1", "ciclismo", "t2", "corrida"]
TEMPOS = [f"{e}_s" for e in ETAPAS] + ["oficial_s"]
STATUS = ["concluiu", "DNF", "DNS", "DSQ", "sem resultado"]
COLUNAS = (["edicao", "id_inscricao", "id_atleta", "sexo", "numero_peito", "categoria", "equipe", "status"]
           + TEMPOS + ["parciais_vazias", "motivo", "fonte_resultado", "origem_pagina", "origem_posicao", "copias"])


class InscricaoConflitante(ValueError):
    """O mesmo id_inscricao aparece com conteúdo diferente nos arquivos de inscrição."""


class ResultadoConflitante(ValueError):
    """A API mandou duas versões diferentes do resultado da mesma inscrição."""


class ResultadoSemInscricao(ValueError):
    """A API mandou o resultado de uma inscrição que não está nos arquivos de inscrição."""


class AtletaSemCadastro(ValueError):
    """Uma inscrição aponta para um id_atleta que não está no atletas.csv."""


class RegraQuebrada(ValueError):
    """A base montada quebrou uma ou mais regras do contrato (veja conferir)."""


def segundos(texto):
    """'1:14:19' vira 4459. None continua vazio (pd.NA): tempo que não existe não é zero."""
    if texto is None:
        return pd.NA
    h, m, s = (int(p) for p in texto.split(":"))
    return h * 3600 + m * 60 + s


# ---------------------------------------------------------------- arquivos

def ler_inscricoes(pasta=DADOS):
    """As duas edições numa tabela só, com a coluna edicao. Retorna (inscricoes, contagem).

    O arquivo de 2024 usa vírgula e o de 2025 usa ponto e vírgula. Linha repetida idêntica sai.
    O mesmo id_inscricao com conteúdo diferente para com InscricaoConflitante.
    contagem diz, por arquivo, quantas linhas foram lidas e quantas repetidas saíram.
    """
    pasta = Path(pasta)
    partes, contagem = [], {}
    for edicao, nome, sep in [(2024, "inscricoes_2024.csv", ","), (2025, "inscricoes_2025.csv", ";")]:
        tabela = pd.read_csv(pasta / nome, sep=sep, dtype={"id_inscricao": str, "equipe": str})
        repetidas = int(tabela.duplicated().sum())
        tabela = tabela.drop_duplicates().assign(edicao=edicao)
        contagem[nome] = {"linhas": len(tabela) + repetidas, "repetidas": repetidas, "inscricoes": len(tabela)}
        partes.append(tabela)
    inscricoes = pd.concat(partes, ignore_index=True)
    conflito = inscricoes[inscricoes["id_inscricao"].duplicated(keep=False)]
    if len(conflito):
        ids = sorted(conflito["id_inscricao"].unique())
        raise InscricaoConflitante(f"{len(ids)} inscrição(ões) com duas versões diferentes: {', '.join(ids)}")
    return inscricoes, contagem


def ler_atletas(pasta=DADOS):
    """O cadastro, uma linha por id_atleta."""
    atletas = pd.read_csv(Path(pasta) / "atletas.csv")
    if atletas["id_atleta"].duplicated().any():
        raise ValueError("atletas.csv tem id_atleta repetido")
    return atletas


# ---------------------------------------------------------------- resultados da API

def linha_do_resultado(r):
    """Um resultado da API (um dicionário) vira uma linha da base, com os tempos em segundos."""
    linha = {"edicao": int(r["edicao"]), "id_inscricao": r["id_inscricao"], "status": r["status"],
             "oficial_s": segundos(r.get("tempo_oficial")), "motivo": r.get("motivo")}
    parciais = r.get("parciais") or {}
    for etapa in ETAPAS:
        linha[f"{etapa}_s"] = segundos(parciais.get(etapa))
    return linha


def sem_origem(r):
    """O resultado sem a chave origem, que a coleta acrescenta: é o que a API mandou."""
    return {k: v for k, v in r.items() if k != "origem"}


def unificar_resultados(linhas):
    """Uma linha por inscrição, a partir das linhas da coleta. Retorna (resultados, repetidos).

    Compara as cópias do mesmo id_inscricao depois da coleta inteira: a cópia pode estar em outra
    página. Cópia idêntica conta uma vez e fica com a origem da primeira. Duas versões diferentes
    param com ResultadoConflitante: nenhum campo diz qual é a certa.
    repetidos lista cada id que veio mais de uma vez, com a origem de cada cópia.
    """
    primeiras, origens = {}, {}
    for r in linhas:
        chave = r["id_inscricao"]
        origens.setdefault(chave, []).append(r.get("origem"))
        if chave not in primeiras:
            primeiras[chave] = r
        elif sem_origem(primeiras[chave]) != sem_origem(r):
            raise ResultadoConflitante(f"duas versões diferentes do resultado {chave}: origens {origens[chave]}")
    saida = []
    for chave, r in primeiras.items():
        linha = linha_do_resultado(r)
        origem = r.get("origem") or {}
        linha.update(fonte_resultado="api", origem_pagina=origem.get("pagina"), origem_posicao=origem.get("posicao"),
                     copias=len(origens[chave]))
        saida.append(linha)
    resultados = pd.DataFrame(saida, columns=["edicao", "id_inscricao", "status"] + TEMPOS
                              + ["motivo", "fonte_resultado", "origem_pagina", "origem_posicao", "copias"])
    repetidos = {k: v for k, v in origens.items() if len(v) > 1}
    return resultados, repetidos


# ---------------------------------------------------------------- a base

def montar_base(inscricoes, atletas, resultados):
    """Uma linha por inscrição, com o sexo do cadastro e o resultado quando existe.

    A junção parte das inscrições (how="left"): quem não tem resultado fica, com o status
    "sem resultado" e os tempos vazios. Resultado de inscrição que não existe para com
    ResultadoSemInscricao; inscrição de atleta fora do cadastro para com AtletaSemCadastro.
    Os tempos ficam em segundos, no tipo Int64, que aceita vazio.
    """
    chaves = inscricoes[["edicao", "id_inscricao"]]
    sobra = resultados.merge(chaves, on=["edicao", "id_inscricao"], how="left", indicator=True)
    sobra = sobra[sobra["_merge"] == "left_only"]
    if len(sobra):
        raise ResultadoSemInscricao(f"{len(sobra)} resultado(s) sem inscrição: {', '.join(sobra['id_inscricao'])}")
    faltam = sorted(set(inscricoes["id_atleta"]) - set(atletas["id_atleta"]))
    if faltam:
        raise AtletaSemCadastro(f"{len(faltam)} id_atleta fora do cadastro: {', '.join(map(str, faltam))}")

    base = inscricoes.merge(atletas[["id_atleta", "sexo"]], on="id_atleta", how="left", validate="many_to_one")
    base = base.merge(resultados, on=["edicao", "id_inscricao"], how="left", validate="one_to_one")
    base["status"] = base["status"].fillna("sem resultado")
    for c in TEMPOS + ["origem_pagina", "origem_posicao"]:
        base[c] = base[c].astype("Int64")
    base["copias"] = base["copias"].fillna(0).astype("int64")  # quantas vezes a API mandou; 0 = nenhuma
    base["parciais_vazias"] = base[[f"{e}_s" for e in ETAPAS]].isna().sum(axis=1).astype("int64")
    return base[COLUNAS].sort_values(["edicao", "id_inscricao"]).reset_index(drop=True)


# ---------------------------------------------------------------- a conferência

def conferir(base):
    """As regras do contrato, uma por uma. Retorna a lista de problemas; vazia quer dizer que a base passou.

    Cada problema diz a regra, quantas linhas quebram e até cinco id_inscricao.
    """
    problemas = []
    parciais = base[[f"{e}_s" for e in ETAPAS]]
    tem_parcial = parciais.notna().any(axis=1)
    tem_oficial = base["oficial_s"].notna()
    concluiu = base["status"] == "concluiu"
    completas = concluiu & parciais.notna().all(axis=1)
    soma = parciais.sum(axis=1, min_count=1)
    depois_de_vazia = parciais.isna().cummax(axis=1) & parciais.notna()

    regras = [
        ("uma linha por inscrição", base["id_inscricao"].duplicated(keep=False)),
        ("edição igual ao começo do id_inscricao", base["id_inscricao"].str[:4] != base["edicao"].astype(str)),
        ("status conhecido", ~base["status"].isin(STATUS)),
        ("DNS e sem resultado não têm parcial", base["status"].isin(["DNS", "sem resultado"]) & tem_parcial),
        ("quem concluiu tem tempo oficial", concluiu & ~tem_oficial),
        ("só quem concluiu tem tempo oficial", ~concluiu & tem_oficial),
        ("cinco parciais somam o tempo oficial", completas & tem_oficial & (soma != base["oficial_s"])),
        ("DNF não tem parcial depois de uma etapa vazia",
         (base["status"] == "DNF") & depois_de_vazia.any(axis=1)),
        ("nenhum tempo zero ou negativo", (base[TEMPOS] <= 0).fillna(False).any(axis=1)),
        ("sexo do cadastro igual à letra da categoria", base["sexo"] != base["categoria"].str[0]),
    ]
    for nome, quebra in regras:
        quebra = quebra.fillna(False).astype(bool)
        if quebra.any():
            ids = list(base.loc[quebra, "id_inscricao"].drop_duplicates())
            problemas.append(f"{nome}: {len(ids)} inscrição(ões), ex.: {', '.join(ids[:5])}")
    return problemas


QUANTAS_REGRAS = 10


# ---------------------------------------------------------------- ler a base gravada

def ler_base(caminho):
    """Lê o base_triatlo.csv que o rodar.py grava, com os mesmos tipos da base em memória."""
    tipos = {c: "Int64" for c in TEMPOS + ["origem_pagina", "origem_posicao"]}
    tipos.update(id_inscricao=str, equipe=str, motivo=str, fonte_resultado=str, categoria=str, sexo=str, status=str)
    base = pd.read_csv(caminho, dtype=tipos, keep_default_na=False, na_values=[""])
    return base[COLUNAS]


def resultados_do_arquivo(caminho):
    """Uma lista de resultados no formato da API, lida de um arquivo JSON."""
    return json.loads(Path(caminho).read_text(encoding="utf-8"))
