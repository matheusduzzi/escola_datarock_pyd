"""Chama a API do kit uma vez e guarda as respostas em respostas/, para os testes usarem sem a API.

Com a API rodando em outro terminal (a partir da raiz do kit: python3 api/servidor.py), de dentro desta pasta:
    python3 gravar_respostas.py

Grava duas coisas, cada uma num arquivo JSON com a chamada, o código e o corpo da resposta:
  - as páginas dos desclassificados (status=DSQ), 3 por página: dsq-pagina-1.json, dsq-pagina-2.json...
  - a resposta de uma chamada sem token: sem-token.json

São respostas de verdade da API, e não escritas à mão. Os testes leem esses arquivos e nunca chamam a API.
Rode de novo só quando a API mudar; depois, rode os testes e veja o que mudou.
"""
import json
import sys
from pathlib import Path

from coletar import ENDERECO_PADRAO, ROTA, ApiForaDoAr, chamar

BASE_URL = ENDERECO_PADRAO  # o servidor local do kit
TOKEN = 'kit-local'  # o token da API do kit; um token de verdade nunca fica escrito no programa
PASTA = Path('respostas')


def guardar(nome, codigo, corpo, caminho):
    arquivo = PASTA / nome
    arquivo.write_text(json.dumps({'chamada': caminho, 'codigo': codigo, 'corpo': corpo},
                                  ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'{arquivo}: {codigo}, {len(corpo.get("itens", []))} itens')


def main():
    PASTA.mkdir(exist_ok=True)
    filtros = {'status': 'DSQ'}  # a mesma ordem de parâmetros que o coletar.py usa
    try:
        pagina, total_paginas = 1, 1
        while pagina <= total_paginas:
            codigo, corpo, caminho = chamar(BASE_URL, TOKEN, ROTA, dict(filtros, pagina=pagina, por_pagina=3), 10)
            if codigo != 200:
                print(f'a página {pagina} respondeu {codigo}; nada mais foi gravado')
                return 1
            guardar(f'dsq-pagina-{pagina}.json', codigo, corpo, caminho)
            total_paginas = corpo['total_paginas']
            pagina += 1
        codigo, corpo, caminho = chamar(BASE_URL, '', ROTA, dict(filtros, pagina=1, por_pagina=3), 10)
        guardar('sem-token.json', codigo, corpo, caminho)
    except ApiForaDoAr as erro:
        print(f'{erro}. Suba a API em outro terminal, a partir da raiz do kit: python3 api/servidor.py')
        return 3
    return 0


if __name__ == '__main__':
    sys.exit(main())
