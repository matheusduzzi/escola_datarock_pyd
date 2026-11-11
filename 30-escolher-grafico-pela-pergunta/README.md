# 30. Escolher gráfico pela pergunta

Os arquivos da aula «Escolher gráfico pela pergunta». Rode os comandos de dentro desta pasta. Os dados são os da competição de triatlo, que ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md), e as distâncias e a temperatura de cada edição estão em `../dados/triatlo/edicoes.csv`.

Você só precisa do Python com o pandas, como no README da raiz do kit. Essa aula não desenha gráficos: ela imprime os números que cada gráfico mostraria. Desenhar no Matplotlib é a aula 31, «Construir gráficos estáticos». Para ver se o pandas está aí:

```bash
python3 -c "import pandas; print(pandas.__version__)"
```

A aula foi rodada com o Python 3.9.6 e o pandas 2.3.3. Se aparecer `No module named 'pandas'`, rode `python3 -m pip install pandas` com o mesmo `python3`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `resumos.py` | Lê os dados do triatlo e imprime, para cada uma das quatro perguntas da aula, a tabela que o gráfico desenharia, quantas marcas ele tem e quem fica fora. Com `--tabela`, escreve o `resultados.csv`. |
| `plano-visual.md` | A folha do exercício. Salve uma cópia com o seu nome. |

O `resultados.csv` tem uma linha por inscrição das duas edições (880 linhas), já sem as cópias repetidas que a aula 26 mostrou. As colunas são `edicao`, `id_inscricao`, `id_atleta`, `categoria`, `sexo`, `idade` (no ano da prova), `status`, as cinco parciais em minutos (`natacao_min`, `t1_min`, `ciclismo_min`, `t2_min`, `corrida_min`) e o tempo oficial em horas (`oficial_h`). O `status` `sem resultado` marca a inscrição que não tem nenhum resultado no arquivo. Parcial vazia fica vazia.

## Comandos

```bash
python3 resumos.py --pergunta distribuicao
python3 resumos.py --pergunta relacao
python3 resumos.py --pergunta composicao
python3 resumos.py --pergunta evolucao
python3 resumos.py --tabela
```

No Windows, troque `python3` por `py`.

Para as contas do exercício, abra o `resultados.csv` no pandas:

```bash
python3 -c "import pandas as pd; r = pd.read_csv('resultados.csv'); print(r[r.edicao == 2025].status.value_counts())"
```

Se o `resumos.py` não achar os dados, ele para com o código 2 e diz qual arquivo faltou: rode de dentro desta pasta, no kit do curso. Sem `--pergunta` nem `--tabela`, ou com uma pergunta que não existe, ele também para com o código 2 e mostra as opções.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
