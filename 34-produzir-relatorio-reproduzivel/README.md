# 34. Produzir relatório reproduzível

Os arquivos da aula «Produzir relatório reproduzível». Rode os comandos de dentro desta pasta. Os dados são os da competição de triatlo, que ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md).

## O que você precisa instalar

O pandas e o Matplotlib, os mesmos da aula 31, «Construir gráficos estáticos». Nada de novo:

```bash
python3 -m pip install pandas matplotlib
```

A aula foi rodada com o Python 3.9.6, o pandas 2.3.3 e o Matplotlib 3.9.4. Com outras versões, o relatório sai com os mesmos números, mas o fim dele muda, porque ele escreve as versões que usou. Os PNGs também podem sair com outros bytes.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `relatorio.py` | Gera o relatório da prova inteiro numa pasta `relatorio/`: o `relatorio.md`, o `numeros.csv` e as figuras em `relatorio/figuras/`. Depois imprime o que gravou, com o começo do sha256 de cada arquivo. Com `--numeros`, imprime também de onde vem cada número das frases. |

O `relatorio.md` é um arquivo Markdown, texto com marcação leve. Abra no VS Code e use a pré-visualização do Markdown para ver as tabelas e as figuras no lugar. O `numeros.csv` abre em qualquer planilha.

O `relatorio.py` também serve de biblioteca:

- `carregar()` retorna uma tabela com uma linha por inscrição das duas edições, com `edicao`, `id_atleta`, `numero_peito`, `categoria`, `equipe`, `sexo`, `status`, as parciais em minutos (`natacao_min`, `t1_min`, `ciclismo_min`, `t2_min`, `corrida_min`) e o tempo oficial em horas (`oficial_h`). `carregar_edicoes()` retorna o `edicoes.csv` com a edição no índice. `concluintes(t)` separa quem concluiu.
- `Registro()` guarda os números das frases. `r.anota(nome, valor, conta, base, casas=1, unidade='')` anota o número e retorna o texto dele, já com vírgula: `r.anota('taxa', 89.12, 'concluíram / largaram', 'quem largou', unidade='%')` retorna `'89,1%'`. `r['taxa']` retorna o mesmo texto de novo. `r.tabela()` retorna a tabela de origem.
- `tabela_md(df)` escreve uma tabela do pandas em Markdown, com vírgula nos decimais. `salvar_figura(fig, caminho)` grava o PNG e fecha a figura. `virgula(85.4)` escreve `85,4`.
- `numeros_sem_origem(texto, r)` retorna os números das frases de um texto que não estão no registro. `hashes(pasta)` retorna o começo do sha256 de cada arquivo da pasta.
- `gerar(dados, saida, carimbo)` grava o relatório da aula numa pasta e retorna os hashes do que gravou. O `carimbo` é uma linha de texto livre, que vai para o fim, em «Como gerar de novo». Se uma conta não fecha, ele levanta `ContaNaoFecha` e não grava nada.

## Comandos

```bash
python3 relatorio.py
python3 relatorio.py --numeros
```

No Windows, troque `python3` por `py`. Rode duas vezes e compare os hashes que aparecem: com os mesmos dados, são os mesmos.

Se uma conta não fecha, por exemplo um resultado da API sem inscrição, o programa para com o código 1, diz o motivo e não grava nada. A pasta `relatorio/` de antes fica como estava. Se não achar os dados, para com o código 2 e diz qual arquivo faltou: rode de dentro desta pasta, no kit do curso.

Para a prática e o exercício, crie um arquivo nesta pasta (`guiada.py` ou `meu_relatorio.py`), começando por:

```python
import pandas as pd
import matplotlib.pyplot as plt
from relatorio import (carregar, carregar_edicoes, concluintes, gerar, hashes, Registro, ContaNaoFecha,
                       tabela_md, salvar_figura, numeros_sem_origem, virgula)
```

## O exercício

O pedido está na página da aula: a Marta quer saber se a natação de 2025 foi mais rápida, ou só mais curta. O seu `meu_relatorio.py` grava o relatório numa pasta `meu-relatorio/`, do zero, a cada vez que roda.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
