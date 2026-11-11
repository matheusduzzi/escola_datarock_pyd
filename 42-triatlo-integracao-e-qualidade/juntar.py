"""Junta os resultados recuperados à base e mostra o que entrou e o que ficou pendente.

Rode depois do rodar.py, de dentro da pasta da aula:

    python3 juntar.py

Lê saida/base_triatlo.csv e dados_da_aula/recuperados.json, chama a sua juntar_recuperados
(recuperados.py) e passa a base nova nas regras do contrato. Só grava
saida/base_com_recuperados.csv se a base nova passou. Sai com 1 se não passou.
"""
import sys
from pathlib import Path

import pandas as pd

import integrar
from recuperados import juntar_recuperados

AQUI = Path(__file__).resolve().parent


def main():
    base = integrar.ler_base(AQUI / "saida" / "base_triatlo.csv")
    recuperados = integrar.resultados_do_arquivo(AQUI / "dados_da_aula" / "recuperados.json")
    antes = base.copy()
    nova, pendencias = juntar_recuperados(base, recuperados)

    print(f"recuperados.json: {len(recuperados)} itens, {len({r['id_inscricao'] for r in recuperados})} inscrições")
    preenchidas = nova.loc[nova["fonte_resultado"] == "recuperados", "id_inscricao"]
    print(f"preenchidas: {len(preenchidas)} ({', '.join(preenchidas)})")
    sem_mudar = sorted({r["id_inscricao"] for r in recuperados} - set(preenchidas) - set(pendencias))
    print(f"já estavam iguais na base: {len(sem_mudar)} ({', '.join(sem_mudar)})")
    print(f"pendências: {len(pendencias)}")
    for id_inscricao, motivo in sorted(pendencias.items()):
        print(f"  {id_inscricao}: {motivo}")
    print("a base que entrou ficou igual:", base.equals(antes))
    tabela = pd.crosstab(nova["edicao"], nova["status"], margins=True, margins_name="total")
    print(tabela.reindex(columns=integrar.STATUS + ["total"], fill_value=0).to_string())
    problemas = integrar.conferir(nova)
    print(f"{integrar.QUANTAS_REGRAS} regras, {len(problemas)} problema(s)")
    for p in problemas:
        print(f"  {p}")
    if problemas or len(nova) != len(base) or list(nova.columns) != integrar.COLUNAS:
        print("ERROR a base nova não passou. Nada foi gravado.", file=sys.stderr)
        return 1
    nova.to_csv(AQUI / "saida" / "base_com_recuperados.csv", index=False)
    print("gravei saida/base_com_recuperados.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
