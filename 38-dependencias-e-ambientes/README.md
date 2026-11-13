# 38. Dependências e ambientes

Os arquivos da aula «Dependências e ambientes». Rode os comandos de dentro desta pasta. O `arvore.py` lê os programas das outras pastas do kit, então o kit precisa estar inteiro, com as pastas das aulas lado a lado.

Você só precisa do Python. O `arvore.py` usa só a biblioteca padrão: ele lê o que está instalado no Python onde você roda e não instala nada. Para ver a árvore inteira do `requisitos-do-caio.txt`, os pacotes das aulas anteriores precisam estar instalados nesse Python. O que faltar aparece como `FALTANDO`.

A aula foi rodada com o Python 3.9.6 no macOS. No seu computador, as versões, as contas e a lista de pacotes podem sair diferentes: é isso que a aula ensina a ver. No Windows, troque `python3` por `py`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `arvore.py` | Lê um arquivo de requisitos e mostra a árvore: cada pacote, a versão instalada, o Python que ele pede, a licença que declara e quem trouxe. Com `--travar`, imprime a lista travada. Com `--ambiente`, compara a árvore com tudo o que está instalado. Com `--imports`, lê os `.py` das pastas e diz se cada import de fora da biblioteca padrão tem dono na lista. |
| `requisitos-do-caio.txt` | A linha de instalação do Caio, um pacote por linha, sem versão. |
| `estrategia-dependencias.md` | A folha do exercício. Salve uma cópia com o seu nome. |

O arquivo de requisitos aceita o formato do pip: um pacote por linha, com ou sem faixa (`pandas>=2.3,<3`), comentários depois de `#` e a linha `-r outro-arquivo.txt` para incluir outro arquivo.

## Comandos

```bash
python3 arvore.py requisitos-do-caio.txt
python3 arvore.py requisitos-do-caio.txt --imports ..
python3 arvore.py requisitos-do-caio.txt --travar
python3 arvore.py requisitos-do-caio.txt --ambiente
python3 arvore.py ../02-organizar-um-projeto-executavel/entregas-por-cidade/requirements.txt
python3 arvore.py ../02-organizar-um-projeto-executavel/entregas-por-cidade/requirements.txt --imports ../02-organizar-um-projeto-executavel/entregas-por-cidade
```

O `--imports ..` termina com o código 1 quando acha um import sem dono na lista. Com a lista do Caio, ele acha dois: é o que a seção 4 da aula mostra. Quando a sua lista cobre tudo, a última linha diz 0 e o código é 0. Ele não lê o que está dentro de um venv, de uma pasta `site-packages` ou de uma pasta oculta: a `.venv` que você criar aqui para o exercício fica de fora. Se as aulas seguintes acrescentarem programas ao kit, a lista de imports pode crescer.

Sem pacote faltando, os outros modos terminam com o código 0. Com algum `FALTANDO`, terminam com 1. Se o arquivo de requisitos ou a pasta não existir, o `arvore.py` para com o código 2 e diz o que não achou.

## Para o exercício

Escreva o seu `requirements.in` e o seu `requirements-dev.in` nesta pasta. Para gerar a lista travada num ambiente limpo, como na aula 03, «Preparar o ambiente», de Primeiros passos em dados:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.in
.venv/bin/python arvore.py requirements-dev.in --travar
```

No Windows, o Python do venv fica em `.venv\Scripts\python.exe`. A pasta `.venv` não vai para o Git: você apaga e cria de novo quando quiser.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
