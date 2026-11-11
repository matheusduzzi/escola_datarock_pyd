# 01. Escolher Python, SQL e ambiente de execução

Os arquivos da aula «Escolher Python, SQL e ambiente de execução». Rode os comandos de dentro desta pasta. Os dois programas usam a base da Loja Exemplo, em `../dados/loja`; o dicionário está em [../dados/loja/LEIA-ME.md](../dados/loja/LEIA-ME.md).

Os programas usam o pandas do kit do curso (veja o README da raiz do kit) e o `sqlite3`, que já vem com o Python. As saídas da aula são do pandas 2.3.3 com Python 3.9. No pandas 3, os bytes das colunas de texto na parte 4 do `comparar.py` podem sair diferentes, porque o texto ganhou outro tipo; os resultados das contas são os mesmos.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `comparar.py` | Monta um banco SQLite na memória com os pedidos e os produtos da loja e faz o faturamento por mês em SQL e em pandas. Mostra quantas linhas saem do banco, a memória da tabela e se os dois batem. |
| `por_partes.py` | Lê os pedidos em pedaços e mostra o que dá para fazer por partes: o faturamento bate, os clientes diferentes só batem juntando os ids, a mediana não bate. |
| `situacoes.md` | As três situações do exercício. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 comparar.py
python3 por_partes.py
python3 por_partes.py --linhas 1000
python3 por_partes.py --linhas 5000
```

No Windows, troque `python3` por `py`.

O `comparar.py` mostra cinco partes, uma depois da outra. O `por_partes.py` usa 500 linhas por pedaço se você não disser nada. Com `--linhas 5000`, a tabela inteira cabe num pedaço só e as três contas batem: é de propósito, é o pedido 2 da prática guiada.

Os dois programas não gravam nada. Eles só leem `../dados/loja` e mostram o resultado no terminal.

O exercício não tem programa: você decide e escreve na folha.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
