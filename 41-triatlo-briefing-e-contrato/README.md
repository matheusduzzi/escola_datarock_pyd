# 41. Triatlo: briefing e contrato

O começo do projeto final. Antes de juntar arquivos e fazer gráfico, você escreve o que cada palavra quer dizer e como cada número vai ser contado.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `briefing-da-bia.md` | O pedido da Bia, que organiza a competição. É o caso da aula. |
| `explorar.py` | Uma primeira olhada nos dados: linhas, chaves, repetidos, status e tempos vazios. Não grava nada. |
| `folha-do-contrato.md` | A folha que você preenche: o dicionário e as perguntas, cada uma com o seu denominador. |
| `mensagem-da-livia.md` | As quatro perguntas da comissão técnica. É o exercício. |

Os dados ficam na base compartilhada do kit, em `../dados/triatlo/`. O dicionário das colunas está em `../dados/triatlo/LEIA-ME.md`.

## Do que você precisa

Python 3.9 ou mais novo com o pandas, o mesmo ambiente do diagnóstico. Rode de dentro dessa pasta:

```bash
python3 explorar.py
```

A saída começa com `== 1. Linhas e chaves de cada arquivo` e tem nove partes. A primeira linha da parte 1 é:

```text
atletas.csv          linhas= 700  id_atleta diferentes= 700
```

Se aparecer `FileNotFoundError`, você não está dentro da pasta da aula, ou a pasta `dados` do kit não está ao lado dela. No Windows, troque `python3` por `py`.

Nessa aula os resultados são lidos direto do arquivo `api_resultados.json`, que é o que a API local serve. Na aula 42, «Triatlo: integração e qualidade», eles passam a vir pela API.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
