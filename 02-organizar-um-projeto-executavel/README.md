# 02. Organizar um projeto executável

Os arquivos da aula «Organizar um projeto executável». Os dados são os da Loja Exemplo, que ficam em `../dados/loja`. O dicionário das tabelas está em [../dados/loja/LEIA-ME.md](../dados/loja/LEIA-ME.md).

Você precisa do Python com o pandas, como no resto do curso, e do python-dotenv, que lê o arquivo `.env`. Os dois estão no `requirements.txt` do projeto. Se o pandas ainda não está instalado, veja o README da raiz do kit.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `entregas_por_cidade.py` | O script do Caio: um arquivo só, com o caminho da máquina dele e o período escrito no código. |
| `entregas-por-cidade/` | O mesmo relatório organizado em projeto, com README, `.env.exemplo`, `.gitignore` e o pacote `entregas/`. |
| `top_produtos.py` | O script do exercício, também de um arquivo só. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

A pasta `entregas-por-cidade/` tem dois arquivos que começam com ponto: `.env.exemplo` e `.gitignore`. Alguns sistemas escondem esses arquivos. No terminal, `ls -a` mostra os dois; no Windows, `dir /a`.

## Comandos

Da pasta dessa aula:

```bash
python3 entregas_por_cidade.py
```

Para de propósito com `FileNotFoundError` e o código 1: o caminho é o do computador do Caio.

Da pasta do projeto:

```bash
cd entregas-por-cidade
python3 -m pip install -r requirements.txt
cp .env.exemplo .env
python3 -m entregas --inicio 2026-04 --fim 2026-06
python3 -m entregas --inicio 2026-04 --fim 2026-06 --mostrar-config
```

No Windows, troque `python3` por `py` e `cp` por `copy`.

O relatório termina com `Total: 571369.12` e grava `saida/entregas-por-cidade_2026-04_a_2026-06.csv`. Sem o `.env`, o programa para com o código 1 e diz o que fazer. Um mês escrito fora de `AAAA-MM` para com o código 2. O README do projeto tem a tabela das mensagens de erro.

Para o exercício, crie a pasta `produtos-mais-vendidos/` aqui, ao lado de `entregas-por-cidade/`, e organize o `top_produtos.py` nela.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
