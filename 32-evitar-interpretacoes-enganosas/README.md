# 32. Evitar interpretações enganosas

Os arquivos da aula «Evitar interpretações enganosas». Rode os comandos de dentro desta pasta. Os dados são os da competição de triatlo, que ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md).

## O que você precisa instalar

O pandas e o Matplotlib, os mesmos da aula 31, «Construir gráficos estáticos». Se você já rodou aquela aula, não precisa instalar nada. Se não:

```bash
python3 -m pip install pandas matplotlib
```

A aula foi rodada com o Python 3.9.6, o pandas 2.3.3 e o Matplotlib 3.9.4. O Seaborn não é usado aqui.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `revisar.py` | Desenha o gráfico que o Caio mandou para a assembleia, a versão corrigida e o gráfico de abandono do exercício, e salva cada um em PNG na pasta `saidas/`. Depois de salvar, imprime a ficha do gráfico: título, nome e limites dos eixos, marcas, legenda, quantas barras e onde elas começam, e os textos. Com `--conta`, imprime os números que a revisão usa: eixo, agregação, cobertura e seleção. |

O `revisar.py` também serve de biblioteca. `carregar()` retorna uma tabela com uma linha por inscrição das duas edições, com `edicao`, `id_atleta`, `categoria`, `sexo`, `idade`, `status`, as parciais em minutos (`natacao_min`, `t1_min`, `ciclismo_min`, `t2_min`, `corrida_min`) e o tempo oficial em horas (`oficial_h`). Parcial vazia fica vazia. `concluintes(t)` separa quem concluiu. `LARGARAM` é a lista dos status de quem largou: `concluiu`, `DNF` e `DSQ`. `ficha(fig)` imprime a ficha de qualquer figura do Matplotlib, e `virgula(85.4)` escreve `85,4`.

## Comandos

```bash
python3 revisar.py --grafico caio
python3 revisar.py --conta eixo
python3 revisar.py --conta agregacao
python3 revisar.py --conta cobertura
python3 revisar.py --conta selecao
python3 revisar.py --grafico corrigido
python3 revisar.py --grafico abandono
```

No Windows, troque `python3` por `py`. Os PNGs ficam em `saidas/`. Abra cada um no visualizador de imagens e compare com a ficha.

Para a prática e o exercício, crie um arquivo nesta pasta (`guiada.py` ou `meu_grafico.py`), começando por:

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from revisar import carregar, concluintes, ficha, virgula, LARGARAM

t = carregar()
```

Se o `revisar.py` não achar os dados, ele para com o código 2 e diz qual arquivo faltou: rode de dentro desta pasta, no kit do curso. Sem `--grafico` nem `--conta`, ou com um nome que não existe, ele também para com o código 2 e mostra as opções.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
