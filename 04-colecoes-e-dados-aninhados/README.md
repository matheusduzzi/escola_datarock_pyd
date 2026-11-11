# 04. Coleções e dados aninhados

Os arquivos da aula «Coleções e dados aninhados». Rode os comandos de dentro desta pasta. Os dois arquivos JSON têm os pedidos de junho e de maio da Loja Exemplo, como o aplicativo de vendas mandou, com cliente e produto dentro de cada pedido. A base da loja, com o status final de cada pedido, está em `../dados/loja`; o dicionário das tabelas está em [../dados/loja/LEIA-ME.md](../dados/loja/LEIA-ME.md).

Os programas dessa aula só usam a biblioteca padrão do Python 3.9 ou mais novo. O pandas só aparece na contagem pela base, no exercício, e é o mesmo que você instalou para o curso.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `pedidos-junho.json` | Os 528 registros de junho, com cópias e versões antigas. A aula e a prática guiada usam este. |
| `pedidos-maio.json` | Os registros de maio, no mesmo formato. O exercício usa este. |
| `avaliacoes_caio.py` | O programa do Caio: conta os entregues do arquivo, sem tirar repetição. |
| `avaliacoes.py` | O programa depois da aula: tira cópias e versões antigas com a regra escrita, monta um pedido de avaliação por cliente e produto e grava a lista. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 avaliacoes_caio.py
python3 avaliacoes.py
```

No Windows, troque `python3` por `py`.

O `avaliacoes_caio.py` mostra 479 pedidos de avaliação. A aula começa por aí. O `avaliacoes.py` mostra as contas de cada etapa, a tabela por cidade e grava `saida/avaliacoes-junho.csv`. A pasta `saida/` é criada na primeira vez que você roda.

Para a prática guiada, crie um arquivo seu nesta pasta e importe as funções do `avaliacoes.py`, como a aula mostra.

O exercício pede que você escreva o seu `cupons.py` nesta pasta, para os pedidos de maio.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
