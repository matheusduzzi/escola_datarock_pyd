# Contrato de entrada: pedidos da loja online

O combinado entre a Loja Exemplo e a plataforma da loja online. É o que o `ler_pedidos_online.py` segue. Quando o arquivo chega diferente disso, o programa para e diz o que veio diferente.

## O arquivo

| Item | CSV | JSON |
|---|---|---|
| Como vem | Uma linha por pedido, com cabeçalho | Uma lista de objetos, um objeto por pedido |
| Codificação | Windows-1252 (`cp1252`), a da planilha da plataforma | UTF-8 |
| Separador | `;` | não tem |
| Decimal | vírgula, sem separador de milhar: `1535,02` | ponto, como número: `1535.02` |
| Data e hora | `DD/MM/AAAA HH:MM`, horário de Brasília: `01/07/2026 02:57` | ISO 8601 com o fuso: `2026-07-01T02:57:00-03:00` |
| Vazio | célula vazia | `null` |

Uma linha (ou um objeto) é um pedido de um produto só. Os nomes dos campos são exatamente os da tabela abaixo, sem campo a mais nem a menos.

## Os campos

| Campo | Tipo | Pode vir vazio? | Formato ou valores | O que quer dizer |
|---|---|---|---|---|
| `id_pedido` | texto | não | 6 dígitos, com os zeros à esquerda: `004801` | o número do pedido na plataforma; não se repete no arquivo |
| `id_cliente` | inteiro | não | o `id_cliente` do cadastro da loja | quem comprou |
| `id_produto` | inteiro | não | o `id_produto` do cadastro da loja | o que comprou |
| `data_pedido` | data e hora | não | veja a tabela do arquivo | quando o cliente fechou o pedido |
| `cidade_entrega` | texto | não | com acento, como no cadastro: `São Carlos` | para onde vai |
| `quantidade` | inteiro | não | 1 ou mais | quantas unidades do produto |
| `valor` | decimal, em reais | não | duas casas | o total do pedido, já com o desconto do cupom |
| `cupom` | texto | sim | o código do cupom: `VOLTA15` | vazio quer dizer pedido sem cupom |
| `status` | texto | não | `pago`, `enviado`, `entregue` ou `cancelado` | em que pé está o pedido |

## No pandas

| Tipo do contrato | Tipo no pandas |
|---|---|
| texto | `string` |
| inteiro | `int64` |
| decimal | `float64` |
| data e hora | `datetime64[ns, America/Sao_Paulo]` |

O `id_pedido` é texto porque é um código, não uma quantidade: ninguém soma número de pedido. Se ele virar o número `4801`, perde os zeros e não bate mais com o `004801` que aparece na plataforma e no e-mail do cliente.
