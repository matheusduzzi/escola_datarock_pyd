# Minhas respostas: o pacote do site

Nome:

## 1. A previsão, antes de rodar

O menor e o maior valor que eu olhei nos arrays originais:

| Array | Menor | Maior |
|---|---|---|
| `r["peito"]` |  |  |
| `r["edicao"]` |  |  |
| `r["tempos"]` |  |  |

### Os quatro arrays da proposta

| Array | Forma | Tipo | nbytes | Todos os valores cabem? | Motivo |
|---|---|---|---|---|---|
| `peito8` |  |  |  |  |  |
| `edicao8` |  |  |  |  |  |
| `concluiu` |  |  |  |  |  |
| `tempos16` |  |  |  |  |  |

### As cinco contas do site

| Conta | Forma | Tipo | O valor sai certo? | Motivo |
|---|---|---|---|---|
| a. `tempos16.sum(axis=1)` |  |  |  |  |
| b. `tempos16[:, 2] + tempos16[:, 4]` |  |  |  |  |
| c. `tempos16 / 60` |  |  |  |  |
| d. `(edicao8 == 2025).sum()` |  |  |  |  |
| e. `concluiu.sum()` |  |  |  |  |

## 2. O que saiu

Saída de `python3 pacote_do_site.py`:

```text

```

| Item | O que eu previ | O que saiu | Se errei, a regra que explica |
|---|---|---|---|
| `peito8` |  |  |  |
| `edicao8` |  |  |  |
| `concluiu` |  |  |  |
| `tempos16` |  |  |  |
| a |  |  |  |
| b |  |  |  |
| c |  |  |  |
| d |  |  |  |
| e |  |  |  |

Os quatro números:

| Número | Proposta do Caio | Certo seria |
|---|---|---|
| peitos diferentes |  |  |
| resultados de 2025 na conta d |  |  |
| conta b negativa |  |  |
| parciais vazias que viraram 0 |  |  |

## 3. A minha recomendação

| Array | Tipo | Por quê | nbytes (do programa) |
|---|---|---|---|
| peito |  |  |  |
| edicao |  |  |  |
| concluiu |  |  |  |
| tempos |  |  |  |
| **total** |  |  |  |

Bytes por linha, à mão:

Com 1 milhão de linhas:

Os quatro números na versão nova:
