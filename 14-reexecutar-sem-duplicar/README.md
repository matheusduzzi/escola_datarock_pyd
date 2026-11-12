# 14. Reexecutar sem duplicar

Os arquivos da aula «Reexecutar sem duplicar». Os comandos abaixo são de dentro desta pasta. Os programas só usam a biblioteca padrão do Python, com o `sqlite3` que já vem com ele. O trecho da seção 1 da aula usa o pandas, o mesmo do resto do curso.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `acumular_ia.py` | A coleta de todo dia do jeito que a IA escreveu: acrescenta cada página no fim de `acumulado-<edicao>.jsonl`. A seção 1 da aula mostra o que acontece depois de três rodadas. |
| `atualizar.py` | O programa da aula: atualiza a base `base-triatlo.sqlite` com uma linha por resultado, guarda as páginas no checkpoint e grava a rodada de uma vez. |
| `coletar.py` | O programa da aula 13, sem mudança. O `atualizar.py` usa as tentativas e o tempo limite dele. |
| `impressao.py` | A impressão digital dos resultados de uma base, sem as datas. Duas bases com os mesmos resultados têm a mesma impressão. |
| `transacao.py` | O exemplo da seção 4: uma transação que falha no meio não deixa nada gravado. |
| `api_revisada.py` | A API do kit, na mesma porta e com o mesmo token, servindo os resultados depois da revisão da cronometragem. |
| `api_instavel.py` | A API da aula 13 com falhas que não passam logo. Nessa aula ela ganhou a opção `--pasta`, para servir os dados revisados. |
| `revisada/api_resultados.json` | Os resultados depois da revisão da cronometragem: três resultados de 2025 corrigidos e uma inscrição cancelada. |
| `gerar_revisada.py` | Gera o `revisada/api_resultados.json` a partir dos dados do triatlo do kit. Sempre escreve o mesmo arquivo. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Subir a API

São três jeitos, um de cada vez, sempre na porta 8765. Pare um (Ctrl+C) antes de subir o outro.

A API normal, a das aulas 11 a 13, num terminal na pasta `api` do kit:

```bash
python3 servidor.py
```

A API com a revisão dos tempos, desta pasta:

```bash
python3 api_revisada.py
```

A API que cai na página 3, desta pasta, com os dados de antes ou com os revisados:

```bash
python3 api_instavel.py --cenario fora
python3 api_instavel.py --cenario fora --pasta revisada
```

No cenário `fora`, a página 3 responde 503 em toda chamada, e a coleta desiste depois de 3 tentativas. Os outros cenários da aula 13 (`espera-longa` e `madrugada`) também funcionam.

## Definir o token

Em outro terminal, nesta pasta. O token da API do kit é `kit-local`. Ele fica numa variável de ambiente, e não dentro do programa.

No macOS e no Linux:

```bash
export API_TRIATLO_TOKEN=kit-local
```

No PowerShell: `$env:API_TRIATLO_TOKEN = "kit-local"`. No Prompt de Comando do Windows: `set API_TRIATLO_TOKEN=kit-local`.

Os programas procuram a API no endereço da variável `API_TRIATLO_URL`. Sem ela, usam o endereço da API do kit, na porta 8765 da sua máquina. Só defina a variável se a API estiver em outro lugar.

## Comandos

```bash
python3 acumular_ia.py --edicao 2025
python3 atualizar.py --edicao 2025
python3 atualizar.py --edicao 2025 --base base-direta.sqlite
python3 atualizar.py --edicao 2025 --por-pagina 50
python3 impressao.py base-triatlo.sqlite
python3 transacao.py
```

No Windows, troque `python3` por `py`.

O `atualizar.py` aceita:

- `--edicao`, obrigatório: a edição que vai coletar;
- `--base`, o arquivo da base, padrão `base-triatlo.sqlite` (o programa cria se não existir);
- `--por-pagina`, de 1 a 100, padrão 100;
- `--espera`, o tempo limite de cada chamada, em segundos, padrão 10;
- `--do-zero`, para descartar o checkpoint e começar a rodada da página 1;
- `--endereco`, se a API estiver em outro endereço.

Ele termina com o código:

- 0 quando a base foi atualizada;
- 1 quando a coleta não bateu ou a API respondeu um erro que não passa tentando de novo; a base não mudou e o checkpoint foi descartado;
- 2 quando falta a variável `API_TRIATLO_TOKEN`, sem fazer chamada nenhuma;
- 3 quando a falha podia passar e não passou; a base não mudou e as páginas que vieram ficaram no checkpoint.

Para ver o código de saída do último comando, rode `echo $?` no macOS e no Linux, ou `echo $LASTEXITCODE` no PowerShell.

## O que fica na base

O `base-triatlo.sqlite` é um arquivo só, com quatro tabelas:

| Tabela | Uma linha é |
|---|---|
| `resultados` | um resultado, com a chave (edição e `id_inscricao`), o conteúdo em JSON, quando entrou e quando mudou pela última vez |
| `rodadas` | uma rodada que terminou, com quantos novos, mudaram, iguais e não vieram |
| `checkpoint` | a rodada em andamento, se houver: rota, filtros, `por_pagina`, total e hora em que começou |
| `checkpoint_paginas` | uma página que já veio na rodada em andamento |

O checkpoint só é usado se for da mesma rodada, se o total da API não mudou e se tiver menos de uma hora. Depois de uma rodada que termina, as duas tabelas do checkpoint ficam vazias.

## Para o exercício

A função `atualizar()` do `atualizar.py` aceita um parâmetro `ao_aplicar`, explicado no comentário dela. Para copiar uma base, use `cp` no macOS e no Linux e `copy` no Windows.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
