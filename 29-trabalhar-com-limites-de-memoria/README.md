# 29. Trabalhar com limites de memória

Os arquivos da aula «Trabalhar com limites de memória». Rode os comandos de dentro desta pasta. O `gerar.py` usa o catálogo de produtos da Loja Exemplo, que fica em `../dados/loja/produtos.csv`. O dicionário está em [../dados/loja/LEIA-ME.md](../dados/loja/LEIA-ME.md).

Você só precisa do Python com o pandas, como no README da raiz do kit. Para ver se ele está aí:

```bash
python3 -c "import pandas; print(pandas.__version__)"
```

A aula foi rodada com o Python 3.9.6 e o pandas 2.3.3. Se aparecer `No module named 'pandas'`, rode `python3 -m pip install pandas` com o mesmo `python3`.

O `historico_itens.csv` não vem pronto: ele tem 131 MB. O `gerar.py` escreve o arquivo no seu computador, sempre com o mesmo conteúdo, em poucos segundos. Deixe uns 150 MB livres no disco.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `gerar.py` | Monta o `historico_itens.csv`: os itens vendidos no marketplace Vitrine Paulista, de janeiro de 2024 a junho de 2026. A última linha da saída traz o começo do sha256 do arquivo, para você ver se o seu é igual ao da aula. |
| `historico_itens.csv` | Escrito pelo `gerar.py`. Uma linha por item de pedido, com 20 colunas: `id_item`, `id_pedido`, `data` (AAAA-MM-DD), `hora`, `id_cliente`, `nome_cliente`, `cidade`, `loja`, `id_produto`, `produto`, `categoria`, `quantidade`, `preco_unitario`, `desconto_pct`, `valor` (valor do item, com o desconto), `status` (`entregue`, `cancelado` ou `devolvido`, o mesmo em todos os itens do pedido), `canal`, `cupom`, `navegador` e `pagina_origem`. |
| `medir.py` | A função `medir`, que roda outra função e retorna o resultado e o pico de memória em MB, pelo `tracemalloc` do Python. |
| `memoria.py` | O faturamento por mês e categoria de seis jeitos: o código da IA, as colunas, os tipos, as partes, os clientes distintos e a comparação. |
| `comparacao.md` | A tabela de memória e resultado, escrita pelo `memoria.py --jeito comparar`. Os números dependem do seu computador e da versão do pandas; o resultado não. |
| `testar_partes.py` | Testa a leitura por partes e a comparação de resultados com as primeiras 30 mil linhas. |
| `exercicio.py` | O programa do exercício. Você preenche `COLUNAS_EX` e `TIPOS_EX` e escreve a função `resumo_por_partes`. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 gerar.py
python3 memoria.py --jeito ia
python3 memoria.py --jeito colunas
python3 memoria.py --jeito tipos
python3 memoria.py --jeito partes
python3 memoria.py --jeito distintos
python3 memoria.py --jeito comparar
python3 testar_partes.py
python3 exercicio.py
```

No Windows, troque `python3` por `py`.

O pico de memória que aparece no seu computador pode ser um pouco diferente do da aula, conforme a versão do Python e do pandas. As linhas de resultado (somas, contagens, "igual" ou "diferente") têm de ser as mesmas.

O `exercicio.py` para com o código 1 e a mensagem `falta escrever resumo_por_partes` enquanto você não escrever a função. Depois de escrita, ele compara o seu resumo com o da leitura inteira em três tamanhos de parte, confere que cada leitura trouxe no máximo o tamanho de parte pedido e que nenhum `pd.concat` juntou mais linhas de itens do que cabem numa parte (juntar todas as partes antes da conta monta o arquivo inteiro de novo), mede o pico, grava `resumo_cidades.csv` e sai com 0 se tudo estiver certo, e com 1 se achar algum problema.

O `testar_partes.py` sai com 1 se a comparação responder errado em algum caso. Se você mexer no `memoria.py`, rode ele de novo.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
