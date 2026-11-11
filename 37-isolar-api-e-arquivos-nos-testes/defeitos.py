"""Versões com defeito do coletar.py e do transformacoes.py. Aula «Isolar API e arquivos nos testes».

Cada defeito troca uma linha só da função certa. A tabela DEFEITOS mostra a linha de antes e a de depois.
O conftest.py aplica a troca quando você roda
    python3 -m pytest --defeito D1
e os testes dizem se pegam o defeito. A função roda, não dá erro de sintaxe e parece certa.

D1 a D3 são do coletar.py e são pegos pelos testes da aula. E1 a E5 são do exercício.
"""
import inspect

import coletar
import transformacoes

# código: (módulo, função, linha certa, linha com defeito, o que está errado)
DEFEITOS = {
    'D1': (coletar, 'coletar',
           'for pagina in range(1, total_paginas + 1):',
           'for pagina in range(1, total_paginas):',
           'a última página nunca é pedida'),
    'D2': (coletar, 'coletar',
           'if corpo["total"] != total:',
           'if False:',
           'o total que muda no meio da coleta passa sem aviso'),
    'D3': (coletar, 'chamar',
           'resposta = erro  # 4xx e 5xx: o código e o corpo vêm na exceção',
           'raise ApiForaDoAr(f"a API não respondeu em {endereco}: {erro}")',
           'um erro 401 ou 404 vira "a API não respondeu"'),
    'E1': (transformacoes, 'ler_dados',
           "pd.read_csv(pasta / 'inscricoes_2025.csv', sep=';')",
           "pd.read_csv(pasta / 'inscricoes_2025.csv')",
           'o arquivo de 2025 é lido com vírgula, e não ponto e vírgula'),
    'E2': (transformacoes, 'ler_dados',
           'pasta = Path(pasta)',
           'pasta = Path(DADOS)',
           'a pasta pedida é ignorada: lê sempre ../dados/triatlo'),
    'E3': (coletar, 'chamar',
           'headers={"Authorization": f"Bearer {token}"})',
           'headers={})',
           'a chamada sai sem o token'),
    'E4': (coletar, 'chamar',
           'resposta = urllib.request.urlopen(pedido, timeout=espera)',
           'resposta = urllib.request.urlopen(pedido)',
           'a chamada não tem tempo limite'),
    'E5': (coletar, 'main',
           'token = os.environ.get("API_TRIATLO_TOKEN")',
           'token = os.environ.get("API_TRIATLO_TOKEN") or "kit-local"',
           'sem a variável do token, o programa usa um token escrito no código'),
}


def ativar(codigo):
    """Troca a função certa pela mesma função com a linha do defeito. Retorna a descrição."""
    modulo, nome, antes, depois, descricao = DEFEITOS[codigo]
    fonte = inspect.getsource(getattr(modulo, nome))
    assert fonte.count(antes) == 1, f'{codigo}: a linha certa não está uma vez só em {nome}'
    exec(compile(fonte.replace(antes, depois), modulo.__file__, 'exec'), vars(modulo))
    return f'{codigo} em {nome}: {descricao}'
