# Competição de triatlo

Os dados do projeto final. A competição, os atletas e os tempos são inventados; nenhum número vem de prova real. São duas edições de uma prova de longa distância, em 2024 e 2025.

| Arquivo | Uma linha é | Colunas |
|---|---|---|
| `edicoes.csv` | uma edição | edicao, data_prova, natacao_km, ciclismo_km, corrida_km, temperatura_max_c, observacao |
| `atletas.csv` | um atleta | id_atleta, nome, sexo, ano_nascimento, uf |
| `inscricoes_2024.csv` | uma inscrição em 2024 | id_inscricao, id_atleta, numero_peito, categoria, equipe |
| `inscricoes_2025.csv` | uma inscrição em 2025 | as mesmas colunas, separadas por `;` |
| `api_resultados.json` | um resultado, servido pela API local | edicao, id_inscricao, numero_peito, status, parciais, tempo_oficial, motivo |

Os arquivos de inscrição vieram de origens diferentes: o de 2024 usa vírgula e o de 2025 usa ponto e vírgula. Um atleta pode aparecer nas duas edições, com o mesmo `id_atleta` e inscrições diferentes.

`categoria` junta o sexo e a faixa de idade no ano da prova, por exemplo `F40-44`. `equipe` vazia quer dizer atleta sem equipe.

Os resultados chegam pela API local (veja `../../api/LEIA-ME.md`). Cada resultado tem:

- `status`: `concluiu`, `DNF` (largou e não terminou), `DNS` (inscrito que não largou) ou `DSQ` (desclassificado);
- `parciais`: os tempos de natação, primeira transição (`t1`), ciclismo, segunda transição (`t2`) e corrida, no formato `H:MM:SS`. Parcial `null` quer dizer que o tempo não existe, não que foi zero;
- `tempo_oficial`: o tempo final de quem concluiu, `null` para os outros;
- `motivo`: só nos desclassificados.

Veja `edicoes.csv` antes de comparar as duas edições: a distância da natação e o calor não foram os mesmos.

Para gerar os arquivos de novo, de dentro desta pasta:

```bash
python3 gerar.py
```

O gerador só usa a biblioteca padrão e sempre escreve os mesmos arquivos.
