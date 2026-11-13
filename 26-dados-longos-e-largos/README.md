# 26. Dados longos e largos

Os arquivos da aula «Dados longos e largos». Rode os comandos de dentro desta pasta. Os dados são os da competição de triatlo, que ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md), e as distâncias e a temperatura de cada edição estão em `../dados/triatlo/edicoes.csv`.

Você só precisa do Python com o pandas, como no README da raiz do kit. Para ver se ele está aí:

```bash
python3 -c "import pandas; print(pandas.__version__)"
```

A aula foi rodada com o Python 3.9.6 e o pandas 2.3.3. Se aparecer `No module named 'pandas'`, rode `python3 -m pip install pandas` com o mesmo `python3`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `tabelas.py` | Lê `../dados/triatlo/api_resultados.json` e escreve as parciais nos dois formatos, em segundos. Os resultados entram como chegam no arquivo, com os repetidos. Parcial vazia fica vazia. |
| `parciais_largo.csv` | Uma linha por resultado, uma coluna por etapa. É a saída do `tabelas.py`. |
| `parciais_longo.csv` | Uma linha por resultado e etapa, com a etapa na coluna `etapa` e o tempo em `segundos`. É a saída do `tabelas.py`. |
| `chave.py` | Diz se um conjunto de colunas é chave de um arquivo: uma linha para cada combinação. Se não for, mostra as combinações repetidas e diz se as cópias são iguais. |
| `pivotar.py` | Leva o longo de 2025 para o largo de cinco jeitos e mostra o que cada um faz com uma inscrição repetida, um DNF e um DNS. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 tabelas.py
python3 chave.py parciais_largo.csv edicao id_inscricao
python3 chave.py parciais_longo.csv edicao id_inscricao etapa
python3 chave.py parciais_largo.csv numero_peito
python3 chave.py parciais_largo.csv edicao numero_peito
python3 chave.py ../dados/triatlo/inscricoes_2025.csv id_inscricao
python3 pivotar.py --jeito pivot
python3 pivotar.py --jeito media
python3 pivotar.py --jeito soma
python3 pivotar.py --jeito sem-repetidos
python3 pivotar.py --jeito peito
```

No Windows, troque `python3` por `py`.

O `pivotar.py --jeito pivot` para de propósito com o código 1 e a mensagem `ValueError: Index contains duplicate entries, cannot reshape`. É o erro que a aula explica na seção 5.

O `chave.py` com um arquivo ou uma coluna que não existe para com o código 2 e diz o que faltou. Os nomes das colunas são os da primeira linha do arquivo.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
