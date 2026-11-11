# 05. Funções, escopo e contratos

Os arquivos da aula «Funções, escopo e contratos». Rode os comandos de dentro desta pasta. Os pedidos vêm de `../dados/loja`; o dicionário das tabelas está em [../dados/loja/LEIA-ME.md](../dados/loja/LEIA-ME.md).

Os programas dessa aula só usam a biblioteca padrão do Python 3.9 ou mais novo. O pandas só aparece na conta de maio da aula e na contagem do exercício, e é o mesmo que você instalou para o curso.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `ticket.py` | O ticket médio do mês do Caio, como ele deixou. |
| `ticket_contrato.py` | O ticket médio depois da aula: ler, calcular e mostrar em três funções, com o contrato no docstring. |
| `casos_ticket.py` | Os nove casos de fronteira do `resumo_do_mes`. |
| `prever_escopo.py` | Pedido 1 da prática guiada: nomes locais, globais e lista como valor padrão. |
| `separar_cancelados.py` | Pedido 2 da prática guiada: uma função para você escrever o contrato. |
| `semana.py` | Pedido 3 da prática guiada: a semana do mês das datas que você passar no comando. |
| `voltaram.py` | A função do exercício, como o Caio deixou. |
| `casos_voltaram.py` | Roda os casos de fronteira do exercício. Tem um caso de exemplo; os outros você escreve. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 ticket.py
python3 ticket_contrato.py
python3 casos_ticket.py
python3 prever_escopo.py
python3 separar_cancelados.py
python3 semana.py 2026-05-01 2026-05-07
python3 voltaram.py
python3 casos_voltaram.py voltaram
```

No Windows, troque `python3` por `py`.

O `ticket.py` roda sem erro e mostra o ticket de maio duas vezes. É de propósito: a aula começa por aí. O `ticket_contrato.py` mostra maio e junho; com meses no fim do comando, mostra esses meses (`python3 ticket_contrato.py 2026-07`).

No `prever_escopo.py` e no `separar_cancelados.py`, escreva a sua resposta antes de rodar. No `semana.py`, troque as datas do comando pelas suas. As respostas estão na aula.

O `voltaram.py` roda sem erro. O `casos_voltaram.py voltaram` termina com 1 falha, a do caso de exemplo: é o ponto de partida do exercício. Quando você tiver o `voltaram_novo.py`, rode `python3 casos_voltaram.py voltaram_novo`.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
