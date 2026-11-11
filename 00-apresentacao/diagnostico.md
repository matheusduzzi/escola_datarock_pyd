# Diagnóstico: por onde começar em Python para dados

O Caio, do financeiro da Loja Exemplo, me mandou duas planilhas de março e um programa que parou no meio. Ele queria saber quanto cada categoria faturou e quanto veio de cada cidade. Antes de mexer no programa dele, eu fiz as cinco tarefas abaixo com os mesmos arquivos. Elas usam o que o curso pede de entrada: ler um programa, escrever uma função, ler um CSV, filtrar, agrupar e juntar no pandas, e entender uma mensagem de erro.

O diagnóstico não é prova e não tem nota. Ele mostra por onde você começa. Anote na [folha de respostas](minhas-respostas.md) o que você previu, o comando que rodou e a saída que apareceu. Só depois compare com as respostas comentadas.

Os comandos rodam de dentro da pasta `00-apresentacao/`:

```bash
cd 00-apresentacao
python3 tarefa1.py
```

No Windows, troque `python3` por `py`.

## Os dados

`dados/pedidos.csv` tem 12 pedidos, de 27 de fevereiro a 1º de abril. Uma linha é um pedido. O `valor` é o total do pedido; quando o caixa não anotou o valor, a célula fica vazia. O `status` é `entregue` ou `cancelado`.

`dados/clientes.csv` tem o cadastro dos clientes, com a cidade. Uma linha deveria ser um cliente.

## Tarefa 1. Ler um programa

Abra `tarefa1.py` e leia tudo antes de rodar. Anote na folha o que a última linha vai mostrar: os quatro valores, na ordem. Depois rode e compare.

Responda também:

1. Qual o valor de `total` logo depois do `for`, antes do cupom?
2. Por que `codigo` mostra `70` e não `7`? Que tipo de dado ele é?
3. Se o cupom fosse `"volta10"`, em minúsculas, o que mudaria na saída?

## Tarefa 2. Escrever uma função pequena

Em `tarefa2.py`, escreva a função `total_pedido(itens)`. Ela recebe uma lista de itens, cada um um dicionário com `qtd` e `preco`, e retorna a soma de quantidade vezes preço. Lista vazia retorna `0`.

| Itens | Retorno esperado |
|---|---|
| nenhum item | `0` |
| 2 canecas de 25,00 | `50.0` |
| 2 canecas de 25,00 e 1 camiseta de 60,00 | `110.0` |

Rode o teste:

```bash
python3 testar_tarefa2.py
```

Antes de você escrever a função, o teste avisa que ela ainda não existe e para. Com a função pronta, ele mostra `ok` nos três exemplos. Abra `testar_tarefa2.py` e diga o que a linha `from tarefa2 import total_pedido` faz e em que pasta o Python procura `tarefa2.py`. Depois faça a prova: mova `tarefa2.py` para a pasta de cima, rode o teste de novo, anote a mensagem e coloque o arquivo de volta.

## Tarefa 3. Faturamento de março por categoria

Em `tarefa3.py`, leia `dados/pedidos.csv` com o pandas e monte uma tabela com uma linha por categoria, só com os pedidos **entregues** de **março**. As colunas são:

| Coluna | O que é |
|---|---|
| `categoria` | Casa, Eletro ou Esporte |
| `pedidos` | quantos pedidos entregues a categoria teve em março |
| `sem_valor` | quantos desses pedidos estão com o valor vazio |
| `faturamento` | soma dos valores que existem |

Guarde a tabela final na variável `resultado` e mostre com `print(resultado)`. Diga na folha por que o pedido sem valor entra em `pedidos` e não entra no `faturamento`, e o que mudaria se você trocasse o vazio por zero.

## Tarefa 4. Juntar pedidos e clientes

O Caio também quer os pedidos entregues de março e o faturamento por cidade. Em `tarefa4.py`, junte os pedidos com os clientes pelo `id_cliente` e monte uma tabela com `cidade`, `pedidos` e `faturamento`. Toda cidade do cadastro aparece, mesmo a que não teve pedido, com zero.

Antes de juntar, conte quantos pedidos entregues de março existem. Depois de juntar, conte de novo. Anote os dois números na folha. Se eles forem diferentes, ache o motivo nos dados antes de seguir. A soma da coluna `pedidos` da sua tabela tem que bater com a contagem de antes do merge.

Guarde a tabela final em `resultado` e mostre com `print(resultado)`.

## Tarefa 5. Ler o erro e corrigir

Rode o programa que o Caio mandou:

```bash
python3 tarefa5.py
```

Ele para com uma mensagem de erro. Anote na folha:

1. em que linha o programa parou e qual o tipo do erro;
2. o que a mensagem quer dizer, com as suas palavras;
3. a correção que você fez e a saída depois dela.

Corrija o próprio `tarefa5.py`. Pode ser que a primeira correção revele outro erro; anote esse também. O programa corrigido mostra o total dos pedidos entregues, de todos os meses, e quantos pedidos entregues ficaram de fora por estarem sem valor.

## Como ler o resultado

Cada tarefa olha uma habilidade. Se você travou numa delas, estude a aula de Primeiros passos em dados: SQL e Python para quem está migrando indicada abaixo e volte à tarefa.

| Tarefa | Habilidade | Aulas de Primeiros passos em dados |
|---|---|---|
| Todas | Rodar um script no terminal | 02. Editor, terminal e execução; 03. Preparar o ambiente |
| 1 | Ler um programa com variáveis, tipos, listas, dicionários, `if` e `for` | 19. Como ler um programa; 20. Variáveis, tipos e operadores; 21. Listas e dicionários; 24. Decisões e repetição |
| 2 | Escrever uma função pequena e usar `import` | 22. Funções, métodos e bibliotecas; 23. Escrever uma função pequena |
| 3 | Ler CSV, filtrar e agrupar no pandas | 27. Ler e inspecionar CSV; 28. Selecionar, filtrar e conferir; 30. Agrupar e verificar no pandas; 31. Faturamento por mês |
| 4 | Juntar tabelas no pandas e checar a contagem | 15. Chaves e cardinalidade; 17. Quem ficou de fora do JOIN; 29. Do SQL ao pandas |
| 5 | Ler uma mensagem de erro e corrigir | 25. Ler e corrigir erros de Python; 04. Quando o comando não funciona |

Se as cinco saíram sem ajuda, siga para a aula 01. Se travou em uma ou duas, estude as aulas indicadas e refaça só essas tarefas. Se travou em três ou mais, faça antes a parte de Python e pandas de Primeiros passos em dados, das aulas 19 a 31.

Saber SQL ajuda nas tarefas 3 e 4, mas não substitui o Python: o curso começa do que as cinco tarefas pedem. A tarefa 4 é a que mais pesa, porque o merge roda sem erro e o número sai errado.
