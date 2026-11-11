# 09. Processar múltiplos arquivos

Os arquivos da aula «Processar múltiplos arquivos». Os programas acham as pastas a partir do lugar deles, então rodam de dentro desta pasta ou da raiz do kit. Os comandos abaixo são de dentro desta pasta.

Os programas usam o pandas do kit do curso (veja o README da raiz do kit). As saídas da aula são do pandas 2.3.3 com Python 3.9.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `exportacoes/` | A pasta de exportações da loja online, de julho a outubro, do jeito que o Caio mandou. |
| `olhar_pasta.py` | Mostra o caminho do script do Caio, a diferença entre partir do terminal e partir do programa e três ordens para os mesmos arquivos. |
| `juntar_direto.py` | O script do Caio, só com o caminho trocado: junta todos os `.json` da pasta. |
| `contrato_pedidos.py` | O contrato de entrada dos pedidos da aula 08, que o `consolidar_pedidos.py` usa para ler cada arquivo. |
| `consolidar_pedidos.py` | Olha a pasta, lê cada arquivo pelo contrato e junta os meses em ordem, com o arquivo e o registro de cada pedido. |
| `inscricoes-2026/` | Os lotes de inscrição de 2026 do triatlo, para o exercício. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 olhar_pasta.py
python3 juntar_direto.py
python3 consolidar_pedidos.py
python3 consolidar_pedidos.py --ignorar "pedidos-online-setembro (1).json"
python3 consolidar_pedidos.py --ignorar "pedidos-online-setembro (1).json" --meses julho agosto setembro outubro novembro
```

No Windows, troque `python3` por `py`.

O `juntar_direto.py` roda sem erro e conta pedidos a mais. A aula mostra por quê.

O `consolidar_pedidos.py` sem opção termina com o código 1 e mostra o que está fora do lugar na pasta. É de propósito: é a seção 4 da aula. Com o `--ignorar`, ele junta os quatro meses e grava `saida/pedidos-consolidados.csv`, com as colunas `arquivo` e `registro` na frente. O último comando pede novembro, que não tem arquivo, e termina com o código 1: é o pedido 2 da prática guiada.

As mensagens de problema saem no terminal com `ERROR` na frente, e os avisos com `INFO`. O resumo sai na saída normal. Para ver o código de saída do último comando, rode `echo $?` no macOS e no Linux, ou `echo $LASTEXITCODE` no PowerShell.

Para ver que o caminho parte do programa, rode da raiz do kit:

```bash
cd ..
python3 09-processar-multiplos-arquivos/consolidar_pedidos.py --ignorar "pedidos-online-setembro (1).json"
```

A pasta `saida/` é criada pelo programa. Pode apagar quando quiser: ela sai igual toda vez que você roda.

O exercício não tem programa pronto: você escreve o seu, usando o `consolidar_pedidos.py` como modelo.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
