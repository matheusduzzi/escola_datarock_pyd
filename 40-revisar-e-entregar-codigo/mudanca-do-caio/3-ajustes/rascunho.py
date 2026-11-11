import pandas as pd

d = pd.read_csv("/Users/caio/Desktop/triatlo/resultados (2).csv")
print(d[d.status != "terminou"].groupby("categoria").size())
print(d.t1_s.describe())
