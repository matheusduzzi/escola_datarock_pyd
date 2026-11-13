# 35. Como testar transformações

Os arquivos da aula «Como testar transformações». Rode os comandos de dentro desta pasta. Os dados são os da competição de triatlo, que ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md).

Você só precisa do Python 3.9 ou mais novo. Os três programas usam só a biblioteca padrão: não precisa do pandas nem de biblioteca de testes. O pytest entra na próxima aula, «Escrever testes de dados e funções». A aula foi rodada com o Python 3.9.6.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `regras.py` | As regras de transformação do projeto: `segundos`, `categoria`, `soma_parciais`, `consolidar` e `juntar`, cada uma com o comentário do que promete. Também tem `ler_dados`, que lê os arquivos do triatlo como eles vêm. |
| `defeitos.py` | Versões com defeito das regras. D1 a D7 são das três regras da aula. E1 a E6 são das duas regras do exercício. |
| `sondar.py` | Roda o plano de testes da aula contra as regras certas ou contra um defeito, e monta a matriz de quem pega cada defeito. |
| `plano-de-testes.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 sondar.py
python3 sondar.py --caio
python3 sondar.py --defeito D3
python3 sondar.py --matriz
python3 sondar.py --defeitos
```

O primeiro roda os 25 testes do plano da aula e termina com quantos passaram. Com `--defeito`, ele troca uma regra pela versão com defeito antes de rodar. Quando algum teste falha, o `sondar.py` sai com o código 1: é o que acontece de propósito com `--defeito D3`.

No Windows, troque `python3` por `py`.

Para as contas do exercício, use as regras direto no Python. Este comando conta os itens da API, os resultados depois de `consolidar` e as linhas depois de `juntar`:

```bash
python3 -c "from regras import *; a, i, r = ler_dados(); print(len(r), len(consolidar(r)), len(i), len(juntar(i, r)))"
```

E este conta os status depois de `juntar`, por edição:

```bash
python3 -c "from collections import Counter; from regras import *; a, i, r = ler_dados(); print(Counter((x['edicao'], x['status']) for x in juntar(i, r)))"
```

Os defeitos E1 a E6 são para você raciocinar sobre o plano. O `sondar.py` não roda o seu plano: com `--defeito E3`, ele para com o código 2 e avisa que esse plano é o que você escreve. Com um defeito que não existe, como `--defeito D9`, ele também para com o código 2 e mostra como listar os defeitos. Se ele não achar os dados, para com o código 2 e diz qual arquivo faltou: rode de dentro desta pasta, no kit do curso.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
