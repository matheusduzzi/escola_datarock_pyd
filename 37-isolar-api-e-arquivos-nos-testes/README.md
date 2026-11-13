# 37. Isolar API e arquivos nos testes

Os arquivos da aula «Isolar API e arquivos nos testes». Rode os comandos de dentro desta pasta. Os testes daqui não precisam da API nem dos arquivos do triatlo; só dois comandos usam a API, e eles dizem isso.

## Do que você precisa

O Python 3.9 ou mais novo, o pandas e o pytest, os mesmos da aula 36, «Escrever testes de dados e funções». O `unittest.mock` já vem com o Python. Se ainda não tem o pytest:

```bash
python3 -m pip install pytest
```

A aula foi rodada com o Python 3.9.6, o pandas 2.3.3 e o pytest 8.4.2. A versão mais nova do pytest pede Python 3.10 ou mais novo; no Python 3.9, o `pip` instala a última que funciona nele. Com outras versões, o texto das mensagens pode mudar um pouco, e o tempo no fim da saída muda em toda rodada. O pytest corta as linhas do resumo pela largura do seu terminal. No Windows, troque `python3` por `py`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `coletar.py` | A coleta da aula 12, «Consumir uma API paginada», sem mudança nenhuma. É o programa que os testes testam. |
| `transformacoes.py` | As funções da aula 36, sem mudança. O exercício testa o `ler_dados` dela. |
| `testes_da_ia.py` | Os primeiros testes da coleta, do jeito que a IA escreveu: chamam a API, leem os arquivos do triatlo e gravam na pasta. A seção 1 da aula mostra o que dá errado. |
| `gravar_respostas.py` | Chama a API uma vez e guarda as respostas em `respostas/`. Precisa da API ligada. |
| `respostas/` | As respostas gravadas: três páginas dos desclassificados e uma chamada sem token. |
| `conftest.py` | A guarda de rede, a API falsa (`api_falsa`) e a opção `--defeito`. |
| `test_coleta.py` | Os 9 testes da aula, sem API e sem os arquivos do triatlo. |
| `rodar_sozinho.py` | Copia esta pasta para longe do kit, roda os testes lá e diz se algum teste criou ou mudou arquivo. |
| `defeitos.py` | Cada defeito troca uma linha do `coletar.py` ou do `transformacoes.py`. D1 a D3 são da aula. E1 a E5 são do exercício. |
| `rodar_defeitos.py` | Roda os testes contra cada defeito e diz quais testes pegaram. |
| `test_exercicio.py` | O esqueleto do exercício: seis testes com o nome e o que cada um tem que mostrar. |

## Os comandos que usam a API

Suba a API num terminal e deixe aberto, como na aula 12. A partir da raiz do kit:

```bash
cd api
python3 servidor.py
```

Em outro terminal, nesta pasta:

```bash
python3 -m pytest -q testes_da_ia.py --com-rede --tb=no -rN
python3 gravar_respostas.py
```

O primeiro grava um `resultados-2025.json` nesta pasta. Apague esse arquivo depois: é o problema da seção 1. O segundo grava de novo os arquivos de `respostas/`; com a mesma API, eles saem iguais aos do kit. Depois pare a API com Ctrl+C. Sem a API, o `gravar_respostas.py` diz que ela não respondeu e sai com o código 3.

## Os comandos da aula, sem a API

```bash
python3 -m pytest -q testes_da_ia.py --com-rede --tb=no -rN
python3 -m pytest -q testes_da_ia.py --com-rede --tb=no -rf
python3 -m pytest -q test_coleta.py
python3 -m pytest -q testes_da_ia.py --tb=no -rf
python3 rodar_sozinho.py
python3 rodar_sozinho.py testes_da_ia.py
python3 -m pytest -q test_coleta.py --defeito D1 --tb=no -rf
python3 rodar_defeitos.py
```

O `test_coleta.py` termina com `9 passed`, com a API ligada ou não. O `-rN` esconde a lista das falhas no fim; com `-rf`, o pytest mostra a mensagem de cada teste que falhou. O `--com-rede` desliga a guarda de rede: sem ele, todo teste que tenta abrir uma conexão para com `RedeNoTeste`. Quando algum teste falha, o pytest sai com o código 1: é o que acontece de propósito com o `testes_da_ia.py` e com `--defeito`. Com um defeito que não existe, como `--defeito D9`, ele para com o código 4 e lista os que existem.

O `rodar_defeitos.py` sai com 0 quando todo defeito fez algum teste falhar, com 1 quando algum defeito passou sem nenhum teste falhar, e com 2 quando algum teste falha com as funções certas ou quando o pytest não está instalado. O `rodar_sozinho.py` sai com o código do pytest.

## Para o exercício

```bash
python3 -m pytest -q test_exercicio.py
python3 -m pytest -q test_exercicio.py --defeito E1
python3 rodar_defeitos.py --exercicio
python3 rodar_sozinho.py test_exercicio.py
```

Antes de você escrever os testes, o primeiro mostra `6 skipped` e o `rodar_defeitos.py --exercicio` diz `Defeitos pegos: 0 de 5`, com o código 1. Rodar só `python3 -m pytest -q` roda os dois arquivos que começam com `test_`.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
