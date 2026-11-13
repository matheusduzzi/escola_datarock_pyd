# 39. Reproduzir em ambiente limpo

Os arquivos da aula «Reproduzir em ambiente limpo». Rode os comandos de dentro desta pasta.

| Arquivo | Para que serve |
|---|---|
| `tempos-por-etapa/` | O projeto do Caio, do jeito que ele mandou para a Lívia. Ele tem problemas de propósito: é o que a aula e o exercício acham. |
| `registro.py` | Segue o README de um projeto numa cópia limpa e escreve o registro de execução. Só usa a biblioteca padrão e não instala nada. |
| `registro-de-execucao.md` | A folha do exercício. Salve uma cópia com o seu nome. |
| `gerar_resultados.py` | Gera de novo `tempos-por-etapa/dados/resultados.csv`, igual byte a byte. Você não precisa rodar: o arquivo já vem pronto. |

A aula foi rodada com o Python 3.9.6 no macOS. No Windows, troque `python3` por `py` e `.venv/bin/python` por `.venv\Scripts\python.exe`.

## Antes de começar

Guarde uma cópia da pasta `tempos-por-etapa` do jeito que veio. Você vai mexer nela no exercício, e a aula compara com a original.

## Preparar o ambiente do projeto

O ambiente fica dentro da pasta do projeto, como o README dele manda. Crie e instale assim, de dentro desta pasta:

```bash
python3 -m venv tempos-por-etapa/.venv
tempos-por-etapa/.venv/bin/python -m pip install -r tempos-por-etapa/requirements-dev.txt
```

A lista `requirements-dev.txt` foi travada no Python 3.9.6 do macOS. Se o seu Python é outro, o pip pode escolher outras versões ou parar na instalação. Anote o que aconteceu: isso entra no registro. O exercício diz o que fazer nesse caso.

## Rodar o registro

Sempre com o Python do ambiente do projeto, não com o `python3` do sistema:

```bash
tempos-por-etapa/.venv/bin/python registro.py tempos-por-etapa
tempos-por-etapa/.venv/bin/python registro.py tempos-por-etapa --como-windows
tempos-por-etapa/.venv/bin/python registro.py tempos-por-etapa --salvar meu-registro.md
```

O `registro.py` copia o projeto para uma pasta temporária, sem o que o `.gitignore` tira, que é o que o Git levaria. Depois lê o bloco de comandos da seção "Como rodar" do README do projeto. No passo do `pip install -r`, ele compara o que está instalado com a lista. Os outros comandos de Python ele roda na cópia, um por um, e mostra o código de saída e as últimas linhas, mesmo depois de um passo falhar. Uma linha que não é de Python, como `cp`, ele não roda e não diz que reproduziu. A pasta do projeto não muda.

Com `--como-windows`, o `open()` passa a ler arquivos em cp1252 quando o código não diz a codificação. É o que costuma acontecer no Windows em português até o Python 3.14. A opção imita só isso: o Python e os pacotes continuam os do seu ambiente.

O registro termina com o código 0 e a linha `resultado: reproduziu` quando todos os passos passam e o ambiente bate com a lista. Termina com 1 quando algum passo falha ou o ambiente não bate. Se a pasta, o README ou a seção "Como rodar" não existir, termina com 2 e diz o que não achou.

O `.gitignore` do projeto é lido numa versão curta das regras do Git: nomes, pastas terminadas em `/`, curingas como `*.csv` e linhas com `!`. Num projeto real, a cópia limpa de verdade é um `git clone` numa pasta nova.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
