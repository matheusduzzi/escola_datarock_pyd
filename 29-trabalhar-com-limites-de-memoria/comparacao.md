# Faturamento por mês e categoria: memória e resultado

Arquivo: historico_itens.csv, 409.176 linhas x 20 colunas. Resultado: 150 somas (30 meses x 5 categorias), total R$ 126.673.501,75, comparadas em centavos com a leitura do arquivo inteiro.

Pico de memória de cada jeito, lendo as primeiras 100 mil linhas, as primeiras 200 mil e o arquivo todo:

| Jeito | 100 mil linhas | 200 mil linhas | 409.176 linhas (todas) | Resultado com o arquivo inteiro |
|---|---:|---:|---:|---|
| lê tudo (o código da IA) | 65,0 MB | 128,8 MB | 261,7 MB | é a referência |
| só as 5 colunas da conta | 14,0 MB | 28,0 MB | 57,1 MB | igual: 150 valores iguais em centavos |
| 5 colunas com tipos menores | 8,4 MB | 16,8 MB | 34,1 MB | igual: 150 valores iguais em centavos |
| 5 colunas, tipos e partes de 20000 linhas | 2,7 MB | 2,7 MB | 2,7 MB | igual: 150 valores iguais em centavos |
| o mesmo, com valor em float32 | 2,5 MB | 2,5 MB | 2,6 MB | diferente: 134 de 150 valores diferentes (maior diferença R$ 0,23) |

- O pico é medido com o tracemalloc (medir.py): a memória que o Python e o pandas pediram durante a leitura e a conta.
  O gerenciador de tarefas mostra mais, porque soma o próprio Python. A régua é a mesma para todos os jeitos.
- Tudo roda num computador só, uma parte depois da outra.

Gerado por `python3 memoria.py --jeito comparar`.
