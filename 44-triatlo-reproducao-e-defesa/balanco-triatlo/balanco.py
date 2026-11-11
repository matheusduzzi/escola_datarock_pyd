"""O balanço do triatlo de ponta a ponta, num comando só.

De dentro da pasta do projeto:
    python3 balanco.py                    # sobe a API local, monta a base, analisa e grava saida/
    python3 balanco.py --saida outra      # grava em outra pasta
    python3 balanco.py --endereco URL     # usa outra API; o token vem de API_TRIATLO_TOKEN

Passos:
  1 a 5. a base, como no rodar.py: arquivos, coleta pela API, cópias, junção e regras do contrato;
  6. grava saida/base_triatlo.csv e saida/conferencia.txt, só se a base passou;
  7. a análise e o relatório, em saida/relatorio/, a partir da base gravada.

Sem --endereco, o programa sobe a API local de api/servidor.py numa porta livre, com as falhas
preparadas ligadas, e desliga no fim. O token dela é o que o próprio servidor define. Uma API de
verdade não tem token no código: com --endereco, ele vem da variável de ambiente.

Código de saída:
  0  base e relatório gravados
  1  a coleta não bateu ou a base quebrou uma regra do contrato; nada foi gravado
  2  com --endereco, falta a variável API_TRIATLO_TOKEN; nenhuma chamada foi feita
  3  a API falhou e não voltou dentro das tentativas; nada foi gravado
"""
import argparse
import os
import sys
import threading
from pathlib import Path

import analise
import coletar
import integrar
import rodar
from api import servidor

ERROS_DA_BASE = (coletar.ColetaIncompleta, integrar.InscricaoConflitante, integrar.ResultadoConflitante,
                 integrar.ResultadoSemInscricao, integrar.AtletaSemCadastro, integrar.RegraQuebrada)


def api_local():
    """Sobe a API do projeto numa porta livre, numa thread. Retorna o servidor e o endereço."""
    srv, _ = servidor.criar_servidor(servidor.PADRAO, 0, falhas=True)
    srv.RequestHandlerClass.log_message = lambda *args: None
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--saida", default="saida", help="pasta onde tudo é gravado (padrão saida)")
    ap.add_argument("--endereco", help="outra API, no lugar da local do projeto")
    ap.add_argument("--espera", type=float, default=10, help="tempo limite de cada chamada, em segundos")
    a = ap.parse_args(argv)

    if a.endereco:
        token = os.environ.get("API_TRIATLO_TOKEN")
        if not token:
            print("ERROR falta a variável de ambiente API_TRIATLO_TOKEN para a API de --endereco. "
                  "Nenhuma chamada foi feita.", file=sys.stderr)
            return 2
        srv, endereco = None, a.endereco
    else:
        srv, endereco = api_local()
        token = servidor.TOKEN

    tela = rodar.Tela()
    tela("API local do projeto, com as falhas preparadas" if srv else "API de --endereco")
    try:
        base = rodar.montar(endereco, token, a.espera, tela)
    except ERROS_DA_BASE as erro:
        print(f"ERROR {erro}. Nada foi gravado em {a.saida}/.", file=sys.stderr)
        return 1
    except coletar.Desisti as erro:
        print(f"ERROR desisti: {erro}. Nada foi gravado em {a.saida}/.", file=sys.stderr)
        return 3
    finally:
        if srv:
            srv.shutdown()

    pasta = Path(a.saida)
    pasta.mkdir(exist_ok=True)
    caminho = pasta / "base_triatlo.csv"
    rodar.gravar_csv(base, caminho)
    tela(f"\n== 6. Base gravada\n{caminho}: {len(base)} linhas, {len(base.columns)} colunas")
    (pasta / "conferencia.txt").write_text("\n".join(tela.linhas) + "\n", encoding="utf-8")

    print("\n== 7. Análise")
    gravada, edicoes = analise.ler_base(caminho), analise.ler_edicoes()
    analise.mostrar(gravada, edicoes)
    origem = {"nome": caminho.name, "sha256": analise.sha256(caminho), "comando": "python3 balanco.py"}
    hashes = analise.gerar(gravada, edicoes, pasta / "relatorio", origem)
    print(f"\ngravei {pasta}/: base_triatlo.csv {analise.sha256(caminho)[:12]} | conferencia.txt")
    print(f"gravei {pasta}/relatorio/: " + " | ".join(f"{k} {v}" for k, v in hashes.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
