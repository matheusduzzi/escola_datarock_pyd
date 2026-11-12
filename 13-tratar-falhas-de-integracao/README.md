# 13. Tratar falhas de integração

Os arquivos da aula «Tratar falhas de integração». Os comandos abaixo são de dentro desta pasta. Os programas só usam a biblioteca padrão do Python; não precisa instalar nada.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `coletar_insistente.py` | A coleta com tentativas, do jeito que a IA escreveu: tenta de novo até dar certo, com qualquer erro. A seção 1 da aula mostra por que isso é um problema. |
| `coletar.py` | O programa da aula: a coleta da aula 12 com tempo limite por chamada, no máximo 3 tentativas por página, espera pelo que a API pede (até 30 s) e cada falha anotada no resumo. |
| `api_instavel.py` | A API do kit com falhas que não passam logo, para ver o programa desistir. Três cenários: `fora`, `espera-longa` e `madrugada`. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Subir a API

A API é a da pasta `api` do kit, a mesma das aulas 11 e 12. Abra um terminal na pasta `api` e suba com as falhas preparadas:

```bash
python3 servidor.py --falhas
```

Com `--falhas`, a página 2 responde 429 e a página 3 responde 503 na primeira chamada, e a primeira chamada da página 5 demora 5 segundos para responder. O LEIA-ME da pasta `api` explica. Para ver as falhas de novo, pare com Ctrl+C e suba outra vez.

Para os cenários que não passam logo, pare a API normal e suba a `api_instavel.py`, de dentro desta pasta. Ela usa a mesma porta, os mesmos dados e o mesmo token:

```bash
python3 api_instavel.py --cenario fora
python3 api_instavel.py --cenario espera-longa
python3 api_instavel.py --cenario madrugada
```

| Cenário | O que acontece |
|---|---|
| `fora` | a página 3 responde 503 em toda chamada |
| `espera-longa` | a primeira chamada da página 2 responde 429 e pede uma hora de espera (3600 s) |
| `madrugada` | a primeira chamada da página 2 responde 429 e pede 3 s; as duas primeiras da página 3 respondem 503 |

As duas APIs escrevem no terminal cada chamada que recebem, com o código da resposta. É ali que você conta as chamadas nos pedidos 2 e 3 da prática.

## Definir o token

Em outro terminal, nesta pasta. O token da API do kit é `kit-local`. Ele fica numa variável de ambiente, e não dentro do programa.

No macOS e no Linux:

```bash
export API_TRIATLO_TOKEN=kit-local
```

No PowerShell: `$env:API_TRIATLO_TOKEN = "kit-local"`. No Prompt de Comando do Windows: `set API_TRIATLO_TOKEN=kit-local`.

Para o token errado da seção 6 e do pedido 3, troque o valor (`export API_TRIATLO_TOKEN=errado`) e volte para `kit-local` depois.

## O endereço da API

Os programas procuram a API no endereço da variável `API_TRIATLO_URL`. Sem ela, usam o endereço da API do kit, na porta 8765 da sua máquina. Só defina a variável se a API estiver em outro lugar; também dá para passar `--endereco`.

## Comandos

```bash
python3 coletar_insistente.py
python3 coletar.py --edicao 2025
python3 coletar.py --edicao 2025 --espera 2 --saida resultados-2025-espera.json
```

No Windows, troque `python3` por `py`.

O `coletar_insistente.py` não termina com o token errado ou com a API parada. Aperte Ctrl+C para parar.

O `coletar.py` aceita:

- `--edicao`, obrigatório: a edição que vai coletar;
- `--por-pagina`, de 1 a 100, padrão 100;
- `--saida`, o nome do arquivo, padrão `resultados-<edicao>.json`;
- `--espera`, o tempo limite de cada chamada, em segundos, padrão 10;
- `--endereco`, se a API estiver em outro endereço.

Ele termina com o código:

- 0 quando a coleta bateu e o arquivo foi gravado, com as falhas do caminho no resumo;
- 1 quando a coleta não bateu ou a API respondeu um erro que não passa tentando de novo (401, 400, 404, 500...); nada foi gravado;
- 2 quando falta a variável `API_TRIATLO_TOKEN`, sem fazer chamada nenhuma;
- 3 quando a falha podia passar e não passou: 3 tentativas sem sucesso, ou a API pediu mais de 30 s de espera; nada foi gravado.

Para ver o código de saída do último comando, rode `echo $?` no macOS e no Linux, ou `echo $LASTEXITCODE` no PowerShell.

## Ver se um arquivo mudou

Para a seção 6 e o exercício, anote a impressão digital do arquivo antes e depois de uma rodada que desiste. Se ela não mudou, o arquivo é o mesmo.

No macOS e no Linux:

```bash
shasum -a 256 resultados-2025.json
```

No PowerShell: `Get-FileHash resultados-2025.json`.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
