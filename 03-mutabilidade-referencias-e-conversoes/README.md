# 03. Mutabilidade, referências e conversões

Os arquivos da aula «Mutabilidade, referências e conversões». Rode os comandos de dentro desta pasta. O catálogo de produtos, os pedidos e o cadastro de clientes vêm de `../dados/loja`; o dicionário das tabelas está em [../dados/loja/LEIA-ME.md](../dados/loja/LEIA-ME.md).

Os programas dessa aula só usam a biblioteca padrão do Python 3.9 ou mais novo. O pandas só aparece na parte 6 do «Por dentro» e na contagem do exercício, e é o mesmo que você instalou para o curso.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `promocao.py` | A simulação da promoção de julho do Caio, como ele deixou. |
| `promocao_corrigido.py` | A simulação depois da aula: converte o preço na leitura e monta um catálogo novo. |
| `prever_listas.py` | Pedido 1 da prática guiada: lista dentro de dicionário, cópia, `+=` e `+`. |
| `prever_funcoes.py` | Pedido 2 da prática guiada: funções que recebem uma lista, e uma tupla com lista dentro. |
| `prever_conversoes.py` | Pedido 3 da prática guiada: `int`, `float`, `str`, `bool` e `round`. |
| `campanha.py` | O programa do exercício. |
| `amostra.csv` | Seis pedidos da base, para você prever a saída do exercício à mão. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 promocao.py
python3 promocao_corrigido.py
python3 prever_listas.py
python3 prever_funcoes.py
python3 prever_conversoes.py
python3 campanha.py --pedidos amostra.csv
```

No Windows, troque `python3` por `py`.

O `promocao.py` mostra a tabela com as duas colunas iguais e para com um `TypeError`. É de propósito: a aula começa por aí. O `promocao_corrigido.py` mostra o preço de hoje e o da promoção e os três produtos mais baratos.

Nos três `prever_`, escreva o que cada `print` vai mostrar antes de rodar. As respostas estão na aula.

O `campanha.py` roda sem erro. O exercício pede que você escreva na folha o que ele vai mostrar antes de rodar o comando.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
