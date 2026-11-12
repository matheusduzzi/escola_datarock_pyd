"""Pedido 1 da prática guiada: quatro tempos de natação, um deles vazio."""
import warnings

import numpy as np

a = np.array([4709.0, np.nan, 4459.0, 5080.0])
print(f"a = {a}")
print(f"np.mean(a)              -> {np.mean(a)}")
print(f"np.nanmean(a)           -> {np.nanmean(a):.3f}")
print(f"np.nan_to_num(a).mean() -> {np.nan_to_num(a).mean()}")
print(f"np.nanmedian(a)         -> {np.nanmedian(a)}")
print(f"(~np.isnan(a)).sum()    -> {(~np.isnan(a)).sum()}")
with warnings.catch_warnings(record=True) as avisos:
    warnings.simplefilter("always")
    vazio = np.nanmean(np.array([np.nan, np.nan]))
print(f"np.nanmean([nan, nan])  -> {vazio} | aviso: {avisos[0].category.__name__}: {avisos[0].message}")
