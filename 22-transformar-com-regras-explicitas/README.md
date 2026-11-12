# 22. Transformar com regras explícitas

Os arquivos da aula «Transformar com regras explícitas». Rode os comandos de dentro desta pasta. A aula usa a base da Loja Exemplo, em `../dados/loja`, e o exercício usa o cadastro de atletas do triatlo, em `../dados/triatlo`. Os dicionários estão em [../dados/loja/LEIA-ME.md](../dados/loja/LEIA-ME.md) e [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md).

Você só precisa do Python com o pandas, como no README da raiz do kit. Para ver se ele está aí:

```bash
python3 -c "import pandas; print(pandas.__version__)"
```

A aula foi rodada com o Python 3.9.6 e o pandas 2.3.3. Se aparecer `No module named 'pandas'`, rode `python3 -m pip install pandas` com o mesmo `python3`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `gerar.py` | Lê `../dados/loja` e `../dados/triatlo` e monta os três arquivos de entrada da aula. Sempre escreve os mesmos arquivos. |
| `pedidos_caixa.csv` | A exportação do caixa do primeiro semestre, como saiu do sistema: as colunas de `pedidos.csv` da base da loja, com o status escrito de vários jeitos e dois dias reenviados. |
| `fechamento_financeiro.csv` | O fechamento do financeiro, mês a mês: `mes`, `pedidos_entregues` e `receita`. |
| `inscricoes_2026.csv` | A lista de inscrições de 2026 do triatlo, para o exercício: `id_inscricao`, `id_atleta`, `sexo`, `ano_nascimento`, `categoria`, `valor_pago` e `cortesia`. |
| `pipeline.py` | A `Etapa` (tipo, nome, função, colunas que muda e motivo), o `rodar`, que roda as etapas, checa o tipo de cada uma e conta o que ela fez, e o `mostrar`, que imprime as contagens. |
| `loja.py` | A receita do semestre de sete jeitos: o código da IA, a limpeza, a regra, a imputação, a ordem, o pipeline certo e a decisão da gerente do pedido 3. |
| `contagens.csv` | As contagens do pipeline da loja, escritas pelo `loja.py --jeito certo`. |
| `pequeno.py` | As quatro etapas da loja numa tabela de seis pedidos (pedido 1). |
| `testar_pipeline.py` | Estraga as etapas da loja de dez jeitos e vê se o `pipeline.rodar` acusa cada um (pedido 2). |
| `exercicio.py` | O programa do exercício. Você escreve a função `montar_etapas`. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 gerar.py
python3 loja.py --jeito ia
python3 loja.py --jeito limpeza
python3 loja.py --jeito regra
python3 loja.py --jeito imputacao
python3 loja.py --jeito ordem
python3 loja.py --jeito certo
python3 pequeno.py
python3 testar_pipeline.py
python3 loja.py --jeito gerente
python3 exercicio.py
```

No Windows, troque `python3` por `py`.

O `exercicio.py` para com o código 1 e a mensagem `falta escrever montar_etapas` enquanto você não escrever a função. Depois de escrita, ele grava `contagens_inscricoes.csv` e sai com 0 se todas as etapas passarem nas checagens do `pipeline.rodar`, e com 1 se alguma parar. A mensagem diz qual etapa parou e por quê.

O `testar_pipeline.py` sai com 1 se o `pipeline.rodar` responder errado em algum caso. Se você mexer no `pipeline.py`, rode ele de novo.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
