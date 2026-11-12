# 20. Índice, alinhamento e tipos anuláveis

Os arquivos da aula «Índice, alinhamento e tipos anuláveis». Rode os comandos de dentro desta pasta. Os dados são os da competição de triatlo, que ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md).

Você precisa do Python com o pandas, como no README da raiz do kit. Para ver a versão:

```bash
python3 -c "import pandas; print(pandas.__version__)"
```

A aula foi rodada com o Python 3.9.6 e o pandas 2.3.3. Com o pandas 3, que exige Python 3.11 ou mais novo, a coluna de texto aparece com o tipo `str` em vez de `object`. O kit não foi rodado no pandas 3: se você usar ele, olhe os tipos que o `tipos.py` imprime antes de comparar com a aula.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `resultados.py` | Lê `../dados/triatlo/api_resultados.json` numa tabela, com o `id_atleta` de cada inscrição e as parciais em segundos. Mantém as cópias que a API repete. Os outros programas usam o `ler()` dele. |
| `ia.py` | As duas versões que a IA mandou para comparar o ciclismo, e quem cada linha pôs lado a lado. |
| `por_atleta.py` | A mesma comparação com o índice no `id_atleta`, com e sem as cópias, e de onde vem cada vazio. |
| `tipos.py` | Como o pandas guarda o vazio: `float64` e `Int64`, a contagem de quem melhorou, o filtro com vazio e o tipo do texto no pandas 3. |
| `prever.py` | Os três pedidos da prática guiada. |
| `exercicio.py` | Os cinco casos do exercício, de A a E. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 ia.py
python3 por_atleta.py
python3 tipos.py
python3 prever.py 1
python3 prever.py 2
python3 prever.py 3
python3 exercicio.py A
```

Troque o `A` por `B`, `C`, `D` e `E` para os outros casos. Escreva a sua previsão na folha antes de rodar cada um. No Windows, troque `python3` por `py`.

O `prever.py` e o `exercicio.py` sem número ou letra param com uma mensagem que diz as opções.

Para o exercício, crie `corrida_duas.py` nesta pasta, ao lado do `resultados.py`, e rode:

```bash
python3 corrida_duas.py
```

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
