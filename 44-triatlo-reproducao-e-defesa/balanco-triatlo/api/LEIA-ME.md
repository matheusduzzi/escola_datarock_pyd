# API local

Um servidor pequeno que roda no seu computador e responde como uma API de verdade: paginação, token, códigos de status e, quando você pede, falhas. Ele serve para as aulas de integração e para o projeto, sem depender de internet, conta ou serviço de terceiros.

## Subir a API

De dentro da pasta `api/`:

```bash
python3 servidor.py
```

A API fica em `http://127.0.0.1:8765` até você apertar Ctrl+C. Para ver se funciona sem deixar o servidor aberto:

```bash
python3 servidor.py --teste
```

## Chamar

```
GET /v1/resultados?edicao=2025&pagina=1&por_pagina=50
Authorization: Bearer kit-local
```

| Parâmetro | O que faz |
|---|---|
| `pagina` | começa em 1 |
| `por_pagina` | de 1 a 100; o padrão é 50 |
| qualquer outro | filtra pelo campo de mesmo nome, por exemplo `edicao=2024` ou `status=DNF` |

A resposta traz `pagina`, `por_pagina`, `total`, `total_paginas` e `itens`.

| Código | Quando |
|---|---|
| 200 | deu certo |
| 400 | `pagina` ou `por_pagina` fora do formato |
| 401 | faltou o cabeçalho `Authorization` ou o token está errado |
| 404 | a rota não existe; a resposta lista as rotas que existem |
| 429 | muitas chamadas; o cabeçalho `Retry-After` diz quantos segundos esperar |
| 503 | serviço fora do ar naquele momento |

## Falhas preparadas

```bash
python3 servidor.py --falhas
```

Com `--falhas`, a primeira chamada da página 2 recebe 429, a primeira da página 3 recebe 503 e a primeira da página 5 demora 5 segundos. A segunda chamada de cada uma responde normal. É assim que as aulas de falhas de integração e de testes mostram o que o seu programa faz quando a API não ajuda.

## Servir outros dados

O servidor publica cada arquivo `api_<nome>.json` de uma pasta como a rota `/v1/<nome>`. Uma aula que trouxer os próprios dados roda:

```bash
python3 ../api/servidor.py --pasta dados_da_aula
```
