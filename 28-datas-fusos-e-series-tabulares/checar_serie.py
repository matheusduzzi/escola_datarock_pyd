"""Checa uma série diária antes de ela ir para um gráfico ou uma média.

    problemas = checar(serie, '2026-01-01', '2026-06-30', medidas=['total'], cobertura='cobertura',
                       sem_dado={'parcial'})

Retorna a lista de problemas encontrados; lista vazia quer dizer que a série passou. O que ela olha:
- a coluna dia existe, é um dia (AAAA-MM-DD), sem hora e sem fuso;
- cada dia do calendário aparece uma vez, em ordem, sem faltar nem sobrar;
- a coluna de cobertura está preenchida em todo dia;
- cada medida é vazia nos dias sem dado e é um número inteiro, de 0 para cima, nos outros.
"""
import pandas as pd


def _dias(coluna):
    if pd.api.types.is_datetime64_any_dtype(coluna):
        if getattr(coluna.dt, 'tz', None) is not None:
            return None, 'a coluna dia tem fuso: guarde só o dia (AAAA-MM-DD)'
        if (coluna.dt.normalize() != coluna).any():
            return None, 'a coluna dia tem hora: guarde só o dia (AAAA-MM-DD)'
        return coluna.dt.strftime('%Y-%m-%d'), None
    texto = coluna.astype('string')
    if not texto.str.fullmatch(r'\d{4}-\d{2}-\d{2}').fillna(False).all():
        return None, 'a coluna dia tem valor que não é um dia AAAA-MM-DD: ' + str(
            texto[~texto.str.fullmatch(r'\d{4}-\d{2}-\d{2}').fillna(False)].iloc[0])
    return texto, None


def checar(serie, inicio, fim, medidas, cobertura, sem_dado):
    problemas = []
    faltam_colunas = [c for c in ['dia', cobertura, *medidas] if c not in serie.columns]
    if faltam_colunas:
        return [f'faltam as colunas: {", ".join(faltam_colunas)}']
    dias, erro = _dias(serie['dia'])
    if erro:
        return [erro]
    calendario = pd.date_range(inicio, fim, freq='D').strftime('%Y-%m-%d')
    repetidos = dias[dias.duplicated()]
    if len(repetidos):
        problemas.append(f'dias repetidos: {len(repetidos)} (ex.: {repetidos.iloc[0]})')
    faltam = calendario.difference(dias)
    if len(faltam):
        problemas.append(f'dias que faltam: {len(faltam)} (ex.: {faltam[0]})')
    sobram = pd.Index(dias.unique()).difference(calendario)
    if len(sobram):
        problemas.append(f'dias fora de {inicio} a {fim}: {len(sobram)} (ex.: {sobram[0]})')
    if not dias.is_monotonic_increasing:
        problemas.append('os dias não estão em ordem')
    cob = serie[cobertura]
    if cob.isna().any():
        problemas.append(f'dias com {cobertura} vazia: {int(cob.isna().sum())}')
    sem = cob.isin(sem_dado).to_numpy()
    for m in medidas:
        valor = pd.to_numeric(serie[m], errors='coerce')
        if (valor.isna() & serie[m].notna()).any():
            problemas.append(f'{m} tem valor que não é número')
        vazio = valor.isna().to_numpy()
        if (~vazio & sem).any():
            problemas.append(f'{m} com valor em dia sem dado: {int((~vazio & sem).sum())} (ex.: {dias[~vazio & sem].iloc[0]})')
        if (vazio & ~sem).any():
            problemas.append(f'{m} vazio em dia com dado: {int((vazio & ~sem).sum())} (ex.: {dias[vazio & ~sem].iloc[0]})')
        com = valor[~vazio]
        if (com < 0).any() or (com != com.round()).any():
            problemas.append(f'{m} tem valor negativo ou com casa decimal')
    return problemas
