# 25. Agregações, transform e métricas de grupo

Os arquivos da aula «Agregações, transform e métricas de grupo». Rode os comandos de dentro desta pasta. Os dados da competição de triatlo ficam em `../dados/triatlo`, com o dicionário em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md). O exemplo pequeno fica em `exemplo/`.

Você só precisa do Python com o pandas, como no README da raiz do kit. Para ver se ele está aí:

```bash
python3 -c "import pandas; print(pandas.__version__)"
```

A aula foi rodada com o Python 3.9.6 e o pandas 2.3.3. Se aparecer `No module named 'pandas'`, rode `python3 -m pip install pandas` com o mesmo `python3`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `metricas.py` | Monta a base do triatlo, uma linha por inscrição, e calcula as métricas de grupo da aula, cada uma no grão que o pedido precisa. As funções dele servem para o exercício. |
| `exemplo/resultados.csv` | Oito inscrições, pequenas o bastante para fazer as contas de cabeça. |
| `exemplo/esperado_tabela.csv` e `exemplo/esperado_atletas.csv` | As respostas do exemplo, feitas à mão antes de rodar o código. |
| `metricas-equipe.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 metricas.py --passo caio
python3 metricas.py --passo tabela
python3 metricas.py --passo atleta
python3 metricas.py --passo podio
python3 metricas.py --passo taxa
python3 metricas.py --passo exemplo
```

No Windows, troque `python3` por `py`.

O passo `exemplo` roda as mesmas funções no exemplo pequeno e compara com as respostas feitas à mão. Se uma conta não bate, ele diz qual e para com o código 1.

## As funções, para o exercício

```bash
python3 -c "from metricas import *; base = carregar_base(); print(len(base), base['equipe'].isna().sum())"
```

A saída é `880 414`: 880 inscrições, 414 delas sem equipe.

| Função | O que faz |
|---|---|
| `carregar_base()` | A base: uma linha por inscrição das duas edições, com o resultado da API. Tem as colunas `tempo_s` (o tempo oficial em segundos, vazio para quem não concluiu), `largou`, `concluiu` e `sem_resultado`. |
| `ler_exemplo()` | O exemplo pequeno, com as mesmas colunas da base. |
| `preparar(tabela)` | Acrescenta `tempo_s`, `largou`, `concluiu` e `sem_resultado` a uma tabela com `status` e `tempo_oficial`. Serve para montar o seu exemplo pequeno. |
| `tabela(base, chave)` | Uma linha por grupo: inscritos, largaram, concluíram, sem resultado, taxa de conclusão e mediana do tempo. Para se uma coluna da chave tiver valor vazio. |
| `por_atleta(base, chave)` | Uma linha por atleta que concluiu, com a posição no grupo, a mediana do grupo e a diferença para ela. Para se alguém concluiu sem tempo. |
| `podio(atletas, chave, minimo, lugares)` | Só as categorias com pelo menos `minimo` atletas que concluíram, e nelas só os primeiros `lugares`. |
| `taxa_geral(tabela, nivel)` | A taxa de cada edição pelas contas somadas, ao lado da média das taxas dos grupos e da taxa por inscritos. |
| `hms`, `dif`, `pct` | Mostram segundos como `11:30:22`, diferenças como `+0:13:50` e frações como `89,1%`. |

A `chave` padrão é `['edicao', 'categoria']`. A `largou` é verdadeira para `concluiu`, `DNF` e `DSQ`.

Se o `metricas.py` não achar os dados, ele para com o código 2 e diz qual arquivo faltou: rode de dentro desta pasta, no kit do curso. Sem `--passo`, ou com um passo que não existe, ele também para com o código 2 e mostra as opções.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
