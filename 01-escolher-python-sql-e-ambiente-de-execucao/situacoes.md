# Três situações da Loja Exemplo

Para cada situação, decida a ferramenta e o lugar onde a conta roda: dentro do banco, num script Python, num notebook, ou uma mistura deles. Anote a decisão e o motivo na sua cópia de `minhas-respostas.md`.

O banco da loja tem as mesmas tabelas da aula (`pedidos`, `produtos`, `clientes`), com os pedidos desde janeiro de 2021. Hoje são cerca de 1,8 milhão de pedidos.

## Situação A. O painel mensal

A gerente quer, no painel da loja, o faturamento dos pedidos entregues por mês e por categoria de produto, desde 2021. O painel atualiza toda manhã, sozinho.

- O painel é uma ferramenta que se conecta ao banco da loja e mostra o resultado de uma consulta SQL. Ele não roda Python.
- Os pedidos e os produtos estão no banco.
- Quem cuida do banco e do painel é a Renata, da TI. Ela escreve SQL todo dia e não programa em Python.
- O Caio já tem um script em pandas que faz essa conta. O script pede a tabela de pedidos inteira ao banco e roda no computador dele.

## Situação B. Planilhas e API

Toda segunda, o Caio monta o relatório de entregas atrasadas da semana anterior, por região, comparado com a meta de prazo de cada região.

- As metas chegam em três planilhas, uma por região, que os gerentes regionais mandam por e-mail toda sexta, em CSV.
- O status de cada entrega vem da API da transportadora: pede um token, entrega 100 entregas por página e responde com o código da entrega e o id do pedido.
- Os pedidos da semana estão no banco da loja. São cerca de 600 pedidos por semana.
- O relatório roda toda segunda. Quando o Caio sai de férias, o Otávio, também do financeiro, roda no lugar dele.

## Situação C. Os cliques dos anúncios

No fim do semestre, a plataforma de anúncios manda um CSV com todos os cliques nos anúncios da loja: uma linha por clique, 60 colunas, 14 GB. São cerca de 35 milhões de cliques, de cerca de 2 milhões de pessoas.

- A gerente quer, por campanha e por mês, o custo total dos cliques e o número de pessoas diferentes que clicaram.
- A conta usa 4 das 60 colunas: `campanha`, `data_clique`, `custo` e `id_usuario`. O `id_usuario` é o código que a plataforma dá para cada pessoa.
- O Caio leu as primeiras 100 mil linhas só com essas 4 colunas e mediu a memória no pandas. Pela conta dele, o arquivo inteiro, só com as 4 colunas, ocuparia uns 7 GB.
- O computador do Caio tem 8 GB de memória. A loja não tem outro servidor com Python.
- O arquivo chega uma vez por semestre, e a conta roda uma vez para cada arquivo.
