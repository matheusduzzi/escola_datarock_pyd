# 12. Consumir uma API paginada

Os arquivos da aula «Consumir uma API paginada». Os comandos abaixo são de dentro desta pasta. Os programas só usam a biblioteca padrão do Python; não precisa instalar nada.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `coletar_direto.py` | O primeiro programa de coleta, do jeito que a IA escreveu. Roda sem erro e perde a última página. A seção 1 da aula mostra por quê. |
| `coletar.py` | O programa da aula: pede todas as páginas de uma edição, guarda a origem de cada linha e só grava quando a soma bate com o total da API. |
| `origem.py` | Mostra de que página, posição e chamada veio cada linha de uma inscrição, num arquivo gravado pelo `coletar.py`. |
| `pagina_que_escorrega.py` | Mostra, sem chamar a API, o que acontece com páginas por número quando a lista muda no meio da coleta. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Subir a API

A API é a da pasta `api/` do kit, a mesma da aula 11. Num terminal, suba e deixe aberto:

```bash
cd ../api
python3 servidor.py
```

Para a seção 6, o pedido 3 da prática e a tarefa 3 do exercício, pare com Ctrl+C e suba de novo com `python3 servidor.py --falhas`. O LEIA-ME da pasta `api/` explica as falhas. Cada falha só acontece na primeira chamada daquela página; para ver de novo, pare e suba a API outra vez.

## Definir o token

Em outro terminal, nesta pasta. O token da API do kit é `kit-local`. Ele fica numa variável de ambiente, e não dentro do programa.

No macOS e no Linux:

```bash
export API_TRIATLO_TOKEN=kit-local
```

No PowerShell: `$env:API_TRIATLO_TOKEN = "kit-local"`. No Prompt de Comando do Windows: `set API_TRIATLO_TOKEN=kit-local`.

A variável vale enquanto esse terminal estiver aberto. Num terminal novo, defina de novo.

## Comandos

```bash
python3 coletar_direto.py
python3 coletar.py --edicao 2025
python3 origem.py resultados-2025.json 2025-0228
python3 coletar.py --edicao 2025 --por-pagina 50 --saida resultados-2025-50.json
python3 pagina_que_escorrega.py
```

No Windows, troque `python3` por `py`.

O `coletar_direto.py` e o `coletar.py` gravam no mesmo `resultados-2025.json`. Rode o `coletar_direto.py` primeiro, como na aula; o `coletar.py` grava por cima com a coleta completa.

O `coletar.py` aceita:

- `--edicao`, obrigatório: a edição que vai coletar;
- `--por-pagina`, de 1 a 100, padrão 100;
- `--saida`, o nome do arquivo, padrão `resultados-<edicao>.json`;
- `--espera`, os segundos de espera por resposta, padrão 10;
- `--endereco`, se a API estiver em outro endereço (padrão `http://127.0.0.1:8765`, ou a variável `API_TRIATLO_URL`).

Ele termina com o código:

- 0 quando a coleta bateu e o arquivo foi gravado;
- 1 quando a coleta não bateu ou a API respondeu com erro; nada foi gravado;
- 2 quando falta a variável `API_TRIATLO_TOKEN`, sem fazer chamada nenhuma;
- 3 quando a API não responde: ela não está rodando, ou passou do tempo de espera; nada foi gravado.

Com a API em `--falhas`, o código 1 é o esperado nas duas primeiras rodadas: é o que a seção 6 da aula mostra. Para ver o código de saída do último comando, rode `echo $?` no macOS e no Linux, ou `echo $LASTEXITCODE` no PowerShell.

## Ver se um arquivo mudou

Para a tarefa 3 do exercício, anote a impressão digital do arquivo antes e depois de rodar com `--falhas`. Se ela não mudou, o arquivo é o mesmo.

No macOS e no Linux:

```bash
shasum -a 256 resultados-2024-2025.json
```

No PowerShell: `Get-FileHash resultados-2024-2025.json`.

O `coletado_em` dentro do arquivo também diz de que coleta ele é.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
