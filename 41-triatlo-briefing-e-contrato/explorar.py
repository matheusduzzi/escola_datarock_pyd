"""Primeira olhada nos dados do triatlo, antes de escrever o contrato.

Rode de dentro da pasta da aula:

    python3 explorar.py

Lê os arquivos de ../dados/triatlo/ e mostra, em nove partes, o que cada arquivo tem:
quantas linhas, qual coluna é a chave, o que se repete, que status aparecem, onde há
tempo vazio e a desistência com dois denominadores. Não grava nada.
"""
import json
from pathlib import Path

import pandas as pd

DADOS = Path(__file__).resolve().parent.parent / "dados" / "triatlo"
ETAPAS = ["natacao", "t1", "ciclismo", "t2", "corrida"]
PARCIAIS = [f"parciais.{e}" for e in ETAPAS]
LARGOU = ["concluiu", "DNF", "DSQ"]


def ler():
    atletas = pd.read_csv(DADOS / "atletas.csv")
    edicoes = pd.read_csv(DADOS / "edicoes.csv")
    i24 = pd.read_csv(DADOS / "inscricoes_2024.csv").assign(edicao=2024)
    i25 = pd.read_csv(DADOS / "inscricoes_2025.csv", sep=";").assign(edicao=2025)
    with open(DADOS / "api_resultados.json", encoding="utf-8") as f:
        resultados = pd.json_normalize(json.load(f))
    return atletas, edicoes, i24, i25, resultados


def titulo(texto):
    print(f"\n== {texto}")


def contar(tabela, condicao):
    return int(condicao(tabela).sum())


def main():
    atletas, edicoes, i24, i25, resultados = ler()

    titulo("1. Linhas e chaves de cada arquivo")
    arquivos = [("atletas.csv", atletas, "id_atleta"),
                ("inscricoes_2024.csv", i24, "id_inscricao"),
                ("inscricoes_2025.csv", i25, "id_inscricao"),
                ("api_resultados.json", resultados, "id_inscricao")]
    for nome, tabela, chave in arquivos:
        diferentes = tabela[chave].nunique()
        print(f"{nome:<20} linhas={len(tabela):>4}  {chave} diferentes={diferentes:>4}")

    titulo("2. As duas edições")
    colunas = ["edicao", "natacao_km", "ciclismo_km", "corrida_km", "temperatura_max_c"]
    print(edicoes[colunas].to_string(index=False))

    titulo("3. Inscrições: linhas repetidas e atletas por edição")
    inscricoes = pd.concat([i24, i25])
    print("linhas repetidas idênticas:", inscricoes.duplicated().sum())
    inscricoes = inscricoes.drop_duplicates()
    por_edicao = inscricoes.groupby("edicao").agg(inscricoes=("id_inscricao", "nunique"),
                                                  atletas=("id_atleta", "nunique"))
    print(por_edicao.to_string())
    duas = inscricoes[inscricoes["id_atleta"].duplicated(keep=False)]
    categorias = duas.pivot(index="id_atleta", columns="edicao", values="categoria")
    mudaram = int((categorias[2024] != categorias[2025]).sum())
    print("atletas nas duas edições:", len(categorias), "| mudaram de categoria:", mudaram)
    print("número de peito 102:")
    peito = inscricoes[inscricoes["numero_peito"] == 102]
    print(peito[["edicao", "id_inscricao", "id_atleta", "categoria"]].to_string(index=False))

    titulo("4. Resultados da API: repetidos por edição")
    itens = resultados.groupby("edicao").agg(itens=("id_inscricao", "size"),
                                             inscricoes=("id_inscricao", "nunique"))
    print(itens.to_string())

    titulo("5. Status por edição, juntando inscrições e resultados")
    unicos = resultados.drop_duplicates("id_inscricao")
    juntos = inscricoes.merge(unicos[["id_inscricao", "status"]], on="id_inscricao", how="left")
    juntos["status"] = juntos["status"].fillna("sem resultado")
    tabela = pd.crosstab(juntos["edicao"], juntos["status"], margins=True, margins_name="total")
    print(tabela.to_string())

    titulo("6. Parciais vazias de quem concluiu")
    concluiu = unicos[unicos["status"] == "concluiu"]
    vazias = concluiu.groupby("edicao")[PARCIAIS].agg(lambda s: s.isna().sum())
    vazias.columns = ETAPAS
    print(vazias.to_string())
    print("concluiu sem tempo oficial:", concluiu["tempo_oficial"].isna().sum())
    duracoes = concluiu[PARCIAIS].apply(pd.to_timedelta)
    completas = duracoes.notna().all(axis=1)
    soma = duracoes[completas].sum(axis=1)
    oficial = pd.to_timedelta(concluiu.loc[completas, "tempo_oficial"])
    print(f"concluiu com as cinco parciais: {int(completas.sum())}"
          f" | soma igual ao tempo oficial: {int((soma == oficial).sum())}")
    dsq = unicos[unicos["status"] == "DSQ"]
    dns = unicos[unicos["status"] == "DNS"]
    dnf = unicos[unicos["status"] == "DNF"]
    print(f"DSQ: {len(dsq)}"
          f" | com as cinco parciais: {contar(dsq, lambda t: t[PARCIAIS].notna().all(axis=1))}"
          f" | com tempo oficial: {contar(dsq, lambda t: t['tempo_oficial'].notna())}")
    print(f"DNS com alguma parcial: {contar(dns, lambda t: t[PARCIAIS].notna().any(axis=1))}"
          f" | DNF com tempo oficial: {contar(dnf, lambda t: t['tempo_oficial'].notna())}")

    titulo("7. Uma inscrição com parcial vazia")
    exemplo = unicos[unicos["id_inscricao"] == "2024-0001"].iloc[0]
    for e in ETAPAS:
        print(f"{e:<9} {exemplo[f'parciais.{e}']}")
    print(f"{'oficial':<9} {exemplo['tempo_oficial']}")
    tem = pd.to_timedelta(pd.Series([exemplo[p] for p in PARCIAIS])).sum()
    print(f"{'soma':<9} {str(tem).split(' days ')[-1]}  (só as parciais que existem)")

    titulo("8. DNF com dois denominadores")
    marcado = juntos.assign(dnf=juntos["status"] == "DNF", largou=juntos["status"].isin(LARGOU))
    taxa = marcado.groupby("edicao").agg(dnf=("dnf", "sum"), inscricoes=("id_inscricao", "size"),
                                         largaram=("largou", "sum"))
    taxa["dnf_por_inscricao_%"] = (100 * taxa["dnf"] / taxa["inscricoes"]).round(1)
    taxa["dnf_por_largada_%"] = (100 * taxa["dnf"] / taxa["largaram"]).round(1)
    print(taxa.to_string())

    titulo("9. As cinco maiores taxas de DNF de 2025 por categoria, de quem largou")
    larg25 = marcado[(marcado["edicao"] == 2025) & marcado["largou"]]
    cat = larg25.groupby("categoria").agg(dnf=("dnf", "sum"), largaram=("dnf", "size"))
    cat["dnf_%"] = (100 * cat["dnf"] / cat["largaram"]).round(1)
    print(cat.sort_values("dnf_%", ascending=False, kind="stable").head(5).to_string())


if __name__ == "__main__":
    main()
