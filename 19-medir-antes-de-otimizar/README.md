# 19. Medir antes de otimizar

Os arquivos da aula «Medir antes de otimizar». Rode os comandos de dentro desta pasta. Os dados são os da competição de triatlo, que ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md).

Você precisa do Python com o NumPy, como no README da raiz do kit. Para ver as versões:

```bash
python3 -c "import sys, numpy; print(sys.version.split()[0], numpy.__version__)"
```

A aula foi rodada com o Python 3.9.6 e o NumPy 2.0.2. Se aparecer `No module named 'numpy'`, rode `python3 -m pip install numpy` com o mesmo `python3`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `parciais.py` | Lê `../dados/triatlo/api_resultados.json` e monta os arrays das aulas de NumPy, o mesmo da aula 18. |
| `volume.py` | Monta quantas linhas você pedir a partir dos tempos de 2024, sempre com o mesmo sorteio, o mesmo da aula 17. |
| `medir.py` | `medir.tempo` (melhor e pior tempo pelo `timeit`) e `medir.pico` (pico de memória pelo `tracemalloc`). |
| `versoes.py` | As cinco versões do quadro e a regra `equivale`. |
| `equivalencia.py` | Cada versão do quadro contra a de hoje, pela regra. Aceita `--linhas`. |
| `comparar.py` | O relatório do quadro: memória, tempo e equivalência em 10 mil, 100 mil e 1 milhão de linhas. |
| `etapas.py` | Onde vai o tempo do quadro de hoje. |
| `programa.py` | O pico do programa inteiro, por três caminhos. |
| `pico.py` | O pedido 1 da prática guiada. |
| `medicao.py` | O pedido 2 da prática guiada. |
| `faixas.py` | As quatro versões da contagem por faixa de hora, para o exercício. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 equivalencia.py
python3 comparar.py
python3 etapas.py
python3 programa.py
python3 pico.py
python3 medicao.py
python3 equivalencia.py --linhas 1000
python3 equivalencia.py --linhas 10000
```

No Windows, troque `python3` por `py`.

O `comparar.py` e o `medicao.py` levam alguns segundos cada: eles repetem cada conta até passar de 0,2 segundo, 5 vezes. Os tempos vão sair diferentes dos da aula, e diferentes de uma rodada para outra. A memória sai igual em qualquer rodada.

Para o exercício, crie `relatorio_faixas.py` nesta pasta, ao lado do `faixas.py`, e rode:

```bash
python3 relatorio_faixas.py
```

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
