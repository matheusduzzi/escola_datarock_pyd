# 40. Revisar e entregar código

Os arquivos da aula «Revisar e entregar código». Rode os comandos de dentro desta pasta.

| Arquivo | Para que serve |
|---|---|
| `montar_caso.py` | Monta um repositório Git do `tempos-por-etapa` com a mudança do Caio na branch `transicoes`. Só usa a biblioteca padrão e o Git, sem internet. |
| `tempos-por-etapa/` | O projeto como está na `main`: o que reproduziu na aula anterior, já com a correção do exercício de lá. Faça aquele exercício antes de abrir esta pasta. |
| `mudanca-do-caio/` | Os commits do Caio, um por pasta. O `montar_caso.py` lê daqui. Você não precisa abrir. |
| `modelo-revisao.md` | A folha da revisão: decisão, resumo e um comentário por problema. |
| `modelo-entrega.md` | A folha da entrega para a Lívia, depois da revisão. |

## Do que precisa

- Git 2.28 ou mais novo (`git --version`). O `montar_caso.py` usa `git init -b main`.
- O ambiente do projeto da aula anterior, com o pandas, o Matplotlib e o pytest da lista `requirements-dev.txt`. A lista desta pasta é a mesma de lá. Se ainda não tem, crie de dentro de `tempos-por-etapa`:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
```

No Windows, troque `python3` por `py` e `.venv/bin/python` por `.venv\Scripts\python.exe`.

A aula foi rodada com o Python 3.9.6 no macOS, o Git 2.54, o pandas 2.3.3 e o pytest 8.4.2.

## Montar o caso

```bash
python3 montar_caso.py aula
python3 montar_caso.py exercicio
```

O primeiro cria `caso-aula/tempos-por-etapa`, com os três commits que a aula revisa. O segundo cria `caso-exercicio/tempos-por-etapa`, com um quarto commit: a resposta do Caio à revisão. Os dois ficam na branch `transicoes`. Nomes, e-mails e datas dos commits são fixos, então os hashes do `git log` saem iguais aos da aula.

Se a pasta já existe, o script para com o código 2 e não mexe nela. Para montar de novo, apague a pasta `caso-aula` ou `caso-exercicio`. Sem dizer qual caso, ele mostra o uso e termina com 1.

## Rodar o projeto dentro do caso

Entre na pasta do repositório e use o Python do ambiente que você já criou. Por exemplo, com o ambiente em `tempos-por-etapa/.venv`:

```bash
cd caso-aula/tempos-por-etapa
../../tempos-por-etapa/.venv/bin/python -m tempos
../../tempos-por-etapa/.venv/bin/python -m pytest -q testes
```

Os comandos de Git da aula (`git log`, `git diff`, `git show`) rodam nessa mesma pasta.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
