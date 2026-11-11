# 28. Datas, fusos e séries tabulares

Os arquivos da aula «Datas, fusos e séries tabulares». Rode os comandos de dentro desta pasta. Os pedidos são os da Loja Exemplo, que ficam em `../dados/loja`. O dicionário está em [../dados/loja/LEIA-ME.md](../dados/loja/LEIA-ME.md).

Você só precisa do Python com o pandas, como no README da raiz do kit. Para ver se ele está aí:

```bash
python3 -c "import pandas; print(pandas.__version__)"
```

A aula foi rodada com o Python 3.9.6 e o pandas 2.3.3. Se aparecer `No module named 'pandas'`, rode `python3 -m pip install pandas` com o mesmo `python3`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `gerar.py` | Lê `../dados/loja/pedidos.csv` e monta os quatro arquivos de entrada da aula. Sempre escreve os mesmos arquivos. |
| `caixa_loja.csv` | Os pedidos do caixa da loja física: `id_pedido`, `data_hora` (dd/mm/aaaa HH:MM, no relógio da loja, sem fuso) e `valor`. |
| `site_pedidos.csv` | Os pedidos do site: `id_pedido`, `criado_em` (ISO 8601 em UTC, com o `Z` no fim) e `valor`. |
| `exportacoes_site.csv` | Uma linha por dia de exportação do site, em UTC: `dia_utc`, `status` (`ok` ou `falhou`) e `linhas`. |
| `entregas.csv` | As entregas da transportadora, para o exercício: `id_pedido` e `entregue_em`. |
| `datas.py` | A série diária de pedidos de cinco jeitos: o código da IA, o formato, o fuso, o calendário e o jeito certo. |
| `serie_diaria.csv` e `serie_diaria_LEIA-ME.md` | A série e as regras dela, escritas pelo `datas.py --jeito certo`. |
| `checar_serie.py` | Checa uma série diária: calendário completo, dia sem hora e sem fuso, vazio só nos dias sem dado. Você usa a função `checar` no exercício. |
| `testar_checar.py` | Estraga a série de dez jeitos e vê se o `checar_serie.py` acusa cada um. |
| `exercicio.py` | O programa do exercício. Você escreve as funções `ler_entregas` e `serie_entregas`. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 gerar.py
python3 datas.py --jeito ia
python3 datas.py --jeito formato
python3 datas.py --jeito fuso
python3 datas.py --jeito calendario
python3 datas.py --jeito certo
python3 testar_checar.py
python3 exercicio.py
```

No Windows, troque `python3` por `py`.

O `exercicio.py` para com o código 1 e a mensagem `falta escrever ler_entregas` enquanto você não escrever as duas funções. Depois de escritas, ele grava `serie_entregas.csv` e sai com 0 se o `checar_serie` disser `ok`, e com 1 se ele achar algum problema.

O `testar_checar.py` sai com 1 se o `checar_serie.py` responder errado em algum caso. Se você mexer no `checar_serie.py`, rode ele de novo.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
