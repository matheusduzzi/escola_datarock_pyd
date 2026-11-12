"""O código que a IA mandou para comparar o ciclismo de 2024 com o de 2025.

Uso, de dentro da pasta da aula:
    python3 ia.py

Roda as duas versões da IA: a primeira filtra cada edição e subtrai; a segunda acrescenta
reset_index(drop=True). Depois mostra quem a segunda versão pôs lado a lado em cada linha.
"""
from resultados import ler

tabela = ler()
r24 = tabela[tabela['edicao'] == 2024]
r25 = tabela[tabela['edicao'] == 2025]
print(f'resultados no arquivo: {len(tabela)} | 2024: {len(r24)} | 2025: {len(r25)}')

# 1ª versão da IA
dif = r25['ciclismo'] - r24['ciclismo']
print(f'1ª versão: {len(dif)} linhas, {dif.isna().sum()} vazias, média da diferença: {dif.mean()}')

# 2ª versão da IA, depois de "corrigir"
a = r24.reset_index(drop=True)
b = r25.reset_index(drop=True)
dif = b['ciclismo'] - a['ciclismo']
print(f'2ª versão: {len(dif)} linhas, {dif.isna().sum()} vazias, média da diferença: {dif.mean() / 60:+.1f} min')

print()
print('quem a 2ª versão pôs lado a lado, nas 5 primeiras linhas:')
print('linha  atleta em 2024  atleta em 2025')
for i in range(5):
    print(f'{i:>5}  {a.loc[i, "id_atleta"]:>14}  {b.loc[i, "id_atleta"]:>14}')
lado_a_lado = min(len(a), len(b))
mesmo = (a['id_atleta'].iloc[:lado_a_lado] == b['id_atleta'].iloc[:lado_a_lado]).sum()
print(f'linhas com o mesmo atleta dos dois lados: {mesmo} de {lado_a_lado}')
