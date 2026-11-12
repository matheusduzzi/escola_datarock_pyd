"""Checa uma conversão de tipos: nenhuma linha perdida e nenhum valor sumido sem registro.

Uso:
    problemas = checar(original, convertida, rejeicoes, chave, tipos)

original   a tabela como veio do arquivo (tudo texto)
convertida a tabela depois da conversão, com as mesmas linhas, na mesma ordem
rejeicoes  uma linha por valor rejeitado: chave, coluna, valor_original, motivo
chave      o nome da coluna que diz de qual linha veio cada valor
tipos      {coluna: tipo esperado na convertida}, por exemplo {'valor_pago': 'Float64'}

Retorna a lista de problemas. Lista vazia quer dizer ok.
O checar não sabe se um valor convertido está certo; ele só vê se cada valor foi para algum lugar.
"""
import pandas as pd


def _texto(coluna):
    t = coluna.astype('string').str.strip()
    return t.mask(t == '')


def checar(original, convertida, rejeicoes, chave, tipos):
    problemas = []
    if len(convertida) != len(original):
        problemas.append(f'linhas: o arquivo tem {len(original)}, a convertida tem {len(convertida)}')
        return problemas
    if chave not in convertida or list(convertida[chave].astype(str)) != list(original[chave].astype(str)):
        problemas.append(f'a coluna {chave} da convertida não é a do arquivo, na mesma ordem')
        return problemas
    colunas_rej = [chave, 'coluna', 'valor_original', 'motivo']
    if list(rejeicoes.columns) != colunas_rej:
        problemas.append(f'rejeicoes precisa das colunas {", ".join(colunas_rej)}')
        return problemas
    sem_motivo = int(_texto(rejeicoes['motivo']).isna().sum())
    if sem_motivo:
        problemas.append(f'rejeições sem motivo: {sem_motivo}')
    estranhas = sorted(set(rejeicoes['coluna']) - set(tipos))
    if estranhas:
        problemas.append(f'rejeições de colunas que não estão em tipos: {", ".join(estranhas)}')
    repetidas = int(rejeicoes.duplicated([chave, 'coluna']).sum())
    if repetidas:
        problemas.append(f'o mesmo valor rejeitado mais de uma vez: {repetidas}')

    pos = {str(k): i for i, k in enumerate(original[chave])}
    for nome, tipo in tipos.items():
        if nome not in convertida:
            problemas.append(f'{nome}: falta na convertida')
            continue
        if str(convertida[nome].dtype) != tipo:
            problemas.append(f'{nome}: tipo {convertida[nome].dtype}, esperado {tipo}')
        bruto = _texto(original[nome]).to_numpy()
        novo = convertida[nome].notna().to_numpy()
        rej = rejeicoes[rejeicoes['coluna'] == nome]
        marcada = [False] * len(original)
        trocado = []
        for k, v in zip(rej[chave].astype(str), rej['valor_original']):
            i = pos.get(k)
            if i is None:
                problemas.append(f'{nome}: rejeição de uma linha que não existe ({chave} {k})')
                continue
            marcada[i] = True
            if not pd.isna(bruto[i]) and str(v).strip() != str(bruto[i]):
                trocado.append(k)
        vazio = [pd.isna(b) for b in bruto]
        sumiu = [i for i in range(len(original)) if not vazio[i] and not novo[i] and not marcada[i]]
        duas = [i for i in range(len(original)) if novo[i] and marcada[i]]
        inventado = [i for i in range(len(original)) if vazio[i] and novo[i]]
        vazio_rej = [i for i in range(len(original)) if vazio[i] and marcada[i]]
        ex = lambda lista: f' (ex.: {chave} {original[chave].iloc[lista[0]]})'
        if trocado:
            problemas.append(f'{nome}: valor_original diferente do arquivo: {len(trocado)} (ex.: {chave} {trocado[0]})')
        if sumiu:
            problemas.append(f'{nome}: valores que sumiram sem registro: {len(sumiu)}' + ex(sumiu))
        if duas:
            problemas.append(f'{nome}: valores convertidos e rejeitados ao mesmo tempo: {len(duas)}' + ex(duas))
        if inventado:
            problemas.append(f'{nome}: célula vazia no arquivo com valor na convertida: {len(inventado)}' + ex(inventado))
        if vazio_rej:
            problemas.append(f'{nome}: célula vazia registrada como rejeição: {len(vazio_rej)}' + ex(vazio_rej))
    return problemas
