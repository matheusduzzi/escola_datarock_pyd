# API de resultados da cronometragem

O texto que a empresa de cronometragem mandou para a Bia junto com o token, do jeito que veio.

---

Olá, Bia. A partir desta edição, os resultados ficam na nossa API. Seguem as instruções.

**Endereço.** No kit do curso, a API roda no seu computador: `http://127.0.0.1:8765`.

**Rota.** `GET /v1/resultados`

**Autenticação.** Mande o token no cabeçalho `Authorization`, no formato `Bearer <token>`. O token vai por e-mail, separado deste texto.

**Parâmetros.**

- `edicao`: o ano da prova, por exemplo `2025`. Para mais de uma edição na mesma chamada, separe os anos por vírgula: `edicao=2024,2025`.
- `status`: `concluiu`, `DNF`, `DNS` ou `DSQ`. Os filtros aceitam maiúscula ou minúscula.
- `pagina`: começa em 1.
- `por_pagina`: quantos resultados por página. O padrão é 50 e o máximo é 100.

**Resposta.** Um JSON com `pagina`, `por_pagina`, `total`, `total_paginas` e `itens`. Cada item é um resultado, com as parciais de cada etapa.

**Erros.**

- `403`: token inválido ou faltando.
- `404`: página que não existe, depois da última.
- `429`: chamadas demais. Espere 60 segundos antes de chamar de novo.
- `503`: sistema em manutenção. Tente mais tarde.

Qualquer dúvida, é só responder este e-mail.
