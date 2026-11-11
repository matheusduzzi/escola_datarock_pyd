# 33. Interatividade quando ajuda

Os arquivos da aula «Interatividade quando ajuda». Rode os comandos de dentro desta pasta. Os dados são os da competição de triatlo, que ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md).

## O que você precisa instalar

O pandas e o Matplotlib, os mesmos da aula 31, «Construir gráficos estáticos», e o Plotly, que é novo:

```bash
python3 -m pip install pandas matplotlib plotly
```

O `pip` instala junto o narwhals, que o Plotly usa para ler a tabela do pandas. Para ver a versão que ficou instalada:

```bash
python3 -c "import plotly; print(plotly.__version__)"
```

A aula foi rodada com o Python 3.9.6, o pandas 2.3.3, o Matplotlib 3.9.4, o Plotly 7.1.0 e o narwhals 2.21.0. Os arquivos HTML abrem em qualquer navegador atual. Não precisa de Jupyter nem de conta em site nenhum.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `explorar.py` | Monta os gráficos da aula. Com `--grafico todos` e `--grafico helena`, salva um HTML interativo na pasta `saidas/`. Com `--grafico livia`, salva o PNG estático. Depois de salvar, imprime a ficha do gráfico. Com `--conta categorias`, imprime a corrida mediana de cada categoria nas duas edições. |

O `explorar.py` também serve de biblioteca. `carregar()` retorna uma tabela com uma linha por inscrição das duas edições, com `edicao`, `id_atleta`, `numero_peito`, `categoria`, `equipe`, `sexo`, `status`, as parciais em minutos (`natacao_min`, `t1_min`, `ciclismo_min`, `t2_min`, `corrida_min`) e o tempo oficial em horas (`oficial_h`). Parcial vazia fica vazia, e `equipe` fica vazia para quem corre sem equipe. `concluintes(t)` separa quem concluiu, e `LARGARAM` é a lista dos status de quem largou.

Para os gráficos: `ficha_interativo(fig, arquivo)` imprime a ficha de uma figura do Plotly, com o tamanho do HTML, onde está o plotly.js, a régua dos eixos, as séries, o que aparece ao passar o mouse e as opções do menu. `ficha(fig, arquivo)` faz o mesmo para uma figura do Matplotlib. `salvar_html(fig, 'nome')` e `salvar(fig, 'nome')` gravam em `saidas/`. `helena(t)` retorna a figura interativa da aula, e `virgula(85.4)` escreve `85,4`.

## Comandos

```bash
python3 explorar.py --grafico todos
python3 explorar.py --grafico helena
python3 explorar.py --conta categorias
python3 explorar.py --grafico livia
```

No Windows, troque `python3` por `py`. Os arquivos ficam em `saidas/`. Abra cada HTML com dois cliques, ou arrastando para o navegador. Abra o PNG no visualizador de imagens. Compare com a ficha.

Para a prática e o exercício, crie um arquivo nesta pasta (`guiada.py` ou `meu_explorador.py`), começando por:

```python
import pandas as pd
import plotly.express as px
from explorar import carregar, concluintes, ficha, ficha_interativo, salvar, salvar_html, virgula, helena, LARGARAM

t = carregar()
```

Se o Plotly não estiver instalado, o `explorar.py` para com o código 2 e mostra o comando de instalação. Se não achar os dados, também para com o código 2 e diz qual arquivo faltou: rode de dentro desta pasta, no kit do curso. Sem `--grafico` nem `--conta`, ou com um nome que não existe, ele para com o código 2 e mostra as opções.

## O exercício

O pedido está na página da aula: o Jonas quer um explorador das equipes de 2025 para os técnicos dos clubes e uma versão estática para o boletim. O seu `meu_explorador.py` salva os dois arquivos numa pasta `minhas-saidas/` e imprime as duas fichas.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
