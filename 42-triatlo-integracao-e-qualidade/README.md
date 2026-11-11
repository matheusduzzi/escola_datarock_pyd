# 42. Triatlo: integração e qualidade

A segunda parte do projeto final. Você junta os arquivos de inscrição, o cadastro e os resultados que vêm pela API numa base só, uma linha por inscrição, e só grava essa base se ela passar nas regras do contrato da aula 41.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `primeira_versao.py` | A primeira versão da base, do jeito que a IA escreveu. Roda sem erro e conta errado. A seção 1 da aula mostra onde. |
| `coletar.py` | A coleta da aula 13, «Tratar falhas de integração», sem mudança: cada página bate com o total da API, com tempo limite e tentativas limitadas. |
| `integrar.py` | As funções da integração: ler as inscrições, juntar as cópias dos resultados, montar a base e passar as regras do contrato. |
| `rodar.py` | Roda tudo na ordem, mostra a contagem de cada passo e grava `saida/base_triatlo.csv` e `saida/conferencia.txt` só se a base passou. |
| `test_integrar.py` | Os 21 testes da integração. Não usam a API nem os arquivos do triatlo. |
| `dados_da_aula/` | O exercício: os resultados que a cronometragem recuperou depois da prova. Veja o [LEIA-ME](dados_da_aula/LEIA-ME.md). |
| `recuperados.py` | O exercício: a função `juntar_recuperados`, que você escreve. |
| `juntar.py` | Chama a sua função, mostra o que entrou e o que ficou pendente e grava a base nova se ela passou. |
| `test_recuperados.py` | O esqueleto dos testes do exercício: sete testes com o nome e o que cada um tem que mostrar. |

Os dados ficam na base compartilhada do kit, em `../dados/triatlo/`, e a API em `../api/`.

## Do que você precisa

O Python 3.9 ou mais novo, o pandas e o pytest, os mesmos das aulas 36 e 37. Se ainda não tem o pytest:

```bash
python3 -m pip install pytest
```

A aula foi rodada com o Python 3.9.6, o pandas 2.3.3 e o pytest 8.4.2. No Windows, troque `python3` por `py` e veja abaixo como definir a variável do token.

## Os testes, sem a API

De dentro dessa pasta:

```bash
python3 -m pytest -q test_integrar.py
```

A última linha diz `21 passed` e o tempo da rodada.

## A base, com a API

Num terminal, suba a API com as falhas preparadas e deixe aberto:

```bash
cd ../api
python3 servidor.py --falhas
```

Em outro terminal, nessa pasta, defina o token e rode:

```bash
export API_TRIATLO_TOKEN=kit-local
python3 rodar.py
```

No Windows, no PowerShell, o token se define com `$env:API_TRIATLO_TOKEN = "kit-local"`.

A saída tem cinco partes e termina com `gravei saida/base_triatlo.csv: 880 linhas, 20 colunas`. A coleta leva uns 15 segundos, porque a API do kit responde devagar de propósito na página 5. Rodar de novo grava o mesmo arquivo, byte a byte. Depois pare a API com Ctrl+C.

O que pode dar errado:

- `ERROR falta a variável de ambiente API_TRIATLO_TOKEN`, código 2: defina o token no mesmo terminal em que você roda o `rodar.py`.
- `ERROR desisti`, código 3: a API não está ligada, ou está em outra porta. Nada foi gravado.
- `FileNotFoundError`: você não está dentro da pasta da aula, ou a pasta `dados` do kit não está ao lado dela.

## O exercício

Rode o `rodar.py` primeiro: o `juntar.py` lê a `saida/base_triatlo.csv`. Depois de escrever a sua função:

```bash
python3 juntar.py
python3 -m pytest -q test_recuperados.py
```

Antes de você escrever, o `juntar.py` para com `NotImplementedError` e os sete testes falham com `escreva este teste`. É assim que eles começam.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
