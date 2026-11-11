# Entregas por cidade

Pedidos entregues e faturamento por cidade do cliente, num período de meses, para a reunião da gerente da Loja Exemplo. Uma linha da tabela é uma cidade. O faturamento soma o `valor` dos pedidos entregues; pedido sem valor anotado conta em `pedidos` e fica fora da soma.

## Do que precisa

- Python 3.9 ou mais novo.
- As bibliotecas de `requirements.txt`: pandas e python-dotenv.
- A base da Loja Exemplo (`pedidos.csv` e `clientes.csv`). No kit do curso ela fica em `../../dados/loja`.

## Como rodar

Tudo a partir desta pasta, a que tem este README.

```bash
python3 -m pip install -r requirements.txt
cp .env.exemplo .env
python3 -m entregas --inicio 2026-04 --fim 2026-06
```

No Windows, troque `python3` por `py` e `cp` por `copy`.

A saída mostra a tabela, o total e onde o CSV foi gravado:

```text
Total: 571369.12
Tabela gravada em saida/entregas-por-cidade_2026-04_a_2026-06.csv
```

Para outro período, mude só o comando: `--inicio` e `--fim` recebem o mês no formato `AAAA-MM`. Cada período grava um arquivo com o nome dele, então um não apaga o outro.

## Configuração

| Variável | Para que serve | No exemplo |
|---|---|---|
| `LOJA_DADOS` | pasta com `pedidos.csv` e `clientes.csv` | `../../dados/loja` |
| `LOJA_SAIDA` | pasta onde o CSV é gravado | `saida` |
| `LOJA_TOKEN_API` | token da API local, para as aulas de API | vazio |

Caminho relativo parte desta pasta. Se a base está em outro lugar na sua máquina, mude `LOJA_DADOS` no seu `.env`. O `.env` é seu e fica fora do Git; o `.env.exemplo` vai para o Git e nunca leva segredo.

Uma variável definida no terminal vale mais que a do `.env`. Sem o `.env`, num servidor por exemplo, defina as variáveis no terminal:

```bash
LOJA_DADOS=../../dados/loja python3 -m entregas --inicio 2026-04 --fim 2026-06
```

No PowerShell: `$env:LOJA_DADOS = "../../dados/loja"` e depois `py -m entregas --inicio 2026-04 --fim 2026-06`.

Para ver a configuração antes de rodar, acrescente `--mostrar-config`. O token aparece só como "definido" ou "vazio".

## Arquivos

| Caminho | O que faz |
|---|---|
| `entregas/__main__.py` | o comando: chama as partes na ordem |
| `entregas/config.py` | lê o período do comando e as pastas do ambiente ou do `.env` |
| `entregas/entrada.py` | lê os CSVs e para se faltar arquivo ou coluna |
| `entregas/transformacao.py` | as regras: entregues no período, soma por cidade |
| `entregas/saida.py` | mostra a tabela e grava o CSV em `saida/` |

## Quando dá erro

| Mensagem | O que fazer |
|---|---|
| `LOJA_DADOS não está definida` | copie `.env.exemplo` para `.env` ou defina a variável no terminal |
| `achei o .env, mas falta o python-dotenv` | rode `python3 -m pip install -r requirements.txt` |
| `não achei pedidos.csv em ...` | veja se `LOJA_DADOS` aponta para a pasta da base |
| `No module named entregas` | rode o comando desta pasta, com `-m entregas` |
| `--inicio precisa ser AAAA-MM` | escreva o mês com quatro dígitos de ano e dois de mês |
