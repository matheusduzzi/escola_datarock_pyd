# 07. Depurar e tratar exceções

Os arquivos da aula «Depurar e tratar exceções». Rode os comandos de dentro desta pasta. O cadastro de produtos e o de clientes vêm de `../dados/loja`; o dicionário das tabelas está em [../dados/loja/LEIA-ME.md](../dados/loja/LEIA-ME.md).

Os programas dessa aula só usam a biblioteca padrão do Python 3.9 ou mais novo. Não precisa instalar nada.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `pedidos-julho.csv` | Os pedidos de julho como o caixa mandou da primeira vez. |
| `pedidos-julho-v2.csv` | O mesmo arquivo, que o caixa mandou de novo com os valores corrigidos. |
| `fechamento.py` | O fechamento do mês do Caio, como estava na pasta do financeiro. |
| `fechamento_corrigido.py` | O fechamento depois da aula: trata o pedido sem valor e para com uma lista quando o arquivo tem problema. |
| `roteiro-de-investigacao.md` | Os passos que a aula segue quando um programa falha. |
| `clientes_por_cidade.py` | O programa do exercício. |
| `clientes-julho.csv` | O cadastro de clientes com os três clientes cadastrados em julho. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 fechamento.py
python3 fechamento_corrigido.py
python3 fechamento_corrigido.py --arquivo pedidos-julho-v2.csv
python3 fechamento_corrigido.py --arquivo pedidos-agosto.csv
python3 clientes_por_cidade.py
python3 clientes_por_cidade.py --clientes clientes-julho.csv
```

No Windows, troque `python3` por `py`.

O `fechamento.py` do Caio termina sem erro e mostra `Total: 166733.75`. A aula mostra por que esse número está errado.

O `fechamento_corrigido.py` com o arquivo da primeira vez termina com o código 1 e lista duas linhas com problema, sem gravar nada. Com o `pedidos-julho-v2.csv`, ele mostra `Total: 168449.21`, conta os pedidos sem valor e grava `saida/fechamento.csv`. O `pedidos-agosto.csv` não existe: o comando é para você ver a mensagem.

As mensagens de erro saem no terminal com `ERROR` na frente. A tabela e o total saem na saída normal. Para ver o código de saída do último comando, rode `echo $?` no macOS e no Linux, ou `echo $LASTEXITCODE` no PowerShell.

Os dois comandos do `clientes_por_cidade.py` param com erro. É de propósito: é o ponto de partida do exercício.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
