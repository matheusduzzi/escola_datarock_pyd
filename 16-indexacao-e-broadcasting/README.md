# 16. Indexação e broadcasting

Os arquivos da aula «Indexação e broadcasting». Rode os comandos de dentro desta pasta. Os dados são os da competição de triatlo, que ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md), e as distâncias de cada edição estão em `../dados/triatlo/edicoes.csv`.

Você só precisa do Python com o NumPy. O NumPy vem junto quando você instala o pandas, como no README da raiz do kit. Para ver se ele está aí:

```bash
python3 -c "import numpy; print(numpy.__version__)"
```

A aula foi rodada com o NumPy 2.0.2. Se aparecer `No module named 'numpy'`, rode `python3 -m pip install numpy` com o mesmo `python3`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `parciais.py` | Lê `../dados/triatlo/api_resultados.json` e monta os arrays: `tempos` em segundos, com `nan` na parcial vazia, e `peito`, `edicao` e `status`. Resultado repetido entra uma vez. |
| `explorar.py` | Forma, tipo, as primeiras seleções e as máscaras da seção 3. |
| `atleta.py` | As parciais de um atleta como estão no arquivo e em segundos, para a conta à mão. |
| `acima_da_mediana.py` | Os minutos acima ou abaixo da mediana de cada etapa. |
| `fatia_do_tempo.py` | A fatia do tempo de cada atleta em cada etapa, com e sem o `np.newaxis`. |
| `ritmo.py` | A velocidade mediana por edição, com a distância de cada edição. |
| `formas.py` | As contas do pedido 1 da prática guiada. |
| `vista.py` | O pedido 2 da prática guiada. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 explorar.py
python3 acima_da_mediana.py
python3 acima_da_mediana.py --edicao 2025 --peito 102
python3 atleta.py --edicao 2024 --peito 102
python3 fatia_do_tempo.py
python3 fatia_do_tempo.py --errado
python3 fatia_do_tempo.py --errado --amostra 5
python3 ritmo.py
python3 ritmo.py --sem-indexar
python3 formas.py
python3 vista.py
```

No Windows, troque `python3` por `py`.

O `fatia_do_tempo.py --errado` para com `ValueError: operands could not be broadcast together with shapes (366,5) (366,)` e termina com o código 1. É de propósito: é a primeira versão da conta, no arquivo inteiro. Com `--amostra 5`, a mesma conta roda e termina com `Linhas que não somam 1: 5 de 5`.

O `ritmo.py --sem-indexar` também roda sem erro e mostra a natação de 2025 com o dobro da velocidade. É o erro da seção 6 da aula.

O `atleta.py` com um peito que não aparece na edição para com o código 2 e uma mensagem.

Para o exercício, crie `diferenca_para_o_primeiro.py` nesta pasta, ao lado do `parciais.py`, e rode:

```bash
python3 diferenca_para_o_primeiro.py
```

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
