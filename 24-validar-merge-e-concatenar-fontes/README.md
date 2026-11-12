# 24. Validar merge e concatenar fontes

Os arquivos da aula «Validar merge e concatenar fontes». Rode os comandos de dentro desta pasta. Os dados da competição de triatlo ficam em `../dados/triatlo`, com o dicionário em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md). As planilhas do posto de chegada ficam em `posto/`, com o dicionário em [posto/LEIA-ME.md](posto/LEIA-ME.md).

Você só precisa do Python com o pandas, como no README da raiz do kit. Para ver se ele está aí:

```bash
python3 -c "import pandas; print(pandas.__version__)"
```

A aula foi rodada com o Python 3.9.6 e o pandas 2.3.3. Se aparecer `No module named 'pandas'`, rode `python3 -m pip install pandas` com o mesmo `python3`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `reconciliar.py` | Junta a planilha do posto de 2025 aos resultados da API, um passo de cada vez, e mostra se as contas de linhas e de valores fecham. As funções dele servem para o exercício. |
| `posto/posto_2025.csv` e `posto/posto_2024.csv` | As planilhas do posto de chegada, como os fiscais mandaram. A de 2024 é do exercício. |
| `gerar_posto.py` | Escreve as duas planilhas de novo, sempre iguais. Só usa a biblioteca padrão. |
| `reconciliacao.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 reconciliar.py --passo caio
python3 reconciliar.py --passo copias
python3 reconciliar.py --passo peito
python3 reconciliar.py --passo empilhar
python3 reconciliar.py --passo sobreposicao
python3 reconciliar.py --passo base
```

No Windows, troque `python3` por `py`.

O passo `base` faz tudo em ordem e imprime as contas. Se uma conta não fecha, ele para com o código 1 e diz qual foi. Ele também para com o código 1 se a API ou as inscrições tiverem duas versões diferentes da mesma chave, ou se a planilha do posto vier sem uma das colunas esperadas.

## As funções, para o exercício

```bash
python3 -c "from reconciliar import *; t = carregar(); posto, conflitos = copias(ler_posto(2024), ['edicao', 'peito'], 'posto 2024')"
```

| Função | O que faz |
|---|---|
| `carregar()` | Retorna um dicionário com `inscricoes` (as duas edições, como chegam) e `resultados` (a API, como chega). |
| `ler_posto(edicao)` | Lê a planilha do posto daquela edição, como chegou. |
| `copias(tabela, chave, nome)` | Retorna a tabela sem as cópias e as linhas com versões diferentes da mesma chave. Cópia igual conta uma vez. Versões diferentes saem inteiras da primeira tabela. |
| `achar_inscricao(posto, inscricoes)` | Põe o `id_inscricao` em cada linha do posto, pela edição e pelo peito, e troca os nomes das colunas para os da API. Retorna as linhas com inscrição e as sem inscrição. |
| `empilhar(api, posto)` | Empilha as duas tabelas com a coluna `fonte`. Para se as colunas não forem as mesmas. |
| `sobreposicao(empilhada)` | Retorna as chaves que estão nas duas fontes, lado a lado: as iguais e as diferentes. |
| `valores(resultados)` | Quantos de cada status e a soma do tempo oficial de quem concluiu, em segundos, por edição. |
| `montar_base(inscricoes, resultados)` | A base, uma linha por inscrição, com `how="left"`, `validate="one_to_one"` e a coluna `_merge`. |

Se o `reconciliar.py` não achar os dados, ele para com o código 2 e diz qual arquivo faltou: rode de dentro desta pasta, no kit do curso. Sem `--passo`, ou com um passo que não existe, ele também para com o código 2 e mostra as opções.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
