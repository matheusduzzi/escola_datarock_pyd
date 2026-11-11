# Loja Exemplo

A mesma base de Primeiros passos em dados: SQL e Python para quem está migrando. Se você fez aquele curso, os arquivos são iguais aos que você já usou.

| Arquivo | Linhas | Uma linha é | Colunas |
|---|---|---|---|
| `clientes.csv` | 300 | um cliente | id_cliente, nome, cidade, uf, data_cadastro |
| `produtos.csv` | 40 | um produto | id_produto, nome, categoria, preco |
| `pedidos.csv` | 3003 | um pedido, de um produto só | id_pedido, id_cliente, id_produto, data_pedido, quantidade, valor, status |

Os pedidos vão de 1º de janeiro a 30 de junho de 2026. `status` é `entregue` ou `cancelado`. `valor` é o total do pedido; célula vazia quer dizer que o caixa não anotou o valor, não que o pedido custou zero.

Para gerar os arquivos de novo, de dentro desta pasta:

```bash
python3 gerar.py
```

O gerador só usa a biblioteca padrão do Python e sempre escreve os mesmos arquivos. Não edite os CSVs à mão: se uma aula precisar de outro arquivo, ele vem na pasta da aula.
