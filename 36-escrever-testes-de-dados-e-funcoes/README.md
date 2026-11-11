# 36. Escrever testes de dados e funções

Os arquivos da aula «Escrever testes de dados e funções». Rode os comandos de dentro desta pasta. Os dados são os da competição de triatlo, que ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md).

## Do que você precisa

O Python 3.9 ou mais novo, o pandas e o pytest. O pandas você já tem do kit do curso. Instale o pytest no mesmo Python:

```bash
python3 -m pip install pytest
```

E veja a versão:

```bash
python3 -m pytest --version
```

A aula foi rodada com o Python 3.9.6, o pandas 2.3.3 e o pytest 8.4.2. A versão mais nova do pytest pede Python 3.10 ou mais novo; no Python 3.9, o `pip` instala a última que funciona nele. Com outras versões, o texto das mensagens de erro pode mudar um pouco, e o tempo no fim da saída muda em toda rodada. Se aparecer `No module named pytest`, o `pip` instalou em outro Python: rode o `pip` com o mesmo `python3` que você usa para rodar os testes.

No Windows, troque `python3` por `py`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `transformacoes.py` | As funções do relatório: `montar_tabela`, `taxa_conclusao`, `ritmo_natacao` (aula), `melhor_por_atleta` e `ritmo_corrida` (exercício), cada uma com o comentário do que promete. Também tem `ler_dados`, que lê os arquivos do triatlo. |
| `test_tabela.py` | Os 12 testes da aula: regra de negócio, chave, tipos e tolerância. |
| `conftest.py` | As fixtures `dados` e `tabela`, e a opção `--defeito`, que troca uma função pela versão com defeito. |
| `defeitos.py` | As versões com defeito. D1 a D5 são das funções da aula. E1 a E5 são das funções do exercício. |
| `tolerancias.py` | Três jeitos de comparar o mesmo ritmo, para a seção de tolerância. Dois falham de propósito. |
| `rodar_defeitos.py` | Roda os testes contra cada defeito e diz quais testes pegaram. |
| `test_exercicio.py` | O esqueleto do exercício: sete testes com o nome e o que cada um tem que mostrar. |

## Comandos

```bash
python3 -m pytest -q test_tabela.py
python3 -m pytest -q test_tabela.py --defeito D3 --tb=short
python3 -m pytest -q tolerancias.py --tb=short
python3 -m pytest -q tolerancias.py --defeito D4 --tb=no -rf
python3 rodar_defeitos.py
```

O primeiro roda os 12 testes da aula e termina com `12 passed`. Com `--defeito`, o pytest troca uma função pela versão com defeito antes de rodar, e a saída termina dizendo qual defeito estava ativo. Quando algum teste falha, o pytest sai com o código 1: é o que acontece de propósito com `--defeito D3` e com o `tolerancias.py`. Com um defeito que não existe, como `--defeito D9`, ele para com o código 4 e lista os que existem.

O `rodar_defeitos.py` sai com 0 quando todo defeito fez algum teste falhar, com 1 quando algum defeito passou sem nenhum teste falhar, e com 2 quando algum teste falha com as funções certas ou quando o pytest não está instalado.

Para o exercício:

```bash
python3 -m pytest -q test_exercicio.py
python3 -m pytest -q test_exercicio.py --defeito E1
python3 rodar_defeitos.py --exercicio
```

Antes de você escrever os testes, o primeiro mostra `7 skipped` e o último diz `Defeitos pegos: 0 de 5`, com o código 1. Rodar só `python3 -m pytest -q` roda os dois arquivos `test_` juntos.

Se o pytest não achar os dados, o teste que usa a fixture `tabela` para com `arquivo não encontrado` e diz qual arquivo faltou: rode de dentro desta pasta, no kit do curso.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
