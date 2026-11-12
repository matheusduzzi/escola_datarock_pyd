"""Roda uma lista de etapas sobre uma tabela e conta o que cada uma fez.

Cada etapa diz o tipo dela: limpeza, regra ou imputação. O tipo é uma promessa, e o rodar
checa a promessa antes de seguir para a próxima etapa:

- toda etapa: não cria linha, não muda coluna que ela não declarou em `muda`;
- limpeza: não preenche valor vazio;
- regra: diz o motivo (quem decidiu e por quê);
- imputação: diz o motivo, não tira linha, só muda célula que estava vazia e marca cada
  célula preenchida na coluna `<coluna>_preenchido`.

Se uma etapa quebra a promessa, o rodar para com ErroDeEtapa e diz qual foi.
"""
from dataclasses import dataclass
from typing import Callable, Dict, Sequence, Tuple

import pandas as pd

TIPOS = ('limpeza', 'regra', 'imputação')


class ErroDeEtapa(Exception):
    pass


@dataclass
class Etapa:
    tipo: str
    nome: str
    funcao: Callable[[pd.DataFrame], pd.DataFrame]
    muda: Tuple[str, ...] = ()
    motivo: str = ''


def _iguais(a, b):
    """Compara duas colunas célula a célula; vazio com vazio conta como igual."""
    a, b = a.astype(object), b.astype(object)
    return (a == b) | (a.isna() & b.isna())


def _checar(etapa, antes, depois):
    erro = lambda texto: ErroDeEtapa(f'{etapa.nome} ({etapa.tipo}): {texto}')
    if etapa.tipo not in TIPOS:
        raise erro(f'tipo desconhecido; use {", ".join(TIPOS)}')
    if not isinstance(depois, pd.DataFrame):
        raise erro('a função precisa retornar uma tabela')
    if etapa.tipo in ('regra', 'imputação') and not etapa.motivo.strip():
        raise erro('falta o motivo')
    if not depois.index.is_unique:
        raise erro('o índice tem linhas repetidas')
    novas = depois.index.difference(antes.index)
    if len(novas):
        raise erro(f'criou {len(novas)} linha(s)')
    sumiram = [c for c in antes.columns if c not in depois.columns]
    if sumiram:
        raise erro(f'tirou a(s) coluna(s) {sumiram}')
    marcas = [f'{c}_preenchido' for c in etapa.muda] if etapa.tipo == 'imputação' else []
    criadas = [c for c in depois.columns if c not in antes.columns and c not in etapa.muda and c not in marcas]
    if criadas:
        raise erro(f'criou a(s) coluna(s) {criadas} sem declarar')
    a, d = antes.loc[depois.index], depois
    for c in antes.columns:
        if c in etapa.muda or c in marcas:
            continue
        mudou = int((~_iguais(a[c], d[c])).sum())
        if mudou:
            raise erro(f'mudou {mudou} célula(s) da coluna {c}, que ela não declarou')
    if etapa.tipo == 'limpeza':
        for c in antes.columns:
            preenchidas = int((a[c].isna() & d[c].notna()).sum())
            if preenchidas:
                raise erro(f'preencheu {preenchidas} valor(es) vazio(s) da coluna {c}; preencher é imputação ou regra')
    if etapa.tipo == 'imputação':
        if len(depois) != len(antes):
            raise erro(f'tirou {len(antes) - len(depois)} linha(s); imputação só preenche')
        for c, m in zip(etapa.muda, marcas):
            if c not in antes.columns:
                raise erro(f'a coluna {c} não existe')
            mexidas = int((a[c].notna() & ~_iguais(a[c], d[c])).sum())
            if mexidas:
                raise erro(f'mudou {mexidas} valor(es) que já existiam na coluna {c}')
            if m not in d.columns or d[m].dtype != bool:
                raise erro(f'falta a coluna {m}, verdadeira onde o valor foi preenchido')
            preenchidas = a[c].isna() & d[c].notna()
            if not (d[m] == preenchidas).all():
                raise erro(f'a coluna {m} não bate com as células preenchidas de {c}')


def _mudadas(antes, depois):
    a = antes.loc[depois.index]
    return int(sum((~_iguais(a[c], depois[c])).sum() for c in antes.columns if c in depois.columns))


def rodar(tabela: pd.DataFrame, etapas: Sequence[Etapa], acompanhar: Sequence[str] = (),
          medidas: Dict[str, Callable[[pd.DataFrame], object]] = None):
    """Roda as etapas em ordem. Retorna (tabela final, contagens).

    contagens tem uma linha por etapa: linhas antes e depois, células mudadas, vazios de cada
    coluna de `acompanhar` antes e depois, e cada medida calculada depois da etapa.
    A primeira linha, "entrada", mostra a tabela como chegou.
    """
    medidas = medidas or {}
    linhas = []

    def foto(nome, tipo, antes, depois):
        l = {'etapa': nome, 'tipo': tipo, 'linhas antes': len(antes), 'linhas depois': len(depois),
             'células mudadas': _mudadas(antes, depois)}
        for c in acompanhar:
            l[f'{c} vazio antes'] = int(antes[c].isna().sum())
            l[f'{c} vazio depois'] = int(depois[c].isna().sum())
        for nome_medida, f in medidas.items():
            l[nome_medida] = f(depois)
        return l

    atual = tabela.copy()
    linhas.append(foto('entrada', '', atual, atual))
    for etapa in etapas:
        depois = etapa.funcao(atual.copy())
        _checar(etapa, atual, depois)
        linhas.append(foto(etapa.nome, etapa.tipo, atual, depois))
        atual = depois
    return atual, pd.DataFrame(linhas)


def mostrar(contagens: pd.DataFrame):
    """Imprime as contagens juntando cada par antes/depois numa coluna só: "antes → depois"."""
    t = pd.DataFrame({'etapa': contagens['etapa'], 'tipo': contagens['tipo']})
    for c in contagens.columns:
        if c.endswith(' antes'):
            nome = c[:-len(' antes')]
            t[nome] = contagens[c].astype(str) + ' → ' + contagens[nome + ' depois'].astype(str)
        elif not c.endswith(' depois') and c not in t.columns:
            t[c] = contagens[c]
    t = t.rename(columns={'células mudadas': 'mudadas'})
    colunas = list(t.columns)
    valores = [[str(v) for v in t[c]] for c in colunas]
    largura = [max(len(c), *(len(v) for v in vs)) for c, vs in zip(colunas, valores)]
    linhas = ['  '.join(c.ljust(n) for c, n in zip(colunas, largura)).rstrip()]
    for i in range(len(t)):
        linhas.append('  '.join(vs[i].ljust(n) for vs, n in zip(valores, largura)).rstrip())
    return '\n'.join(linhas)
