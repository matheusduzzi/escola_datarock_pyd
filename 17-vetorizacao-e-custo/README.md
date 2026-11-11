# 17. Vetorização e custo

Os arquivos da aula «Vetorização e custo». Rode os comandos de dentro desta pasta. Os dados são os da competição de triatlo, que ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md), e as distâncias de cada edição estão em `../dados/triatlo/edicoes.csv`.

Você só precisa do Python com o NumPy. O NumPy vem junto quando você instala o pandas, como no README da raiz do kit. Para ver se ele está aí:

```bash
python3 -c "import numpy; print(numpy.__version__)"
```

A aula foi rodada com o Python 3.9.6 e o NumPy 2.0.2, num Apple M4. Se aparecer `No module named 'numpy'`, rode `python3 -m pip install numpy` com o mesmo `python3`.

Os tempos que esses programas imprimem são da sua máquina e mudam de uma rodada para outra. Compare a ordem com a da aula, não o número.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `parciais.py` | Lê `../dados/triatlo/api_resultados.json` e monta os arrays: `tempos` em segundos, com `nan` na parcial vazia, e `peito`, `edicao` e `status`. Resultado repetido entra uma vez. É o mesmo da aula 16. |
| `cronometro.py` | Mede o tempo de uma função com o `timeit`: várias chamadas, 5 repetições, fica o melhor tempo. |
| `volume.py` | Monta os tempos de quantos atletas você pedir, sorteando linhas dos atletas que concluíram a edição com as cinco parciais. O sorteio é sempre o mesmo. |
| `comparar.py` | A soma das parciais com loop, com array e com array começando da lista, em 5, 100, 10 mil e 1 milhão de atletas. |
| `boletim.py` | O programa do boletim, com o tempo de cada etapa e as contas nas duas versões. |
| `converter_texto.py` | A conversão das parciais de texto para segundos com loop e com `np.vectorize`. |
| `primeiro_vazio.py` | A busca da primeira parcial vazia em 1 milhão de atletas, com loop e com array. |
| `ritmo_loop.py` | O ritmo em minutos por km de cada atleta de 2025, com loop. É o programa do exercício. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 comparar.py
python3 comparar.py --n 5
python3 boletim.py
python3 converter_texto.py
python3 primeiro_vazio.py --onde inicio
python3 primeiro_vazio.py --onde fim
python3 ritmo_loop.py
python3 ritmo_loop.py --etapas
```

No Windows, troque `python3` por `py`.

O `comparar.py` sem `--n` leva uns 30 segundos: o loop com 1 milhão de atletas é medido várias vezes. O `primeiro_vazio.py` leva alguns segundos em cada caso.

O `primeiro_vazio.py` sem o `--onde` para com o código 2 e uma mensagem que diz as duas opções.

Para o exercício, crie `medir_ritmo.py` nesta pasta, ao lado do `ritmo_loop.py`, e rode:

```bash
python3 medir_ritmo.py
```

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
