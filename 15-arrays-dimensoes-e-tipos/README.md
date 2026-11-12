# 15. Arrays, dimensões e tipos

Os arquivos da aula «Arrays, dimensões e tipos». Rode os comandos de dentro desta pasta. Os dados são os da competição de triatlo, que ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md).

Você só precisa do Python com o NumPy. O NumPy vem junto quando você instala o pandas, como no README da raiz do kit. Para ver se ele está aí:

```bash
python3 -c "import numpy; print(numpy.__version__)"
```

A aula foi rodada com o NumPy 2.0.2. Algumas regras de tipo mudaram no NumPy 2: com uma versão 1.x, o pedido 2 da prática guiada sai diferente. Se aparecer `No module named 'numpy'`, rode `python3 -m pip install numpy` com o mesmo `python3`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `parciais.py` | Lê `../dados/triatlo/api_resultados.json` e monta os arrays: `tempos` em segundos, com `nan` na parcial vazia, e `peito`, `edicao`, `status` e as parciais em `texto`. Resultado repetido entra uma vez. |
| `site_do_caio.py` | A versão do Caio, com os tempos em `int16`: a seção 1 da aula. |
| `explorar.py` | Forma, dimensões, tamanho e tipo dos arrays, e o tipo que sai de valores misturados. |
| `dimensoes.py` | A forma de cada pedaço dos tempos, e o `reshape` que não fecha a conta. |
| `memoria.py` | Bytes, `strides`, o que usa os mesmos números e a lista de listas. Com `--linhas N`, a estimativa para N linhas. |
| `prever.py` | O pedido 1 da prática guiada. |
| `limites.py` | O pedido 2 da prática guiada. |
| `tamanhos.py` | O pedido 3 da prática guiada. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 site_do_caio.py
python3 explorar.py
python3 dimensoes.py
python3 memoria.py
python3 memoria.py --linhas 1000000
python3 prever.py
python3 limites.py
python3 tamanhos.py
```

No Windows, troque `python3` por `py`.

O `site_do_caio.py` mostra o aviso `invalid value encountered in cast` e termina sem erro. É de propósito: é a conversão do `nan` para `int16`. Na máquina em que a aula foi rodada, o `nan` virou 0.

O `limites.py` mostra dois `OverflowError` na saída e termina sem erro: os erros fazem parte da resposta do pedido 2.

Para o exercício, crie `pacote_do_site.py` nesta pasta, ao lado do `parciais.py`, e rode:

```bash
python3 pacote_do_site.py
```

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
