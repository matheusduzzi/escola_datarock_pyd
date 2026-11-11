# Série diária de pedidos da Loja Exemplo

Uma linha por dia de 2026-01-01 a 2026-06-30: 181 dias, sem dia faltando nem repetido.

- **dia**: o dia no relógio de São Paulo (America/Sao_Paulo). O site manda a hora em UTC e ela foi convertida; o caixa da loja escreve a hora de São Paulo, sem fuso.
- **loja**: pedidos do caixa. Vale 0 quando a loja estava fechada (26 domingos e 2026-01-01, 2026-04-03, 2026-04-21, 2026-05-01), marcados em `loja_aberta`.
- **site**: pedidos do site. Fica vazio quando a `cobertura` é `parcial`.
- **cobertura**: `completa` em 179 dias. `parcial` quando a exportação do site falhou numa parte do dia:
  - 2026-04-09: faltam as horas das 21:00 às 24:00; chegaram 8 pedidos do site.
  - 2026-04-10: faltam as horas das 00:00 às 21:00; chegaram 3 pedidos do site.
- **total**: loja + site. Fica vazio nos dias parciais.
- Vazio quer dizer "não sei". Zero quer dizer "não teve pedido".

Gerado por `python3 datas.py --jeito certo`.
