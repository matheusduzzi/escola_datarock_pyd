# 06. Refatorar uma análise

Os arquivos da aula «Refatorar uma análise». Rode os comandos de dentro desta pasta. Os dados são os da Loja Exemplo, que ficam em `../dados/loja`. O dicionário das tabelas está em [../dados/loja/LEIA-ME.md](../dados/loja/LEIA-ME.md).

Você só precisa do Python com o pandas, como no resto do curso. Se o pandas ainda não está instalado, veja o README da raiz do kit. Os notebooks abrem no Jupyter ou no VS Code, mas nenhum comando abaixo precisa deles: o `sessao_limpa.py` roda um notebook pelo terminal.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `faturamento-do-semestre.ipynb` | O notebook do Caio, com os números `In` e as saídas salvas do dia em que ele rodou. |
| `faturamento.py` | As regras do relatório do semestre, uma função por passo. |
| `relatorio.py` | O comando que monta o relatório do semestre e grava `saida/faturamento.csv`. |
| `faturamento-refatorado.ipynb` | O notebook depois da refatoração: só importa o módulo e chama as funções. |
| `sessao_limpa.py` | Roda um script ou notebook do zero, num Python novo e numa cópia limpa da pasta, duas vezes, e diz se as duas saídas batem. |
| `ticket-por-cidade.ipynb` | O notebook do exercício. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 sessao_limpa.py faturamento-do-semestre.ipynb
python3 relatorio.py
python3 relatorio.py --inicio 2026-04 --fim 2026-06
python3 sessao_limpa.py relatorio.py
python3 sessao_limpa.py faturamento-refatorado.ipynb
python3 sessao_limpa.py ticket-por-cidade.ipynb
```

No Windows, troque `python3` por `py`.

O primeiro comando para na célula 3 com `NameError: name 'produtos' is not defined` e termina com o código 1. É de propósito: é o notebook do Caio rodando do zero. O mesmo acontece com o notebook do exercício, numa célula diferente.

O `relatorio.py` sem opções mostra `Total: 1127501.18`, o semestre inteiro. As opções `--inicio` e `--fim` recebem o mês no formato `AAAA-MM`; um mês escrito de outro jeito faz o programa parar com o código 2 e uma mensagem, sem gravar nada.

O `sessao_limpa.py` termina com o código 0 quando as duas execuções terminam bem e batem, 1 quando a execução para com erro e 3 quando a saída muda de uma execução para a outra. Ele não mexe na sua pasta: tudo roda numa cópia temporária, que é apagada no fim. A pasta `saida/` que aparece aqui é a do `relatorio.py` rodado direto.

Para o exercício, crie `ticket.py` e `relatorio_ticket.py` nesta pasta e rode:

```bash
python3 sessao_limpa.py relatorio_ticket.py
```

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
