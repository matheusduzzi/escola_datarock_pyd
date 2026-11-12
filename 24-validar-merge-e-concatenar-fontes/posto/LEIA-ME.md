# As planilhas do posto de chegada

Os fiscais do posto de chegada anotam, numa planilha, quem cruzou a linha e com que tempo. Quem desistiu perto do posto entra como `DNF`, sem tempo. A comissão técnica pediu a planilha de cada edição para completar os resultados que a cronometragem não mandou.

| Arquivo | Uma linha é | Colunas |
|---|---|---|
| `posto_2025.csv` | uma anotação de um fiscal em 2025 | edicao, peito, status, tempo |
| `posto_2024.csv` | uma anotação de um fiscal em 2024 | as mesmas |

As colunas são separadas por `;`. O posto anota o número de peito, não o id da inscrição. O peito recomeça em 101 em cada edição, então a chave para achar a inscrição é a edição com o peito.

- `status`: `concluiu` ou `DNF`, com o mesmo sentido do LEIA-ME dos dados do triatlo;
- `tempo`: o tempo de quem concluiu, no formato `H:MM:SS`; vazio para `DNF`.

As planilhas estão como os fiscais mandaram. Pode ter linha repetida, peito anotado errado e resultado que a API já tem.

Para gerar os arquivos de novo, de dentro da pasta da aula:

```bash
python3 gerar_posto.py
```
