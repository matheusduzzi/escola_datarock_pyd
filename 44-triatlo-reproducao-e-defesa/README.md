# 44. Triatlo: reprodução e defesa

A última parte do projeto final. O balanço das aulas 42 e 43 vira um projeto só, que roda com um comando. Você roda esse projeto num ambiente limpo, compara o que saiu com o que foi enviado para a federação e defende cada escolha e cada falha com uma prova que outra pessoa consegue repetir.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `balanco-triatlo/` | O projeto do jeito que o Caio montou: o código das aulas 42 e 43, os dados, a API local, os testes, o `balanco.py` e o `conferir.py`. Veja o [README do projeto](balanco-triatlo/README.md). |
| `relatorio-enviado.md` | O relatório que a Bia mandou para a federação. É com ele que o Rafael vai comparar. |
| `perguntas-do-rafael.md` | O pedido do exercício: as quatro perguntas da federação. |
| `defesa.md` | A folha da defesa, para você preencher no exercício. |

O registro de execução é o `registro.py` da aula 39, «Reproduzir em ambiente limpo». Ele fica na pasta daquela aula, `../39-reproduzir-em-ambiente-limpo/`.

## Do que você precisa

O Python 3.9 ou mais novo e as bibliotecas da lista travada do projeto, `balanco-triatlo/requirements-dev.txt`: pandas, Matplotlib e pytest, com a versão exata de cada um. A aula foi rodada com o Python 3.9.6 no macOS, o pandas 2.3.3, o Matplotlib 3.9.4 e o pytest 8.4.2. Não precisa de internet: a API é a local, e o `balanco.py` sobe e desliga essa API sozinho.

## Rodar o projeto

O ambiente limpo é um venv novo, só com a lista travada. De dentro da pasta `balanco-triatlo`:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python balanco.py
.venv/bin/python conferir.py
.venv/bin/python -m pytest -q testes
```

No Windows, troque `python3` por `py` e `.venv/bin/python` por `.venv\Scripts\python.exe`.

O `balanco.py` leva uns 15 segundos. O projeto como veio termina o `conferir.py` com `3 de 4 iguais: não reproduziu`, código 1, e os testes com `34 passed`. A seção 4 da aula mostra por quê.

## O registro em ambiente limpo

Volte para esta pasta, a da aula, e rode o registro com o Python do ambiente do projeto:

```bash
cd ..
balanco-triatlo/.venv/bin/python ../39-reproduzir-em-ambiente-limpo/registro.py balanco-triatlo
```

Ele copia o projeto para uma pasta temporária, sem o que o `.gitignore` tira, e segue os passos da seção "Como rodar" do README do projeto. Termina com `resultado: reproduziu` ou `resultado: não reproduziu`. Para gravar o registro num arquivo, acrescente `--salvar meu-registro.md`.

Para comparar o relatório que saiu com o que foi enviado:

```bash
diff relatorio-enviado.md balanco-triatlo/saida/relatorio/relatorio.md
```

Sem diferença, o `diff` não mostra nada e termina com 0. Com diferença, mostra as linhas e termina com 1. Se você não tem o `diff`, abra os dois arquivos lado a lado no VS Code, com o comando "Compare Selected".

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
