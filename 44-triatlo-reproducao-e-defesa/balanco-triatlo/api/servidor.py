"""API local do kit de Python para dados. Só biblioteca padrão, roda no seu computador.

Serve cada arquivo api_<nome>.json de uma pasta como a rota /v1/<nome>, com paginação,
filtro por campo, token fixo e, se você pedir, falhas preparadas.

    python3 servidor.py                          # resultados do triatlo em http://127.0.0.1:8765
    python3 servidor.py --falhas                 # mesma API, com as falhas preparadas ligadas
    python3 servidor.py --pasta ../minha_pasta   # serve os api_*.json de outra pasta
    python3 servidor.py --teste                  # sobe, faz uma chamada e mostra o resultado

Chamada: GET /v1/resultados?edicao=2025&pagina=1&por_pagina=50
Cabeçalho obrigatório: Authorization: Bearer kit-local

Com --falhas, cada caso acontece só na primeira chamada daquela página:
  página 2: 429 com Retry-After: 1
  página 3: 503
  página 5: a resposta demora 5 segundos
"""
import argparse
import json
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

TOKEN = 'kit-local'
PADRAO = Path(__file__).resolve().parent.parent / 'dados' / 'triatlo'
POR_PAGINA, MAXIMO = 50, 100


def carregar(pasta):
    return {p.stem[4:]: json.loads(p.read_text(encoding='utf-8')) for p in sorted(Path(pasta).glob('api_*.json'))}


def criar_servidor(pasta, porta, falhas=False):
    colecoes = carregar(pasta)
    vistas = {}
    trava = threading.Lock()

    class Rotas(BaseHTTPRequestHandler):
        def responder(self, codigo, corpo, extras=None):
            dados = json.dumps(corpo, ensure_ascii=False).encode('utf-8')
            self.send_response(codigo)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(dados)))
            for k, v in (extras or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(dados)

        def do_GET(self):
            url = urllib.parse.urlsplit(self.path)
            partes = url.path.strip('/').split('/')
            if len(partes) != 2 or partes[0] != 'v1' or partes[1] not in colecoes:
                return self.responder(404, {'erro': 'rota_inexistente', 'rotas': [f'/v1/{c}' for c in colecoes]})
            if self.headers.get('Authorization') != f'Bearer {TOKEN}':
                return self.responder(401, {'erro': 'token_ausente_ou_invalido'})
            q = dict(urllib.parse.parse_qsl(url.query))
            try:
                pagina = int(q.pop('pagina', 1))
                por_pagina = int(q.pop('por_pagina', POR_PAGINA))
            except ValueError:
                return self.responder(400, {'erro': 'pagina_e_por_pagina_precisam_ser_inteiros'})
            if pagina < 1 or not 1 <= por_pagina <= MAXIMO:
                return self.responder(400, {'erro': f'pagina >= 1 e por_pagina entre 1 e {MAXIMO}'})
            itens = [i for i in colecoes[partes[1]] if all(str(i.get(k)) == v for k, v in q.items())]
            if falhas:
                chave = (url.path, tuple(sorted(q.items())), pagina)
                with trava:
                    vistas[chave] = vistas.get(chave, 0) + 1
                    primeira = vistas[chave] == 1
                if primeira and pagina == 2:
                    return self.responder(429, {'erro': 'muitas_chamadas'}, {'Retry-After': '1'})
                if primeira and pagina == 3:
                    return self.responder(503, {'erro': 'servico_indisponivel'})
                if primeira and pagina == 5:
                    time.sleep(5)
            total = len(itens)
            inicio = (pagina - 1) * por_pagina
            self.responder(200, {'pagina': pagina, 'por_pagina': por_pagina, 'total': total,
                                 'total_paginas': (total + por_pagina - 1) // por_pagina,
                                 'itens': itens[inicio:inicio + por_pagina]})

        def log_message(self, formato, *args):
            print('  ' + self.address_string() + ' ' + formato % args)

    return ThreadingHTTPServer(('127.0.0.1', porta), Rotas), colecoes


def main():
    ap = argparse.ArgumentParser(description='API local do kit')
    ap.add_argument('--pasta', default=str(PADRAO))
    ap.add_argument('--porta', type=int, default=8765)
    ap.add_argument('--falhas', action='store_true')
    ap.add_argument('--teste', action='store_true', help='sobe numa porta livre, faz uma chamada e sai')
    a = ap.parse_args()
    servidor, colecoes = criar_servidor(a.pasta, 0 if a.teste else a.porta, a.falhas)
    porta = servidor.server_address[1]
    if a.teste:
        servidor.RequestHandlerClass.log_message = lambda *args: None
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        pedido = urllib.request.Request(f'http://127.0.0.1:{porta}/v1/resultados?edicao=2025&pagina=1',
                                        headers={'Authorization': f'Bearer {TOKEN}'})
        with urllib.request.urlopen(pedido, timeout=5) as r:
            corpo = json.load(r)
        print(f"status 200: página {corpo['pagina']} de {corpo['total_paginas']}, "
              f"{len(corpo['itens'])} itens nesta página, total {corpo['total']}")
        servidor.shutdown()
        return
    print(f'API local em http://127.0.0.1:{porta}  rotas: ' + ', '.join(f'/v1/{c}' for c in colecoes))
    print(f'Token: {TOKEN}' + ('  (falhas preparadas ligadas)' if a.falhas else ''))
    print('Ctrl+C para parar.')
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
