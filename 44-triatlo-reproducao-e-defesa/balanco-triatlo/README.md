# Balanço do triatlo

O balanço das edições 2024 e 2025 da competição de triatlo, para a federação: tempo por etapa, desistência e categorias, com o que os números não permitem concluir.

O projeto junta três partes. A base sai dos arquivos de inscrição, do cadastro de atletas e dos resultados que vêm pela API, e só é gravada se passar nas dez regras do contrato. A análise compara só as etapas com a mesma distância, divide a desistência por quem largou e deixa fora do ranking as categorias com menos de 20 pessoas que largaram. O relatório sai do código, com as limitações escritas a partir dos dados.

## Do que precisa

- Python 3.9 ou mais novo.
- As bibliotecas de `requirements-dev.txt`, a lista travada: a versão exata de cada pacote, gerada a partir de `requirements-dev.in`.
- Nada de internet. A API que o projeto usa é a local, em `api/servidor.py`, e o `balanco.py` sobe e desliga essa API sozinho.

## Como rodar

Tudo a partir desta pasta, a que tem este README.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python balanco.py
.venv/bin/python conferir.py
.venv/bin/python -m pytest -q testes
```

No Windows, o Python do ambiente fica em `.venv\Scripts\python.exe`.

O `balanco.py` leva uns 15 segundos, porque a API local responde devagar de propósito numa das páginas. Ele termina com `gravei saida/relatorio/:` e o começo do hash de cada arquivo. O `conferir.py` compara os quatro arquivos de `saida/` com o `esperado.sha256` e termina com `4 de 4 iguais: reproduziu`. Os testes terminam com `34 passed`.

## O que sai

| Arquivo | O que é |
|---|---|
| `saida/base_triatlo.csv` | a base, uma linha por inscrição, tempos em segundos |
| `saida/conferencia.txt` | a tela da montagem da base: contagens, falhas da coleta e regras |
| `saida/relatorio/relatorio.md` | o relatório para a federação |
| `saida/relatorio/figuras/` | os dois gráficos do relatório |

## Arquivos

| Caminho | O que faz |
|---|---|
| `balanco.py` | o comando: sobe a API local, monta a base, analisa e grava `saida/` |
| `coletar.py` | a coleta pela API, com tempo limite e tentativas limitadas |
| `integrar.py` | lê as inscrições e o cadastro, junta as cópias dos resultados, monta a base e passa as regras do contrato |
| `rodar.py` | os passos da base, um por um, com a contagem de cada um |
| `analise.py` | etapas, desistência, categorias, limitações, gráficos e relatório |
| `conferir.py` | compara `saida/` com `esperado.sha256` |
| `esperado.sha256` | os hashes do que o balanço tem que gravar |
| `api/servidor.py` | a API local, com paginação, token e falhas preparadas |
| `dados/triatlo/` | inscrições, atletas, ficha das edições e os resultados que a API serve |
| `testes/` | os testes da integração, da análise e do `conferir.py` |
