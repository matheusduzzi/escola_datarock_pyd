# 18. Agregações e estabilidade numérica

Os arquivos da aula «Agregações e estabilidade numérica». Rode os comandos de dentro desta pasta. Os dados são os da competição de triatlo, que ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md).

Você precisa do Python com o NumPy e o pandas, como no README da raiz do kit. Para ver as versões:

```bash
python3 -c "import numpy, pandas; print(numpy.__version__, pandas.__version__)"
```

A aula foi rodada com o NumPy 2.0.2 e o pandas 2.3.3. Se aparecer `No module named 'numpy'`, rode `python3 -m pip install pandas` com o mesmo `python3`: o NumPy vem junto.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `parciais.py` | Lê `../dados/triatlo/api_resultados.json` e monta os arrays: `tempos` em segundos, com `nan` na parcial vazia, `oficial` (o tempo oficial em segundos), `peito`, `edicao` e `status`. Resultado repetido entra uma vez. |
| `volume.py` | Monta 1 milhão de linhas a partir dos tempos de 2024, o mesmo da aula «Vetorização e custo». |
| `vazios.py` | As parciais vazias de 2025 por status. |
| `media.py` | A média de cada etapa com `np.mean`, `np.nanmean` e com o vazio trocado por zero. |
| `quadro.py` | O quadro de 2025: n, média, mediana, desvio, mínimo e máximo. |
| `conferir.py` | A soma das médias das etapas contra a média do tempo oficial, com `==` e com tolerância. |
| `decimais.py` | Somas de decimais que dependem da ordem. |
| `volume32.py` | A soma de 1 milhão de horas em `float64` e em `float32`. |
| `pequeno.py` | O pedido 1 da prática guiada. |
| `tolerancia.py` | O pedido 2 da prática guiada. |
| `desvio.py` | O pedido 3 da prática guiada. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 vazios.py
python3 media.py
python3 media.py --concluiu
python3 quadro.py
python3 conferir.py --nanmean
python3 conferir.py
python3 conferir.py --sem 109
python3 decimais.py
python3 volume32.py
python3 pequeno.py
python3 tolerancia.py
python3 desvio.py
```

No Windows, troque `python3` por `py`.

O `media.py` mostra `nan` na linha do `np.mean` de propósito: é a primeira versão do quadro, com os vazios dentro. O `pequeno.py` mostra um `RuntimeWarning` de propósito, o aviso do `np.nanmean` quando não sobra nenhum valor. Os dois terminam sem erro.

O `volume32.py` monta 1 milhão de linhas e leva alguns segundos.

Para o exercício, crie `quadro_2024.py` nesta pasta, ao lado do `parciais.py`, e rode:

```bash
python3 quadro_2024.py
```

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
