# 10. Ler JSON aninhado

Os arquivos da aula «Ler JSON aninhado». Os programas acham os arquivos a partir do lugar deles, então rodam de dentro desta pasta ou da raiz do kit. Os comandos abaixo são de dentro desta pasta.

Os programas usam o pandas do kit do curso (veja o README da raiz do kit). As saídas da aula são do pandas 2.3.3 com Python 3.9.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `pedidos-online-novembro-semana-1.json` | A exportação nova da loja online, com carrinho, de 1 a 7 de novembro, do jeito que o Caio mandou. |
| `pedidos-online-reenvio-dia-3.json` | Os pedidos do dia 3 de novembro, exportados de novo pelo aplicativo. É o pedido 3 da prática guiada. |
| `olhar_json.py` | Mostra o que o `pd.read_json` e o `pd.json_normalize` fazem com o arquivo e conta as chaves de cada pedido. |
| `juntar_direto.py` | O jeito direto: abre a lista de itens com o `json_normalize` e soma o faturamento. |
| `separar_pedidos.py` | Separa o arquivo em duas tabelas, pedidos e itens, ligadas pelo `id_pedido`, depois de olhar as regras do combinado. |
| `resumo_semana.py` | Responde a gerente com as duas tabelas e o cadastro de produtos da loja, em `../dados/loja/`. |
| `resultados-2025.json` | Os resultados da edição 2025 do triatlo, exportados pela cronometragem, para o exercício. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 olhar_json.py
python3 juntar_direto.py
python3 separar_pedidos.py
python3 resumo_semana.py
python3 separar_pedidos.py --arquivo pedidos-online-reenvio-dia-3.json
```

No Windows, troque `python3` por `py`.

O `juntar_direto.py` roda sem erro e soma um faturamento maior que o de verdade. A aula mostra por quê.

O `separar_pedidos.py` grava `saida/pedidos.csv` e `saida/itens.csv`. Rode ele antes do `resumo_semana.py`, que lê essas duas tabelas. O último comando lê o reenvio do dia 3 e termina com o código 1, sem gravar nada: é de propósito, é o pedido 3 da prática guiada.

As mensagens de problema saem no terminal com `ERROR` na frente. O resumo sai na saída normal. Para ver o código de saída do último comando, rode `echo $?` no macOS e no Linux, ou `echo $LASTEXITCODE` no PowerShell.

Para ver que o caminho parte do programa, rode da raiz do kit:

```bash
cd ..
python3 10-ler-json-aninhado/separar_pedidos.py
python3 10-ler-json-aninhado/resumo_semana.py
```

A pasta `saida/` é criada pelo programa. Pode apagar quando quiser: ela sai igual toda vez que você roda.

O exercício não tem programa pronto: você escreve o seu, usando o `separar_pedidos.py` como modelo.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
