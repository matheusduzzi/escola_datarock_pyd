# 27. Pivot, melt e reconstrução

Os arquivos da aula «Pivot, melt e reconstrução». Rode os comandos de dentro desta pasta. Os dados são os da competição de triatlo, que ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md).

Você só precisa do Python com o pandas, como no README da raiz do kit. Para ver se ele está aí:

```bash
python3 -c "import pandas; print(pandas.__version__)"
```

A aula foi rodada com o Python 3.9.6 e o pandas 2.3.3. Se aparecer `No module named 'pandas'`, rode `python3 -m pip install pandas` com o mesmo `python3`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `tabelas.py` | Lê `../dados/triatlo/api_resultados.json`, tira as cópias iguais e escreve `resultados_largo.csv`: uma linha por resultado, uma coluna por etapa, mais o status, o peito e o tempo oficial, tudo em segundos. Os outros programas usam as funções dele. |
| `resultados_largo.csv` | A saída do `tabelas.py`, para abrir também numa planilha. |
| `conferir.py` | A conferência de ida e volta: compara a tabela de onde você saiu com a que voltou e diz o que mudou. Você usa a função `ida_e_volta` nos seus programas. |
| `testar_conferir.py` | Estraga a tabela de nove jeitos e vê se o `conferir.py` acusa cada um. |
| `ida_e_volta.py` | Leva a tabela larga para a longa e volta, de cinco jeitos, e roda a conferência em cada um. |
| `historico.py` | Monta `historico_largo.csv`, a planilha do histórico dos atletas do exercício. |
| `historico_largo.csv` | Uma linha por atleta e uma coluna por etapa e edição (`natacao_2024`, ..., `corrida_2025`), em segundos. |
| `exercicio.py` | O programa do exercício. Você escreve as funções `para_longo` e `para_largo`. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 tabelas.py
python3 ida_e_volta.py --jeito certo
python3 ida_e_volta.py --jeito sem-id
python3 ida_e_volta.py --jeito sem-vazio
python3 ida_e_volta.py --jeito reconstruir
python3 ida_e_volta.py --jeito oficial-pela-soma
python3 testar_conferir.py
python3 historico.py
python3 exercicio.py
```

No Windows, troque `python3` por `py`.

O `exercicio.py` para com o código 1 e a mensagem `falta escrever para_longo` enquanto você não escrever as duas funções. Depois de escritas, ele sai com 0 se a ida e volta der igual e com 1 se der diferente.

O `testar_conferir.py` sai com 1 se o `conferir.py` responder errado em algum caso. Se você mexer no `conferir.py`, rode ele de novo.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
