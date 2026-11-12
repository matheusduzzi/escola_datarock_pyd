# Kit do curso Python para dados

Os arquivos que você usa nas aulas: o diagnóstico, a base da Loja Exemplo, os dados da competição de triatlo do projeto final e uma API que roda no seu computador.

## Como o kit está organizado

| Pasta | O que tem |
|---|---|
| `00-apresentacao/` | O diagnóstico: [diagnostico.md](00-apresentacao/diagnostico.md), os dados das cinco tarefas, os programas de cada tarefa, a [folha de respostas](00-apresentacao/minhas-respostas.md), a [folha da sua ordem de estudo](00-apresentacao/minha-ordem.md) e `primeira_olhada.py`, a conta do triatlo que a aula 00 mostra. |
| `dados/loja/` | A base da Loja Exemplo, a mesma de Primeiros passos em dados: SQL e Python para quem está migrando. Ver [dados/loja/LEIA-ME.md](dados/loja/LEIA-ME.md). |
| `dados/triatlo/` | Atletas, inscrições e resultados de duas edições da competição de triatlo. Ver [dados/triatlo/LEIA-ME.md](dados/triatlo/LEIA-ME.md). |
| `api/` | A API local que serve os resultados do triatlo, com paginação, token e falhas preparadas. Ver [api/LEIA-ME.md](api/LEIA-ME.md). |
| `NN-titulo/` | Uma pasta por aula, com o número e o título da aula. Elas entram no kit junto com as aulas. |

Os comandos das aulas rodam de dentro da pasta da aula. Quando uma aula usa a base compartilhada, ela diz o caminho, por exemplo `../dados/loja/pedidos.csv`.

## Do que você precisa

- Python 3.9 ou mais novo, com o pandas. É o ambiente de Primeiros passos em dados: SQL e Python para quem está migrando; se você ainda não preparou o seu, a aula 03. Preparar o ambiente, de lá, mostra como.
- Um editor de código. Se você usa o VS Code de Primeiros passos, serve.
- Um terminal.

As bibliotecas de gráfico e de teste entram nas aulas que usam cada uma, com a versão e o comando de instalação. O projeto fixa todas as versões nas aulas 38 e 39.

Na pasta do kit, instale o que o diagnóstico usa:

```bash
python3 -m pip install -r requirements.txt
```

E veja se funcionou:

```bash
cd 00-apresentacao
python3 -c "import pandas as pd; print(pd.read_csv('dados/pedidos.csv').shape)"
```

A saída é `(12, 6)`: 12 pedidos e 6 colunas. Se aparecer `No module named 'pandas'`, o `pip` instalou em outro Python. Rode `python3 -m pip install pandas` com o mesmo `python3` que você usa para rodar o programa. No Windows, troque `python3` por `py`.

Para ver se a API local sobe:

```bash
cd ../api
python3 servidor.py --teste
```

A saída começa com `status 200` e diz quantas páginas e itens a API tem.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.

## Licença

A licença de uso e redistribuição do kit ainda vai ser definida pela Escola Datarock. Até lá, use os arquivos para estudar o curso. Os dados da Loja Exemplo e do triatlo são inventados e foram gerados pelos programas do próprio kit.

## Aulas com arquivos neste kit

| Pasta | Aula |
|---|---|
| [00-apresentacao/](00-apresentacao/) | Apresentação |
| [01-escolher-python-sql-e-ambiente-de-execucao/](01-escolher-python-sql-e-ambiente-de-execucao/) | Escolher Python, SQL e ambiente de execução |
| [02-organizar-um-projeto-executavel/](02-organizar-um-projeto-executavel/) | Organizar um projeto executável |
| [03-mutabilidade-referencias-e-conversoes/](03-mutabilidade-referencias-e-conversoes/) | Mutabilidade, referências e conversões |
| [04-colecoes-e-dados-aninhados/](04-colecoes-e-dados-aninhados/) | Coleções e dados aninhados |
| [05-funcoes-escopo-e-contratos/](05-funcoes-escopo-e-contratos/) | Funções, escopo e contratos |
| [06-refatorar-uma-analise/](06-refatorar-uma-analise/) | Refatorar uma análise |
| [07-depurar-e-tratar-excecoes/](07-depurar-e-tratar-excecoes/) | Depurar e tratar exceções |
| [08-formatos-e-contratos-de-entrada/](08-formatos-e-contratos-de-entrada/) | Formatos e contratos de entrada |
| [09-processar-multiplos-arquivos/](09-processar-multiplos-arquivos/) | Processar múltiplos arquivos |
| [10-ler-json-aninhado/](10-ler-json-aninhado/) | Ler JSON aninhado |
| [11-http-e-contrato-de-api/](11-http-e-contrato-de-api/) | HTTP e contrato de API |
| [12-consumir-uma-api-paginada/](12-consumir-uma-api-paginada/) | Consumir uma API paginada |
| [13-tratar-falhas-de-integracao/](13-tratar-falhas-de-integracao/) | Tratar falhas de integração |
| [14-reexecutar-sem-duplicar/](14-reexecutar-sem-duplicar/) | Reexecutar sem duplicar |
| [15-arrays-dimensoes-e-tipos/](15-arrays-dimensoes-e-tipos/) | Arrays, dimensões e tipos |
| [16-indexacao-e-broadcasting/](16-indexacao-e-broadcasting/) | Indexação e broadcasting |
| [17-vetorizacao-e-custo/](17-vetorizacao-e-custo/) | Vetorização e custo |
| [18-agregacoes-e-estabilidade-numerica/](18-agregacoes-e-estabilidade-numerica/) | Agregações e estabilidade numérica |
| [19-medir-antes-de-otimizar/](19-medir-antes-de-otimizar/) | Medir antes de otimizar |
| [20-indice-alinhamento-e-tipos-anulaveis/](20-indice-alinhamento-e-tipos-anulaveis/) | Índice, alinhamento e tipos anuláveis |
| [21-converter-e-validar-tipos/](21-converter-e-validar-tipos/) | Converter e validar tipos |
| [22-transformar-com-regras-explicitas/](22-transformar-com-regras-explicitas/) | Transformar com regras explícitas |
| [23-juncoes-e-contratos-de-cardinalidade/](23-juncoes-e-contratos-de-cardinalidade/) | Junções e contratos de cardinalidade |
| [24-validar-merge-e-concatenar-fontes/](24-validar-merge-e-concatenar-fontes/) | Validar merge e concatenar fontes |
| [25-agregacoes-transform-e-metricas-de-grupo/](25-agregacoes-transform-e-metricas-de-grupo/) | Agregações, transform e métricas de grupo |
| [27-pivot-melt-e-reconstrucao/](27-pivot-melt-e-reconstrucao/) | Pivot, melt e reconstrução |
| [28-datas-fusos-e-series-tabulares/](28-datas-fusos-e-series-tabulares/) | Datas, fusos e séries tabulares |
| [30-escolher-grafico-pela-pergunta/](30-escolher-grafico-pela-pergunta/) | Escolher gráfico pela pergunta |
| [32-evitar-interpretacoes-enganosas/](32-evitar-interpretacoes-enganosas/) | Evitar interpretações enganosas |
| [33-interatividade-quando-ajuda/](33-interatividade-quando-ajuda/) | Interatividade quando ajuda |
| [34-produzir-relatorio-reproduzivel/](34-produzir-relatorio-reproduzivel/) | Produzir relatório reproduzível |
| [36-escrever-testes-de-dados-e-funcoes/](36-escrever-testes-de-dados-e-funcoes/) | Escrever testes de dados e funções |
| [40-revisar-e-entregar-codigo/](40-revisar-e-entregar-codigo/) | Revisar e entregar código |
| [41-triatlo-briefing-e-contrato/](41-triatlo-briefing-e-contrato/) | Triatlo: briefing e contrato |
| [42-triatlo-integracao-e-qualidade/](42-triatlo-integracao-e-qualidade/) | Triatlo: integração e qualidade |
| [43-triatlo-analise-e-visualizacao/](43-triatlo-analise-e-visualizacao/) | Triatlo: análise e visualização |
| [44-triatlo-reproducao-e-defesa/](44-triatlo-reproducao-e-defesa/) | Triatlo: reprodução e defesa |
