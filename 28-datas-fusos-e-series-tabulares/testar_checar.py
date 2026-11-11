"""Estraga a série diária de onze jeitos e vê se o checar_serie.py responde certo em cada um.

    python3 testar_checar.py

Sai com 1 se o checar_serie.py errar algum caso. Rode antes python3 gerar.py.
"""
import io
import sys

import pandas as pd

import checar_serie
import datas

ARGS = dict(inicio=datas.INICIO, fim=datas.FIM, medidas=['site', 'total'], cobertura='cobertura', sem_dado={'parcial'})


def casos(serie):
    def mudar(f):
        s = serie.copy()
        f(s)
        return s

    def com_zero(s):
        s.loc[s['dia'] == '2026-04-10', ['site', 'total']] = 0

    def com_fuso(s):
        s['dia'] = pd.to_datetime(s['dia']).dt.tz_localize(datas.FUSO)

    def com_hora(s):
        s['dia'] = pd.to_datetime(s['dia']) + pd.Timedelta(hours=3)

    def com_decimal(s):
        s['total'] = s['total'].astype('Float64')
        s.loc[s['dia'] == '2026-04-11', 'total'] = 20.5

    def sem_cobertura(s):
        s.loc[s['dia'] == '2026-04-11', 'cobertura'] = None

    lido = pd.read_csv(io.StringIO(serie.to_csv(index=False)))
    domingo = pd.to_datetime(serie['dia']).dt.dayofweek == 6
    extra = serie.iloc[[-1]].assign(dia='2026-07-01')
    return [
        ('a série certa', serie, True),
        ('a série gravada em CSV e lida de volta', lido, True),
        ('o dia parcial com 0 no lugar do vazio', mudar(com_zero), False),
        ('sem os domingos, como sai do groupby da loja', serie[~domingo], False),
        ('um dia repetido', pd.concat([serie, serie.iloc[[100]]]).sort_values('dia'), False),
        ('um dia a mais, 2026-07-01', pd.concat([serie, extra]), False),
        ('os dias fora de ordem', serie.sample(frac=1, random_state=1), False),
        ('a coluna dia com fuso', mudar(com_fuso), False),
        ('a coluna dia com hora', mudar(com_hora), False),
        ('um total com casa decimal', mudar(com_decimal), False),
        ('um dia sem cobertura', mudar(sem_cobertura), False),
    ]


def main():
    serie = datas.montar_serie()[0]
    erros = 0
    for nome, s, passa in casos(serie):
        problemas = checar_serie.checar(s, **ARGS)
        certo = (not problemas) == passa
        erros += not certo
        disse = 'ok' if not problemas else problemas[0]
        print(f'{"certo" if certo else "ERRADO"}  {nome}: esperado {"ok" if passa else "problema"}, checar disse: {disse}')
    print(f'{erros} caso(s) com resposta errada')
    sys.exit(1 if erros else 0)


if __name__ == '__main__':
    main()
