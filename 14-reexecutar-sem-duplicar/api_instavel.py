"""A API do kit com outras falhas, para ver o que a coleta faz quando a falha não passa logo.

    python3 api_instavel.py --cenario fora
    python3 api_instavel.py --cenario espera-longa
    python3 api_instavel.py --cenario madrugada
    python3 api_instavel.py --cenario fora --pasta revisada

Usa o servidor.py da pasta api/ do kit, com os mesmos dados, a mesma porta (8765) e o mesmo
token. Com --pasta, serve os api_*.json de outra pasta, como o servidor.py.
Pare a API normal antes de subir esta. Cada cenário muda só as chamadas com o token certo:

  fora          a página 3 responde 503 em toda chamada
  espera-longa  a primeira chamada da página 2 responde 429 com Retry-After: 3600 (uma hora)
  madrugada     a primeira chamada da página 2 responde 429 com Retry-After: 3;
                as duas primeiras da página 3 respondem 503

As chamadas são contadas por página desde que a API subiu. Para ver de novo, pare e suba outra vez.
"""
import argparse
import sys
import threading
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "api"))
import servidor  # noqa: E402  (o servidor.py da pasta api/ do kit)

# Para cada cenário: página -> o que acontece em cada chamada (1ª, 2ª, ...). Depois da lista, a página responde normal.
SEMPRE = None
CENARIOS = {
    "fora": {3: SEMPRE},
    "espera-longa": {2: [(429, "3600")]},
    "madrugada": {2: [(429, "3")], 3: [(503, None), (503, None)]},
}
ERROS = {429: "muitas_chamadas", 503: "servico_indisponivel"}


def criar(cenario, porta=8765, pasta=servidor.PADRAO):
    api, colecoes = servidor.criar_servidor(pasta, porta)
    plano = CENARIOS[cenario]
    chamadas = {}
    trava = threading.Lock()
    Normal = api.RequestHandlerClass

    class Instavel(Normal):
        def do_GET(self):
            if self.headers.get("Authorization") == f"Bearer {servidor.TOKEN}":
                q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(self.path).query))
                pagina = int(q.get("pagina", 1)) if q.get("pagina", "1").isdigit() else None
                if pagina in plano:
                    with trava:
                        chamadas[pagina] = vez = chamadas.get(pagina, 0) + 1
                    regras = plano[pagina]
                    regra = (503, None) if regras is SEMPRE else (regras[vez - 1] if vez <= len(regras) else None)
                    if regra:
                        codigo, depois = regra
                        extras = {"Retry-After": depois} if depois else None
                        return self.responder(codigo, {"erro": ERROS[codigo]}, extras)
            return super().do_GET()

    api.RequestHandlerClass = Instavel
    return api


def main():
    ap = argparse.ArgumentParser(description="API do kit com falhas que não passam logo")
    ap.add_argument("--cenario", required=True, choices=sorted(CENARIOS))
    ap.add_argument("--porta", type=int, default=8765)
    ap.add_argument("--pasta", default=str(servidor.PADRAO), help="pasta com os api_*.json (padrão: os dados do triatlo)")
    a = ap.parse_args()
    api = criar(a.cenario, a.porta, a.pasta)
    print(f"API instável ({a.cenario}) em http://127.0.0.1:{api.server_address[1]}  token: {servidor.TOKEN}")
    print("Ctrl+C para parar.")
    try:
        api.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
