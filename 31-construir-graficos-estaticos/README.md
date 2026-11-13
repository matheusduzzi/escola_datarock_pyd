# 31. Construir gráficos estáticos

Os arquivos da aula «Construir gráficos estáticos». Rode os comandos de dentro desta pasta. Os dados são os da competição de triatlo, que ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md).

## O que você precisa instalar

Essa é a primeira aula do curso que desenha gráficos. Além do pandas, você precisa do Matplotlib e do Seaborn. Instale com o mesmo `python3` que roda as aulas:

```bash
python3 -m pip install matplotlib seaborn
```

E veja se funcionou:

```bash
python3 -c "import matplotlib, seaborn; print(matplotlib.__version__, seaborn.__version__)"
```

A aula foi rodada com o Python 3.9.6, o pandas 2.3.3, o Matplotlib 3.9.4 e o Seaborn 0.13.2. No Python 3.9, o `pip` instala o Matplotlib 3.9, que é a última versão para esse Python. Num Python mais novo, ele instala uma versão mais nova, e o código da aula usa só funções que existem desde o Matplotlib 3.7. Se aparecer `No module named 'matplotlib'`, o `pip` instalou em outro Python: rode o comando de instalação de novo com o mesmo `python3`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `graficos.py` | Desenha os gráficos da aula e salva cada um em PNG na pasta `saidas/`. Depois de salvar, imprime a ficha do gráfico: título, nome dos eixos, limites e marcas de cada eixo, legenda e quantas barras, linhas ou pontos foram desenhados. A ficha é lida do próprio gráfico, não do código. |

O `graficos.py` também serve de biblioteca para o exercício. `carregar()` devolve uma tabela com uma linha por inscrição das duas edições, com `edicao`, `categoria`, `sexo`, `idade`, `status`, as parciais em minutos (`natacao_min`, `t1_min`, `ciclismo_min`, `t2_min`, `corrida_min`) e o tempo oficial em horas (`oficial_h`). Parcial vazia fica vazia. `ficha(fig)` imprime a ficha de qualquer figura do Matplotlib, inclusive as que o Seaborn desenha.

## Comandos

```bash
python3 graficos.py --grafico rascunho
python3 graficos.py --grafico chegada
python3 graficos.py --grafico edicoes
python3 graficos.py --grafico inscritos
python3 graficos.py --grafico dispersao-matplotlib
python3 graficos.py --grafico dispersao-seaborn
python3 graficos.py --grafico todos
```

No Windows, troque `python3` por `py`. Os PNGs ficam em `saidas/`. Abra cada um no visualizador de imagens e compare com a ficha.

Para o exercício, crie um arquivo `meus_graficos.py` nesta pasta, começando por:

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from graficos import carregar, ficha

t = carregar()
```

Se o `graficos.py` não achar os dados, ele para com o código 2 e diz qual arquivo faltou: rode de dentro desta pasta, no kit do curso. Sem `--grafico`, ou com um gráfico que não existe, ele também para com o código 2 e mostra as opções.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
