# Tempos por etapa

Mediana de natação, ciclismo, corrida, transições (T1 + T2) e tempo total por categoria, só de quem terminou a prova. Para a comissão técnica do triatlo.

A coluna `nao_terminaram` conta, em cada categoria, quantos atletas tiveram DNF.

Atleta com DNF (não terminou) ou DNS (não largou) conta entre os inscritos e fica fora das medianas. Parcial vazia não é zero.

## Do que precisa

- Python 3.9 ou mais novo.
- As bibliotecas de `requirements-dev.txt`. O `requirements-dev.txt` é a lista travada: a versão exata de cada pacote, gerada a partir de `requirements-dev.in`.

## Como rodar

Tudo a partir desta pasta, a que tem este README.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m tempos
.venv/bin/python -m pytest -q testes
```

No Windows, o Python do ambiente fica em `.venv\Scripts\python.exe`.

O comando mostra a tabela por categoria e grava `saida/tempos-por-categoria.csv` e o gráfico `saida/medianas-por-categoria.png`. Os testes terminam com `5 passed`.

## Arquivos

| Caminho | O que faz |
|---|---|
| `dados/resultados.csv` | um atleta por linha: categoria, status e as cinco parciais, em segundos |
| `dados/categorias.txt` | as categorias, na ordem do relatório |
| `tempos/leitura.py` | lê os dois arquivos e para se faltar arquivo ou coluna |
| `tempos/calculo.py` | tempo total e medianas por categoria |
| `tempos/grafico.py` | o gráfico das medianas |
| `tempos/__main__.py` | o comando: chama as partes na ordem |
| `testes/test_calculo.py` | os testes do cálculo |
