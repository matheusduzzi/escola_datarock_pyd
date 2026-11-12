"""A diferença do ciclismo de 2024 para 2025, atleta por atleta, com o índice no id_atleta.

Uso, de dentro da pasta da aula:
    python3 por_atleta.py

Primeiro subtrai com as cópias que a API repete, depois sem elas. Conta de onde vem cada
valor vazio do resultado e quantos atletas melhoraram ou pioraram o tempo.
"""
from resultados import ler

tabela = ler()
r24 = tabela[tabela['edicao'] == 2024]
r25 = tabela[tabela['edicao'] == 2025]

c24 = r24.set_index('id_atleta')['ciclismo']
c25 = r25.set_index('id_atleta')['ciclismo']
print('índice: id_atleta')
print(f'2024: {len(c24)} linhas | índice sem repetição: {c24.index.is_unique} '
      f'({c24.index.duplicated().sum()} repetidos)')
print(f'2025: {len(c25)} linhas | índice sem repetição: {c25.index.is_unique} '
      f'({c25.index.duplicated().sum()} repetidos)')
dif = c25 - c24
print(f'com as cópias: {len(dif)} linhas no resultado | atleta 47: '
      f'{(c24.index == 47).sum()} em 2024, {(c25.index == 47).sum()} em 2025, {(dif.index == 47).sum()} no resultado')

print()
c24 = r24.drop_duplicates().set_index('id_atleta')['ciclismo']
c25 = r25.drop_duplicates().set_index('id_atleta')['ciclismo']
dif = c25 - c24
so24 = c24.index.difference(c25.index)
so25 = c25.index.difference(c24.index)
duas = c24.index.intersection(c25.index)
print(f'sem as cópias: 2024 {len(c24)} | 2025 {len(c25)} | resultado {len(dif)}')
print(f'  só em 2024: {len(so24)} | só em 2025: {len(so25)} | nas duas: {len(duas)}')
print(f'  nas duas, sem ciclismo em uma delas: {dif[duas].isna().sum()}')
print(f'  com diferença: {dif.notna().sum()} | vazias: {dif.isna().sum()}')
print(f'mediana da diferença: {dif.median() / 60:+.1f} min | média: {dif.mean() / 60:+.1f} min')
print(f'melhoraram: {(dif < 0).sum()} | pioraram: {(dif > 0).sum()}')
