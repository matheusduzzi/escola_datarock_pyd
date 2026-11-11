# Balanço das edições 2024 e 2025: etapas, desistência e categorias

## O que dá para dizer

- Nas etapas com a mesma distância (ciclismo e corrida), a mediana de quem concluiu foi de 623,9 min em 2024 (371 pessoas) e 644,9 min em 2025 (393 pessoas): 21,0 min a mais em 2025.
- Quase toda essa diferença está na corrida: 18,9 min a mais pela mediana. Na corrida, 17 de 20 categorias foram mais lentas em 2025.
- A desistência de quem largou foi de 31 em 405 em 2024 (7,7%) e de 44 em 441 em 2025 (10,0%). Pararam na corrida 20 em 2024 e 33 em 2025; no ciclismo, 11 e 11.
- Entre as categorias com pelo menos 20 pessoas que largaram, a maior taxa de 2025 é M50-54: 8 de 31 (25,8%). Das 5 maiores de 2024, 2 estão entre as 5 maiores de 2025.

## Tempo por etapa, de quem concluiu

| Etapa | Situação | 2024 (min) | 2025 (min) | Diferença (min) |
|---|---|---|---|---|
| natação | não comparável: 3,8 km em 2024, 1,9 km em 2025 | 71,4 (n=371) | 32,9 (n=393) |  |
| T1 | sem distância: a ficha não tem distância de transição | 6,5 (n=367) | 6,8 (n=392) | 0,3 |
| ciclismo | comparável: 180 km nas duas | 358,4 (n=371) | 360,7 (n=393) | 2,3 |
| T2 | sem distância: a ficha não tem distância de transição | 4,8 (n=370) | 5,0 (n=388) | 0,2 |
| corrida | comparável: 42,2 km nas duas | 265,5 (n=371) | 284,4 (n=393) | 18,9 |

![Tempo por etapa](figuras/etapas.png)

## Desistência por categoria, de quem largou

| Categoria | 2024 | 2025 |
|---|---|---|
| F18-24 | 0 de 13, 0,0% (grupo pequeno) | 2 de 18, 11,1% (grupo pequeno) |
| F25-29 | 2 de 14, 14,3% (grupo pequeno) | 0 de 10, 0,0% (grupo pequeno) |
| F30-34 | 1 de 8, 12,5% (grupo pequeno) | 1 de 9, 11,1% (grupo pequeno) |
| F35-39 | 3 de 15, 20,0% (grupo pequeno) | 0 de 9, 0,0% (grupo pequeno) |
| F40-44 | 1 de 13, 7,7% (grupo pequeno) | 1 de 13, 7,7% (grupo pequeno) |
| F45-49 | 0 de 12, 0,0% (grupo pequeno) | 0 de 10, 0,0% (grupo pequeno) |
| F50-54 | 2 de 13, 15,4% (grupo pequeno) | 1 de 13, 7,7% (grupo pequeno) |
| F55-59 | 1 de 11, 9,1% (grupo pequeno) | 3 de 10, 30,0% (grupo pequeno) |
| F60-64 | 0 de 16, 0,0% (grupo pequeno) | 0 de 13, 0,0% (grupo pequeno) |
| F65+ | 0 de 2, 0,0% (grupo pequeno) | 1 de 7, 14,3% (grupo pequeno) |
| M18-24 | 3 de 38, 7,9% | 5 de 34, 14,7% |
| M25-29 | 3 de 30, 10,0% | 2 de 44, 4,5% |
| M30-34 | 0 de 23, 0,0% | 2 de 29, 6,9% |
| M35-39 | 2 de 30, 6,7% | 3 de 31, 9,7% |
| M40-44 | 3 de 35, 8,6% | 3 de 44, 6,8% |
| M45-49 | 4 de 29, 13,8% | 4 de 31, 12,9% |
| M50-54 | 1 de 28, 3,6% | 8 de 31, 25,8% |
| M55-59 | 0 de 32, 0,0% | 5 de 35, 14,3% |
| M60-64 | 4 de 31, 12,9% | 1 de 33, 3,0% |
| M65+ | 1 de 12, 8,3% (grupo pequeno) | 2 de 17, 11,8% (grupo pequeno) |

![Desistência por categoria](figuras/categorias.png)

## Limitações

- A natação não é comparada: 3,8 km em 2024, 1,9 km em 2025. Nem o ritmo por 100 m resolve, porque a condição que mudou a distância também mudou a água.
- As condições mudaram: máxima de 24 °C em 2024 e 31 °C em 2025; ficha de 2025: natação reduzida por correnteza; corrida com calor. As diferenças de tempo e de desistência comparam as edições como elas foram, sem separar o efeito de cada mudança.
- A mediana da T1 usa 367 tempos em 2024 e 392 em 2025: 4 e 1 pessoas que concluíram estão sem esse tempo.
- A mediana da T2 usa 370 tempos em 2024 e 388 em 2025: 1 e 5 pessoas que concluíram estão sem esse tempo.
- Em 2024, 11 de 20 categorias têm menos de 20 pessoas que largaram. Elas aparecem com o "x de y" e ficam fora do ranking.
- Em 2025, 11 de 20 categorias têm menos de 20 pessoas que largaram. Elas aparecem com o "x de y" e ficam fora do ranking.
- As categorias não têm as mesmas pessoas nos dois anos: 180 atletas correram as duas edições, e 32 deles mudaram de categoria.
- Os dados mostram o que aconteceu na prova. Eles não mostram por que aconteceu: treino, calor, equipamento e quem decidiu se inscrever ficam fora da base.

## De onde vêm os números

- Base: `base_triatlo.csv`, 880 inscrições, sha256 `63041a14d515`.
- Ficha das edições: `edicoes.csv`, com as distâncias, a temperatura máxima e a observação.
- Tempo de etapa: mediana de quem concluiu, sem os tempos vazios. Desistência: DNF dividido por quem largou (concluiu, DNF ou DSQ). Diferença: a edição mais recente menos a anterior.
- Gerado em 11/11/2026 às 11:37.
- Para gerar de novo: `python3 balanco.py`.
