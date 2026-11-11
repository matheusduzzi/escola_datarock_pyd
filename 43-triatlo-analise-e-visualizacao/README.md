# 43. Triatlo: análise e visualização

A terceira parte do projeto final. Você compara as etapas e as categorias das duas edições sem misturar distâncias e condições diferentes. Depois faz os dois gráficos do balanço e gera um relatório com o que os números mostram e o que eles não permitem concluir.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `primeira_analise.py` | O resumo do balanço do jeito que a IA escreveu: cinco frases, cada uma com uma conta. A seção 1 da aula mostra o que cada frase compara. |
| `analise.py` | A análise: distâncias e condições, tempo por etapa, desistência e onde parou, categorias, limitações, os dois gráficos e o relatório. Também serve de biblioteca para o exercício. |
| `test_analise.py` | Os nove testes da análise. Não usam a base do triatlo. |
| `dados_da_aula/base_triatlo.csv` | A base da aula 42, uma linha por inscrição. Veja o [LEIA-ME](dados_da_aula/LEIA-ME.md). |
| `mensagem-da-livia.md` | O pedido do exercício. |
| `faixas.py` | O exercício: as funções `faixa` e `comparar_faixas`, que você escreve. |
| `test_faixas.py` | O esqueleto dos testes do exercício: quatro testes com o nome e o que cada um tem que mostrar. |

A ficha das edições vem da base compartilhada do kit, em `../dados/triatlo/edicoes.csv`.

## Do que você precisa

O Python 3.9 ou mais novo, o pandas, o Matplotlib e o pytest, os mesmos das aulas 31, 34 e 36. Se falta algum:

```bash
python3 -m pip install pandas matplotlib pytest
```

A aula foi rodada com o Python 3.9.6, o pandas 2.3.3, o Matplotlib 3.9.4 e o pytest 8.4.2. Com outras versões, os números saem iguais, mas os PNGs podem sair com outros bytes. No Windows, troque `python3` por `py`.

## A análise

De dentro dessa pasta:

```bash
python3 analise.py
```

A saída tem quatro partes e termina com `gravei relatorio/:` e o começo do hash de cada arquivo. O relatório fica em `relatorio/relatorio.md`, com as figuras em `relatorio/figuras/`. Abra no VS Code com a pré-visualização do Markdown para ver as figuras no lugar. Rode de novo e compare os hashes: com a mesma base, saem os mesmos.

A base do kit é a que o `rodar.py` da aula 42 grava, antes dos resultados recuperados do exercício de lá. Se você fez a aula 42 e quer usar a sua base:

```bash
python3 analise.py --base ../42-triatlo-integracao-e-qualidade/saida/base_triatlo.csv
```

Com a base do exercício da aula 42, os números de quem largou mudam um pouco, e o relatório muda junto.

Se aparecer `ERROR não achei`, código 2, você não está dentro da pasta da aula, ou a pasta `dados` do kit não está ao lado dela.

## Os testes

```bash
python3 -m pytest -q test_analise.py
```

A última linha diz `9 passed` e o tempo da rodada.

## O exercício

O pedido está na página da aula e em `mensagem-da-livia.md`. Depois de escrever as funções:

```bash
python3 faixas.py
python3 -m pytest -q test_faixas.py
```

Antes de você escrever, o `faixas.py` para com `ERROR escreva a função comparar_faixas`, código 1, e os quatro testes falham com `escreva este teste`. É assim que eles começam.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
