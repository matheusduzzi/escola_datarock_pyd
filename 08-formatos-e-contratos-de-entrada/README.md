# 08. Formatos e contratos de entrada

Os arquivos da aula «Formatos e contratos de entrada». Rode os comandos de dentro desta pasta. O exercício usa as inscrições do triatlo, em `../dados/triatlo`; o dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md).

Os programas dessa aula usam o pandas do kit do curso (veja o README da raiz do kit). As saídas da aula são do pandas 2.3.3 com Python 3.9. No pandas 3, alguns tipos aparecem com outro nome, por exemplo `str` no lugar de `object`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `pedidos-online-julho.csv` | Os pedidos de julho da loja online, como a planilha da plataforma exporta: Windows-1252, `;`, vírgula decimal. |
| `pedidos-online-julho.json` | Os mesmos 120 pedidos, na exportação JSON da plataforma. |
| `pedidos-online-agosto.json` | A exportação de agosto, depois que a plataforma foi atualizada. |
| `olhar_formatos.py` | Abre os pedidos de julho do jeito mais direto e mostra o que o pandas entendeu. |
| `contrato-pedidos-online.md` | O contrato de entrada dos pedidos da loja online. |
| `ler_pedidos_online.py` | Lê os pedidos pelo contrato e para com uma lista quando o arquivo não segue. |
| `contrato-inscricoes.md` | O contrato do exercício, para você preencher. Salve uma cópia com o seu nome. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 olhar_formatos.py
python3 ler_pedidos_online.py
python3 ler_pedidos_online.py --arquivo pedidos-online-julho.csv
python3 ler_pedidos_online.py --comparar
python3 ler_pedidos_online.py --arquivo pedidos-online-agosto.json
```

No Windows, troque `python3` por `py`.

O `olhar_formatos.py` mostra seis passos, um depois do outro. O primeiro é o erro de codificação do CSV; o programa mostra a mensagem e segue.

O `ler_pedidos_online.py` com o JSON e com o CSV de julho mostra os 120 pedidos e o tipo de cada campo. O `--comparar` lê os dois e diz se as tabelas são iguais. Com o JSON de agosto, o programa termina com o código 1 e lista o que veio diferente do contrato. É de propósito: é a prática guiada.

As mensagens de erro saem no terminal com `ERROR` na frente. A tabela sai na saída normal. Para ver o código de saída do último comando, rode `echo $?` no macOS e no Linux, ou `echo $LASTEXITCODE` no PowerShell.

O exercício não tem programa pronto: você escreve o seu, usando o `ler_pedidos_online.py` como modelo.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
