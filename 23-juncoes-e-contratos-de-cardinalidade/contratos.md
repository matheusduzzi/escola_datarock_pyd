# Contratos dos merges do projeto do triatlo

Nome:

Salve uma cópia desta folha com o seu nome. Preencha um contrato para cada merge. O primeiro é o da aula, e serve de exemplo.

## Merge principal: inscrições com resultados (exemplo da aula)

| Campo | Resposta |
|---|---|
| Para que serve | a base do projeto, uma linha por inscrição, com o resultado quando existe |
| Esquerda | inscrições das duas edições; uma linha é uma inscrição; 880 depois de tirar 3 cópias iguais |
| Direita | resultados da cronometragem; uma linha é um resultado; 873 depois de tirar 8 cópias iguais |
| Chave | `edicao` + `id_inscricao` |
| Relação esperada | 1 para 0 ou 1: uma inscrição tem no máximo um resultado, um resultado é de uma inscrição |
| `validate` | `"one_to_one"` |
| Cobertura da esquerda | pode faltar resultado: a inscrição fica, com status "sem resultado"; hoje são 7 |
| Cobertura da direita | todo resultado tem inscrição; nenhum sem par |
| `how` | `"left"`, partindo das inscrições |
| Linhas depois | 880, igual ao número de inscrições |
| Se quebrar | cópia igual sai antes do merge; chave repetida com conteúdo diferente para o programa; resultado sem inscrição para o programa |

## Merge A: inscrições com atletas

| Campo | Resposta |
|---|---|
| Para que serve | |
| Esquerda | |
| Direita | |
| Chave | |
| Relação esperada e o motivo | |
| `validate` | |
| Cobertura da esquerda | |
| Cobertura da direita | |
| `how` | |
| Linhas depois | |
| Se quebrar | |

O que o `medir` mostrou (cole a saída):

```text

```

Os dados cumprem o contrato? Quantas linhas saíram do merge?

## Merge B: inscrições com edições

| Campo | Resposta |
|---|---|
| Para que serve | |
| Esquerda | |
| Direita | |
| Chave | |
| Relação esperada e o motivo | |
| `validate` | |
| Cobertura da esquerda | |
| Cobertura da direita | |
| `how` | |
| Linhas depois | |
| Se quebrar | |

O que o `medir` mostrou (cole a saída):

```text

```

Os dados cumprem o contrato? Quantas linhas saíram do merge?

## Merge C: inscrições de 2024 com inscrições de 2025

| Campo | Resposta |
|---|---|
| Para que serve | |
| Esquerda | |
| Direita | |
| Chave | |
| Relação esperada e o motivo | |
| `validate` | |
| Cobertura da esquerda | |
| Cobertura da direita | |
| `how` | |
| Linhas depois | |
| Se quebrar | |

O que o `medir` mostrou (cole a saída):

```text

```

Os dados cumprem o contrato? Quantas linhas saíram do merge?
