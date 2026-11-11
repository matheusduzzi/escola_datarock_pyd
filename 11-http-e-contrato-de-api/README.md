# 11. HTTP e contrato de API

Os arquivos da aula «HTTP e contrato de API». Os comandos abaixo são de dentro desta pasta. O `chamar.py` só usa a biblioteca padrão do Python; não precisa instalar nada.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `documentacao-cronometragem.md` | As instruções que a cronometragem mandou para a Bia, do jeito que vieram. |
| `chamar.py` | Faz uma chamada `GET` à API e mostra a requisição e a resposta: código, cabeçalhos e corpo. |
| `mapa-de-consumo.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Subir a API

A API é a da pasta `api/` do kit. Num terminal, suba e deixe aberto:

```bash
cd ../api
python3 servidor.py
```

Para as falhas da seção 3 e do pedido 2 da prática, pare com Ctrl+C e suba de novo com `python3 servidor.py --falhas`. O LEIA-ME da pasta `api/` explica as falhas.

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
python3 chamar.py "/v1/resultados?edicao=2025&pagina=1&por_pagina=100"
python3 chamar.py "/v1/resultados?edicao=2025&pagina=5&por_pagina=100"
python3 chamar.py "/v1/resultados?edicao=2025&pagina=1&por_pagina=500"
python3 chamar.py "/v1/resultado?edicao=2025"
```

No Windows, troque `python3` por `py`.

Os dois primeiros terminam com o código 0: a API respondeu `200`. Os dois últimos terminam com o código 1 de propósito: a API respondeu `400` e `404`, e a aula mostra por quê. Para ver o código de saída do último comando, rode `echo $?` no macOS e no Linux, ou `echo $LASTEXITCODE` no PowerShell.

Para ver o `401`, troque o token só para uma chamada (no macOS e no Linux):

```bash
API_TRIATLO_TOKEN=errado python3 chamar.py "/v1/resultados?edicao=2025&pagina=1"
```

No PowerShell, defina `$env:API_TRIATLO_TOKEN = "errado"`, chame, e defina `kit-local` de novo.

O `chamar.py` termina com o código:

- 0 quando a API responde com um código 2xx;
- 1 quando ela responde com outro código;
- 2 quando falta a variável `API_TRIATLO_TOKEN`, sem fazer chamada nenhuma;
- 3 quando a API não responde: ela não está rodando, ou passou do tempo de espera (`--espera`, 10 segundos por padrão).

Ele mostra `Bearer ***` no lugar do token e não mostra os cabeçalhos `Date` e `Server`, que mudam a cada chamada.

O exercício não tem programa novo: você usa o `chamar.py` e preenche a folha.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
