"""A análise do projeto do triatlo: etapas, desistência e categorias, com os limites de cada comparação.

Lê a base da aula 42, «Triatlo: integração e qualidade» (uma linha por inscrição, tempos em segundos),
e a ficha das edições (distâncias, temperatura e observação). Segue o contrato da aula 41:
- tempo de etapa só de quem concluiu, sem trocar vazio por zero;
- desistência é DNF, e o denominador é quem largou (concluiu, DNF ou DSQ);
- etapa com distância diferente entre as edições não ganha diferença de tempo;
- categoria com menos de MINIMO pessoas que largaram fica marcada e fora do ranking.

Uso, de dentro da pasta da aula:
    python3 analise.py                      # mostra as contas e grava relatorio/
    python3 analise.py --base OUTRA.csv     # usa outra base, por exemplo a saida/ da aula 42

Para usar no Python:
    from analise import ler_base, ler_edicoes, etapas, desistencia, taxa_por_categoria, gerar
"""
import argparse
import hashlib
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
BASE = AQUI / "dados_da_aula" / "base_triatlo.csv"
DADOS = AQUI.parent / "dados" / "triatlo"
ETAPAS = ["natacao", "t1", "ciclismo", "t2", "corrida"]
NOME = {"natacao": "natação", "t1": "T1", "ciclismo": "ciclismo", "t2": "T2", "corrida": "corrida"}
DISTANCIA = {"natacao": "natacao_km", "ciclismo": "ciclismo_km", "corrida": "corrida_km"}
LARGARAM = ["concluiu", "DNF", "DSQ"]
MINIMO = 20  # com 20 pessoas, uma desistência a mais muda a taxa em 5 pontos


def virgula(x, casas=1):
    """12.34 vira '12,3'. Os números do relatório saem com vírgula."""
    return f"{x:.{casas}f}".replace(".", ",")


def km(x):
    """180.0 vira '180', 42.2 vira '42,2'."""
    return virgula(x, 0) if float(x).is_integer() else virgula(x)


def minutos(s):
    return s / 60


# ---------------------------------------------------------------- ler

def ler_base(caminho=BASE):
    """A base da aula 42, com os tempos no tipo Int64 (vazio continua vazio)."""
    tempos = {f"{e}_s": "Int64" for e in ETAPAS + ["oficial"]}
    tipos = dict(tempos, id_inscricao=str, categoria=str, sexo=str, status=str, equipe=str, motivo=str)
    return pd.read_csv(caminho, dtype=tipos, keep_default_na=False, na_values=[""])


def ler_edicoes(pasta=DADOS):
    """A ficha das edições, com a edição no índice."""
    return pd.read_csv(Path(pasta) / "edicoes.csv").set_index("edicao").sort_index()


def as_duas(edicoes):
    """As duas edições comparadas: a anterior e a mais recente."""
    anos = list(edicoes.index)
    if len(anos) < 2:
        raise ValueError("a comparação precisa de duas edições na ficha")
    return anos[-2], anos[-1]


# ---------------------------------------------------------------- distâncias e condições

def comparabilidade(edicoes):
    """Para cada etapa: ('comparável' | 'não comparável' | 'sem distância', motivo)."""
    a, b = as_duas(edicoes)
    saida = {}
    for e in ETAPAS:
        if e not in DISTANCIA:
            saida[e] = ("sem distância", "a ficha não tem distância de transição")
            continue
        da, db = edicoes.at[a, DISTANCIA[e]], edicoes.at[b, DISTANCIA[e]]
        if da == db:
            saida[e] = ("comparável", f"{km(da)} km nas duas")
        else:
            saida[e] = ("não comparável", f"{km(da)} km em {a}, {km(db)} km em {b}")
    return saida


def condicoes(edicoes):
    """O que mudou entre as duas edições além da distância. Lista vazia: mesmas condições na ficha."""
    a, b = as_duas(edicoes)
    mudou = []
    ta, tb = edicoes.at[a, "temperatura_max_c"], edicoes.at[b, "temperatura_max_c"]
    if ta != tb:
        mudou.append(f"máxima de {ta} °C em {a} e {tb} °C em {b}")
    oa, ob = edicoes.at[a, "observacao"], edicoes.at[b, "observacao"]
    if oa != ob:
        mudou.append(f"ficha de {b}: {ob}")
    return mudou


# ---------------------------------------------------------------- etapas

def etapas(base, edicoes):
    """Mediana de cada etapa de quem concluiu, por edição, com quantos tempos entram.

    Parcial vazia sai da mediana e é contada em 'vazias'. A diferença (mais recente menos anterior,
    em minutos) só existe para etapa comparável ou transição; na etapa não comparável fica vazia.
    """
    a, b = as_duas(edicoes)
    conc = base[base["status"] == "concluiu"]
    comp = comparabilidade(edicoes)
    linhas = []
    for e in ETAPAS:
        linha = {"etapa": NOME[e], "situacao": comp[e][0], "motivo": comp[e][1]}
        for ano in (a, b):
            t = conc.loc[conc["edicao"] == ano, f"{e}_s"]
            linha[f"mediana_{ano}"] = minutos(t.median()) if t.notna().any() else float("nan")
            linha[f"n_{ano}"] = int(t.notna().sum())
            linha[f"vazias_{ano}"] = int(t.isna().sum())
        linha["diferenca"] = (float("nan") if comp[e][0] == "não comparável"
                              else linha[f"mediana_{b}"] - linha[f"mediana_{a}"])
        linhas.append(linha)
    return pd.DataFrame(linhas).set_index("etapa")


def trecho_comparavel(base, edicoes):
    """Mediana da soma das etapas comparáveis (com distância igual), de quem concluiu."""
    a, b = as_duas(edicoes)
    comp = [e for e, (s, _) in comparabilidade(edicoes).items() if s == "comparável"]
    conc = base[base["status"] == "concluiu"]
    soma = conc[[f"{e}_s" for e in comp]].sum(axis=1, min_count=len(comp))
    saida = {"etapas": [NOME[e] for e in comp]}
    for ano in (a, b):
        t = soma[conc["edicao"] == ano]
        saida[ano] = (minutos(t.median()), int(t.notna().sum()))
    return saida


# ---------------------------------------------------------------- desistência

def onde_parou(base):
    """Para cada DNF, a primeira etapa sem tempo: é onde a pessoa parou."""
    dnf = base[base["status"] == "DNF"]
    vazia = dnf[[f"{e}_s" for e in ETAPAS]].isna()
    return vazia.idxmax(axis=1).str[:-2].map(NOME).rename("parou")


def desistencia(base):
    """DNF de quem largou, por edição, e em que etapa as pessoas pararam."""
    larg = base[base["status"].isin(LARGARAM)]
    tab = larg.groupby("edicao").agg(dnf=("status", lambda s: int((s == "DNF").sum())), largaram=("status", "size"))
    tab["pct"] = 100 * tab["dnf"] / tab["largaram"]
    parou = pd.crosstab(base.loc[base["status"] == "DNF", "edicao"], onde_parou(base))
    for e in ETAPAS:
        if NOME[e] not in parou.columns:
            parou[NOME[e]] = 0
    return tab.join(parou[[NOME[e] for e in ETAPAS]]).fillna(0)


# ---------------------------------------------------------------- categorias

def taxa_por_categoria(base, minimo=MINIMO):
    """DNF de quem largou por edição e categoria. 'pequeno' marca o grupo com menos de minimo pessoas."""
    larg = base[base["status"].isin(LARGARAM)]
    tab = (larg.groupby(["edicao", "categoria"])
           .agg(dnf=("status", lambda s: int((s == "DNF").sum())), largaram=("status", "size")))
    tab["pct"] = 100 * tab["dnf"] / tab["largaram"]
    tab["pequeno"] = tab["largaram"] < minimo
    return tab


def ranking(taxas, edicao, n=5):
    """As n maiores taxas de DNF da edição, só entre os grupos que não são pequenos."""
    t = taxas.loc[edicao]
    t = t[~t["pequeno"]]
    return t.sort_values(["pct", "largaram"], ascending=[False, False]).head(n)


def etapa_por_categoria(base, edicoes, etapa="corrida"):
    """Mediana de uma etapa por categoria, de quem concluiu, nas duas edições, com n e diferença."""
    a, b = as_duas(edicoes)
    conc = base[base["status"] == "concluiu"]
    g = conc.groupby(["categoria", "edicao"])[f"{etapa}_s"].agg(["median", "count"]).unstack("edicao")
    tab = pd.DataFrame({f"mediana_{a}": minutos(g[("median", a)]), f"n_{a}": g[("count", a)],
                        f"mediana_{b}": minutos(g[("median", b)]), f"n_{b}": g[("count", b)]})
    tab["diferenca"] = tab[f"mediana_{b}"] - tab[f"mediana_{a}"]
    return tab


def mesmas_pessoas(base):
    """Quantos atletas estão nas duas edições, e quantos deles mudaram de categoria (pelo id_atleta)."""
    anos = sorted(base["edicao"].unique())[-2:]
    cat = base[base["edicao"].isin(anos)].pivot_table(index="id_atleta", columns="edicao", values="categoria",
                                                         aggfunc="first")
    duas = cat.dropna()
    return {"nas_duas": len(duas), "mudaram": int((duas[anos[0]] != duas[anos[1]]).sum())}


# ---------------------------------------------------------------- limites

def limitacoes(base, edicoes, taxas, minimo=MINIMO):
    """Os limites do relatório, escritos a partir dos dados. Cada item diz o que o número não mostra."""
    a, b = as_duas(edicoes)
    itens = []
    for e, (sit, motivo) in comparabilidade(edicoes).items():
        if sit == "não comparável":
            itens.append(f"A {NOME[e]} não é comparada: {motivo}. Nem o ritmo por 100 m resolve, porque "
                         f"a condição que mudou a distância também mudou a água.")
    mudou = condicoes(edicoes)
    if mudou:
        itens.append("As condições mudaram: " + "; ".join(mudou) + ". As diferenças de tempo e de desistência "
                     "comparam as edições como elas foram, sem separar o efeito de cada mudança.")
    tab = etapas(base, edicoes)
    for nome, linha in tab.iterrows():
        if linha[f"vazias_{a}"] or linha[f"vazias_{b}"]:
            itens.append(f"A mediana da {nome} usa {linha[f'n_{a}']} tempos em {a} e {linha[f'n_{b}']} em {b}: "
                         f"{linha[f'vazias_{a}']} e {linha[f'vazias_{b}']} pessoas que concluíram estão sem esse tempo.")
    pequenos = taxas[taxas["pequeno"]]
    for ano in (a, b):
        p = pequenos.loc[ano] if ano in pequenos.index.get_level_values(0) else pequenos.iloc[0:0]
        itens.append(f"Em {ano}, {len(p)} de {len(taxas.loc[ano])} categorias têm menos de {minimo} pessoas que "
                     f"largaram. Elas aparecem com o \"x de y\" e ficam fora do ranking.")
    pessoas = mesmas_pessoas(base)
    itens.append(f"As categorias não têm as mesmas pessoas nos dois anos: {pessoas['nas_duas']} atletas correram as "
                 f"duas edições, e {pessoas['mudaram']} deles mudaram de categoria.")
    itens.append("Os dados mostram o que aconteceu na prova. Eles não mostram por que aconteceu: treino, calor, "
                 "equipamento e quem decidiu se inscrever ficam fora da base.")
    return itens


# ---------------------------------------------------------------- figuras

def figura_etapas(tab, edicoes, caminho):
    """Uma barra por edição em cada etapa, cada etapa com o próprio eixo, começando no zero."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    a, b = as_duas(edicoes)
    fig, eixos = plt.subplots(1, len(tab), figsize=(11, 3.6))
    for ax, (nome, linha) in zip(eixos, tab.iterrows()):
        cores = ["#9aa5a0", "#52645C"] if linha["situacao"] != "não comparável" else ["#d0d0d0", "#b0b0b0"]
        barras = ax.bar([str(a), str(b)], [linha[f"mediana_{a}"], linha[f"mediana_{b}"]], color=cores,
                        hatch="//" if linha["situacao"] == "não comparável" else None)
        for barra, ano in zip(barras, (a, b)):
            ax.annotate(f"{virgula(linha[f'mediana_{ano}'])}\nn={linha[f'n_{ano}']}",
                        (barra.get_x() + barra.get_width() / 2, barra.get_height()),
                        ha="center", va="bottom", fontsize=8)
        ax.set_ylim(0, max(linha[f"mediana_{a}"], linha[f"mediana_{b}"]) * 1.35)
        ax.set_title(nome, fontsize=10)
        ax.set_xlabel(linha["motivo"] if linha["situacao"] != "sem distância" else "transição", fontsize=7)
        ax.tick_params(labelsize=8)
    eixos[0].set_ylabel("mediana de quem concluiu (min)", fontsize=8)
    fig.suptitle("Tempo por etapa: a natação mudou de distância e não entra na comparação", fontsize=11)
    fig.tight_layout()
    fig.savefig(caminho, dpi=110, metadata={"Software": None})
    plt.close(fig)


def figura_categorias(taxas, edicoes, caminho):
    """DNF de quem largou por categoria, um painel por edição, com o 'x de y' ao lado de cada barra."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    a, b = as_duas(edicoes)
    cats = sorted(set(taxas.loc[a].index) | set(taxas.loc[b].index))
    fig, eixos = plt.subplots(1, 2, figsize=(10, 6.4), sharey=True)
    for ax, ano in zip(eixos, (a, b)):
        t = taxas.loc[ano].reindex(cats)
        cores = ["#c9cfcc" if p else "#52645C" for p in t["pequeno"].fillna(True)]
        ax.barh(cats, t["pct"].fillna(0), color=cores)
        for i, (c, linha) in enumerate(t.iterrows()):
            if pd.notna(linha["largaram"]):
                ax.annotate(f"{int(linha['dnf'])} de {int(linha['largaram'])}", (linha["pct"], i),
                            xytext=(3, 0), textcoords="offset points", va="center", fontsize=7)
        ax.set_xlim(0, 40)
        ax.set_title(str(ano), fontsize=10)
        ax.set_xlabel("DNF de quem largou (%)", fontsize=8)
        ax.tick_params(labelsize=8)
    eixos[0].invert_yaxis()  # o eixo é compartilhado: inverter uma vez só
    fig.suptitle(f"Desistência por categoria. Em cinza, grupos com menos de {MINIMO} pessoas que largaram",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(caminho, dpi=110, metadata={"Software": None})
    plt.close(fig)


# ---------------------------------------------------------------- relatório

def sha256(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def texto_relatorio(base, edicoes, origem):
    a, b = as_duas(edicoes)
    tab = etapas(base, edicoes)
    trecho = trecho_comparavel(base, edicoes)
    des = desistencia(base)
    taxas = taxa_por_categoria(base)
    cor = etapa_por_categoria(base, edicoes)
    ambos = cor.dropna()
    lentas = int((ambos["diferenca"] > 0).sum())

    l = [f"# Balanço das edições {a} e {b}: etapas, desistência e categorias", ""]
    l += ["## O que dá para dizer", ""]
    l.append(f"- Nas etapas com a mesma distância ({' e '.join(trecho['etapas'])}), a mediana de quem concluiu "
             f"foi de {virgula(trecho[a][0])} min em {a} ({trecho[a][1]} pessoas) e {virgula(trecho[b][0])} min "
             f"em {b} ({trecho[b][1]} pessoas): {virgula(trecho[b][0] - trecho[a][0])} min a mais em {b}.")
    cor_tab = tab.loc["corrida"]
    l.append(f"- Quase toda essa diferença está na corrida: {virgula(cor_tab['diferenca'])} min a mais pela mediana. "
             f"Na corrida, {lentas} de {len(ambos)} categorias foram mais lentas em {b}.")
    l.append(f"- A desistência de quem largou foi de {des.at[a, 'dnf']} em {des.at[a, 'largaram']} em {a} "
             f"({virgula(des.at[a, 'pct'])}%) e de {des.at[b, 'dnf']} em {des.at[b, 'largaram']} em {b} "
             f"({virgula(des.at[b, 'pct'])}%). Pararam na corrida {int(des.at[a, 'corrida'])} em {a} e "
             f"{int(des.at[b, 'corrida'])} em {b}; no ciclismo, {int(des.at[a, 'ciclismo'])} e "
             f"{int(des.at[b, 'ciclismo'])}.")
    top = {ano: ranking(taxas, ano) for ano in (a, b)}
    comum = sorted(set(top[a].index) & set(top[b].index))
    if len(top[b]):
        l.append(f"- Entre as categorias com pelo menos {MINIMO} pessoas que largaram, a maior taxa de {b} é "
                 f"{top[b].index[0]}: {top[b].iloc[0]['dnf']} de {top[b].iloc[0]['largaram']} "
                 f"({virgula(top[b].iloc[0]['pct'])}%). Das {len(top[a])} maiores de {a}, {len(comum)} estão entre "
                 f"as {len(top[b])} maiores de {b}.")
    else:
        l.append(f"- Nenhuma categoria de {b} tem {MINIMO} pessoas que largaram. O relatório não faz ranking.")
    l += ["", "## Tempo por etapa, de quem concluiu", ""]
    l.append(f"| Etapa | Situação | {a} (min) | {b} (min) | Diferença (min) |")
    l.append("|---|---|---|---|---|")
    for nome, linha in tab.iterrows():
        dif = "" if pd.isna(linha["diferenca"]) else virgula(linha["diferenca"])
        l.append(f"| {nome} | {linha['situacao']}: {linha['motivo']} | {virgula(linha[f'mediana_{a}'])} "
                 f"(n={linha[f'n_{a}']}) | {virgula(linha[f'mediana_{b}'])} (n={linha[f'n_{b}']}) | {dif} |")
    l += ["", "![Tempo por etapa](figuras/etapas.png)", ""]
    l += ["## Desistência por categoria, de quem largou", ""]
    l.append(f"| Categoria | {a} | {b} |")
    l.append("|---|---|---|")
    cats = sorted(set(taxas.loc[a].index) | set(taxas.loc[b].index))
    for c in cats:
        cel = []
        for ano in (a, b):
            if c in taxas.loc[ano].index:
                t = taxas.loc[(ano, c)]
                marca = " (grupo pequeno)" if t["pequeno"] else ""
                cel.append(f"{t['dnf']} de {t['largaram']}, {virgula(t['pct'])}%{marca}")
            else:
                cel.append("ninguém largou")
        l.append(f"| {c} | {cel[0]} | {cel[1]} |")
    l += ["", "![Desistência por categoria](figuras/categorias.png)", ""]
    l += ["## Limitações", ""]
    l += [f"- {item}" for item in limitacoes(base, edicoes, taxas)]
    l += ["", "## De onde vêm os números", ""]
    l.append(f"- Base: `{origem['nome']}`, {len(base)} inscrições, sha256 `{origem['sha256'][:12]}`.")
    l.append("- Ficha das edições: `edicoes.csv`, com as distâncias, a temperatura máxima e a observação.")
    l.append("- Tempo de etapa: mediana de quem concluiu, sem os tempos vazios. Desistência: DNF dividido por quem "
             "largou (concluiu, DNF ou DSQ). Diferença: a edição mais recente menos a anterior.")
    l.append("- Para gerar de novo: `python3 analise.py`.")
    return "\n".join(l) + "\n"


def gerar(base, edicoes, saida, origem):
    """Grava relatorio.md e as duas figuras na pasta saida. Retorna o sha256 de cada arquivo gravado."""
    saida = Path(saida)
    (saida / "figuras").mkdir(parents=True, exist_ok=True)
    figura_etapas(etapas(base, edicoes), edicoes, saida / "figuras" / "etapas.png")
    figura_categorias(taxa_por_categoria(base), edicoes, saida / "figuras" / "categorias.png")
    (saida / "relatorio.md").write_text(texto_relatorio(base, edicoes, origem), encoding="utf-8")
    return {p.relative_to(saida).as_posix(): sha256(p)[:12] for p in sorted(saida.rglob("*")) if p.is_file()}


# ---------------------------------------------------------------- tela

def mostrar(base, edicoes):
    a, b = as_duas(edicoes)
    pd.set_option("display.width", 120)
    print("== 1. Distâncias e condições")
    for e, (sit, motivo) in comparabilidade(edicoes).items():
        print(f"{NOME[e]:9} {sit}: {motivo}")
    for m in condicoes(edicoes):
        print(f"mudou: {m}")

    print("\n== 2. Tempo por etapa, de quem concluiu (mediana em minutos)")
    tab = etapas(base, edicoes)
    cols = [f"mediana_{a}", f"n_{a}", f"mediana_{b}", f"n_{b}", "diferenca"]
    print(tab[cols].round(1).to_string())
    t = trecho_comparavel(base, edicoes)
    print(f"{' + '.join(t['etapas'])}: {a} {t[a][0]:.1f} (n={t[a][1]}) | {b} {t[b][0]:.1f} (n={t[b][1]}) | "
          f"diferença {t[b][0] - t[a][0]:.1f}")

    print("\n== 3. Desistência de quem largou, e onde parou")
    des = desistencia(base)
    print(des.round(1).to_string())

    print(f"\n== 4. Categorias: as cinco maiores taxas de DNF, só grupos com {MINIMO} ou mais que largaram")
    taxas = taxa_por_categoria(base)
    for ano in (a, b):
        r = ranking(taxas, ano)
        print(f"{ano}: " + " | ".join(f"{c} {x['dnf']} de {x['largaram']}" for c, x in r.iterrows()))
    for ano in (a, b):
        print(f"{ano}: {int(taxas.loc[ano]['pequeno'].sum())} de {len(taxas.loc[ano])} categorias com menos de "
              f"{MINIMO} que largaram")
    cor = etapa_por_categoria(base, edicoes).dropna()
    print(f"corrida mais lenta em {b}: {int((cor['diferenca'] > 0).sum())} de {len(cor)} categorias; "
          f"diferença de {cor['diferenca'].min():.1f} a {cor['diferenca'].max():.1f} min")
    p = mesmas_pessoas(base)
    print(f"atletas nas duas edições: {p['nas_duas']} | mudaram de categoria: {p['mudaram']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default=str(BASE), help="a base da aula 42 (padrão: dados_da_aula/base_triatlo.csv)")
    ap.add_argument("--saida", default="relatorio", help="pasta do relatório (padrão: relatorio)")
    args = ap.parse_args(argv)
    try:
        base, edicoes = ler_base(args.base), ler_edicoes()
    except FileNotFoundError as erro:
        print(f"ERROR não achei {erro.filename}. Rode de dentro da pasta da aula, no kit do curso.", file=sys.stderr)
        return 2
    mostrar(base, edicoes)
    hashes = gerar(base, edicoes, args.saida, {"nome": Path(args.base).name, "sha256": sha256(args.base)})
    print(f"\ngravei {args.saida}/: " + " | ".join(f"{k} {v}" for k, v in hashes.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
