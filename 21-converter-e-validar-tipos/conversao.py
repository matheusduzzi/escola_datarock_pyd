"""Funções que convertem uma coluna de texto e dizem o que não converteu, e por quê.

Cada função recebe a coluna como veio do arquivo e retorna duas colunas com o mesmo índice:
os valores convertidos e o motivo de cada rejeição. O motivo fica vazio (<NA>) quando o valor
converteu e quando a célula já estava vazia no arquivo: vazio na origem não é rejeição.
"""
import pandas as pd


def texto(coluna):
    """A coluna como texto, sem espaço nas pontas. Célula vazia vira <NA>."""
    t = coluna.astype('string').str.strip()
    return t.mask(t == '')


def forma(coluna):
    """O desenho de cada valor: cada dígito vira 9. Serve para ver os jeitos de escrever antes de converter."""
    return texto(coluna).str.replace(r'\d', '9', regex=True).fillna('(vazio)')


def _motivos(indice):
    return pd.Series(pd.NA, index=indice, dtype='string')


def _casa(t, padrao):
    return t.str.fullmatch(padrao).fillna(False).astype(bool)


def numero_br(coluna, permitidos=None):
    """Valores em reais escritos à mão (1.150,00 | 1150,00 | 1150 | R$ 980,00) ou pelo app (1150.00).

    Ponto seguido de três dígitos é milhar; ponto seguido de dois dígitos no fim é centavo.
    Com permitidos, um número fora dessa lista é rejeitado com o motivo 'fora da tabela de preços'.
    """
    t = texto(coluna).str.replace(r'^R\$\s*', '', regex=True)
    milhar = _casa(t, r'\d{1,3}(?:\.\d{3})+(?:,\d{2})?')
    virgula = _casa(t, r'\d+(?:,\d{2})?')
    ponto = _casa(t, r'\d+\.\d{2}')
    limpo = t.where(~milhar, t.str.replace('.', '', regex=False))
    limpo = limpo.where(ponto, limpo.str.replace(',', '.', regex=False))
    aceito = milhar | virgula | ponto
    valores = pd.to_numeric(limpo.where(aceito), errors='coerce').astype('Float64')
    motivo = _motivos(coluna.index)
    motivo[t.notna() & ~aceito] = 'não é número'
    if permitidos is not None:
        fora = valores.notna() & ~valores.isin(permitidos)
        motivo[fora] = 'fora da tabela de preços'
        valores[fora] = pd.NA
    return valores, motivo


def data(coluna, formatos, minimo=None, maximo=None):
    """Datas escritas em um dos formatos da lista, tentados em ordem. Nada é adivinhado.

    O que parece data mas não existe no calendário (31/02) é 'data inexistente'; o que não tem
    o desenho de nenhum formato é 'formato desconhecido'; fora de minimo e maximo é 'fora da faixa'.
    """
    t = texto(coluna)
    valores = pd.Series(pd.NaT, index=coluna.index, dtype='datetime64[ns]')
    for formato in formatos:
        falta = valores.isna() & t.notna()
        valores[falta] = pd.to_datetime(t[falta], format=formato, errors='coerce')
    motivo = _motivos(coluna.index)
    nao_leu = t.notna() & valores.isna()
    desenho = _casa(t, r'\d{1,2}/\d{1,2}/\d{4}(?: \d{1,2}:\d{2})?|\d{4}-\d{2}-\d{2}')
    motivo[nao_leu & desenho] = 'data inexistente'
    motivo[nao_leu & ~desenho] = 'formato desconhecido'
    if minimo is not None or maximo is not None:
        fora = valores.notna() & ~valores.between(pd.Timestamp(minimo or '1900-01-01'),
                                                  pd.Timestamp(maximo or '2100-01-01'))
        motivo[fora] = 'fora da faixa'
        valores[fora] = pd.NaT
    return valores, motivo


def categoria(coluna, validas):
    """Texto de uma lista fechada. Antes de comparar, tira espaços e põe em maiúscula.

    Retorna também quantos valores só entraram por causa desse ajuste.
    """
    t = texto(coluna)
    ajustado = t.str.upper().str.replace(r'\s+', '', regex=True)
    ok = ajustado.isin(validas).fillna(False).astype(bool)
    valores = ajustado.where(ok).astype(pd.CategoricalDtype(validas))
    motivo = _motivos(coluna.index)
    motivo[t.notna() & ~ok] = 'categoria desconhecida'
    cru = coluna.astype('string')
    ajustes = int((ok & (ajustado != cru).fillna(False)).sum())
    return valores, motivo, ajustes


def rejeicoes(chave, original, motivos):
    """Junta os motivos de cada coluna numa tabela só: chave, coluna, valor_original, motivo.

    chave é a coluna que diz de qual linha veio cada valor (por exemplo, id_resposta).
    motivos é um dicionário {coluna: coluna de motivos}.
    """
    partes = []
    for nome, motivo in motivos.items():
        tem = motivo.notna()
        partes.append(pd.DataFrame({chave.name: chave[tem].to_numpy(), 'coluna': nome,
                                    'valor_original': original.loc[tem, nome].astype('string').to_numpy(),
                                    'motivo': motivo[tem].to_numpy()}))
    return pd.concat(partes, ignore_index=True)


def relatorio(original, convertida, rejeitadas, colunas, ajustes=None):
    """Uma linha por coluna: lidas, vazias na origem, convertidas, ajustadas e rejeitadas.

    Cada número é contado no seu lugar: vazias no arquivo, convertidas na tabela nova, rejeitadas
    na tabela de rejeições. Se nada sumiu, a conta fecha: vazias + convertidas + rejeitadas = lidas.
    """
    ajustes = ajustes or {}
    linhas = []
    for nome in colunas:
        vazias = int(texto(original[nome]).isna().sum())
        rej = int((rejeitadas['coluna'] == nome).sum())
        linhas.append({'coluna': nome, 'lidas': len(original), 'vazias': vazias,
                       'convertidas': int(convertida[nome].notna().sum()), 'ajustadas': ajustes.get(nome, 0),
                       'rejeitadas': rej})
    return pd.DataFrame(linhas)
