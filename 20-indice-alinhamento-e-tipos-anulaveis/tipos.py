"""Como o pandas guarda o valor vazio em cada tipo de coluna.

Uso, de dentro da pasta da aula:
    python3 tipos.py

Mostra o tipo das colunas lidas, o número de peito que vira número com vírgula, a contagem de
quem melhorou com e sem tipo anulável, o filtro com vazio e o tipo do texto no pandas 3.
"""
import pandas as pd

from resultados import ler

tabela = ler().drop_duplicates()
r24 = tabela[tabela['edicao'] == 2024].set_index('id_atleta')
r25 = tabela[tabela['edicao'] == 2025].set_index('id_atleta')

print('1. tipos lidos')
for col in ['numero_peito', 'ciclismo', 'status']:
    print(f'   {col:<13} {str(tabela[col].dtype):<8} vazios: {tabela[col].isna().sum()}')

print()
print('2. o peito de 2024, nos atletas de 2025')
peito = r24['numero_peito'].reindex(r25.index)
print(f'   int64 -> {peito.dtype}: ' + ', '.join(str(v) for v in peito.head(3)))
peito = r24['numero_peito'].astype('Int64').reindex(r25.index)
print(f'   Int64 -> {peito.dtype}: ' + ', '.join(str(v) for v in peito.head(3)))

print()
print('3. quem melhorou o ciclismo')
dif = r25['ciclismo'] - r24['ciclismo']
melhorou = dif < 0
print(f'   float64: melhorou {melhorou.sum()} | não melhorou {(~melhorou).sum()} | '
      f'piorou {(dif > 0).sum()} | total {len(dif)}')
dif = r25['ciclismo'].astype('Int64') - r24['ciclismo'].astype('Int64')
melhorou = dif < 0
print(f'   Int64:   melhorou {melhorou.sum()} | não melhorou {(~melhorou).sum()} | '
      f'sem dado {melhorou.isna().sum()} | tipo de melhorou: {melhorou.dtype}')

print()
print('4. filtrar com vazio na máscara')
mascara = pd.Series([True, None, False])
try:
    pd.Series([1, 2, 3])[mascara]
except ValueError as erro:
    print(f'   object:  ValueError: {erro}')
mascara = pd.Series([True, None, False], dtype='boolean')
print(f'   boolean: {pd.Series([1, 2, 3])[mascara].tolist()}')

print()
print('5. texto')
print(f'   status, pandas {pd.__version__}: {tabela["status"].dtype}')
with pd.option_context('future.infer_string', True):
    status = pd.Series(['concluiu', None])
    print(f'   com o tipo de texto do pandas 3: {status.dtype}, vazio: {status[1]}')
