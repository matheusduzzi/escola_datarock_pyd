# A base da aula

`base_triatlo.csv` é a base que o `rodar.py` da aula 42, «Triatlo: integração e qualidade», grava em `saida/`: 880 linhas, uma por inscrição das duas edições, e 20 colunas. É o mesmo arquivo, byte a byte. Ele está aqui para você fazer essa aula sem subir a API.

O sha256 do arquivo começa com `63041a14`. Para ver o seu:

```bash
shasum -a 256 base_triatlo.csv
```

No Windows, no PowerShell: `Get-FileHash base_triatlo.csv`.

As colunas são as do contrato da aula 41. As que a análise usa:

| Coluna | O que é |
|---|---|
| `edicao` | 2024 ou 2025 |
| `id_inscricao` | a chave da base, uma por linha |
| `id_atleta` | a pessoa; é a coluna para seguir alguém de um ano para o outro |
| `sexo`, `categoria` | do cadastro e da inscrição; a categoria é o sexo e a faixa de idade no ano da prova |
| `status` | `concluiu`, `DNF`, `DNS`, `DSQ` ou `sem resultado` |
| `natacao_s`, `t1_s`, `ciclismo_s`, `t2_s`, `corrida_s` | as parciais, em segundos; vazio quer dizer que o tempo não existe |
| `oficial_s` | o tempo oficial, em segundos, só de quem concluiu |

As outras colunas (`numero_peito`, `equipe`, `parciais_vazias`, `motivo`, `fonte_resultado`, `origem_pagina`, `origem_posicao`, `copias`) dizem de onde veio cada resultado. Elas estão explicadas na aula 42.
