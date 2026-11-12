# 23. Junções e contratos de cardinalidade

Os arquivos da aula «Junções e contratos de cardinalidade». Rode os comandos de dentro desta pasta. Os dados são os da competição de triatlo, que ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md).

Você só precisa do Python com o pandas, como no README da raiz do kit. Para ver se ele está aí:

```bash
python3 -c "import pandas; print(pandas.__version__)"
```

A aula foi rodada com o Python 3.9.6 e o pandas 2.3.3. Se aparecer `No module named 'pandas'`, rode `python3 -m pip install pandas` com o mesmo `python3`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `medir.py` | Mede a chave de um merge antes de juntar: quantas vezes ela aparece de cada lado, quantas chaves têm par em cada lado, o `validate` mais exigente que os dados passam e quantas linhas saem com `inner`, `left` e `outer`. Lê as tabelas como chegam nos arquivos, com as linhas repetidas. |
| `contratos.md` | A folha do exercício, com o contrato do merge principal como exemplo. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 medir.py --merge peito
python3 medir.py --merge resultados
python3 medir.py --merge validar
```

No Windows, troque `python3` por `py`.

Para medir outro merge, use as funções no Python. A `carregar()` retorna um dicionário com as tabelas `inscricoes` (as duas edições, com a coluna `edicao`), `resultados`, `atletas` e `edicoes`. A `medir(esquerda, direita, chave, nome_esquerda, nome_direita)` imprime as contas. A chave pode ser uma coluna ou uma lista de colunas.

```bash
python3 -c "from medir import carregar, medir; t = carregar(); medir(t['resultados'], t['inscricoes'], ['edicao', 'id_inscricao'], 'resultados', 'inscricoes')"
```

Se o `medir.py` não achar os dados, ele para com o código 2 e diz qual arquivo faltou: rode de dentro desta pasta, no kit do curso. Sem `--merge`, ou com um merge que não existe, ele também para com o código 2 e mostra as opções.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
