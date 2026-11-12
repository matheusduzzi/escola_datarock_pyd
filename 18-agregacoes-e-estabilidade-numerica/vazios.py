"""Onde estão as parciais vazias de 2025, por status. Seção 2 da aula."""
import numpy as np

import parciais

r = parciais.carregar()
de_2025 = r["edicao"] == 2025
tempos = r["tempos"][de_2025]
status = r["status"][de_2025]

print(f"2025: {len(tempos)} inscrições | tempos.shape: {tempos.shape}")
print("Parciais vazias por status")
print(f"{'status':<10}{'linhas':>7}" + "".join(f"{e:>10}" for e in parciais.ETAPAS))
for s in ("concluiu", "DNF", "DNS", "DSQ"):
    vazio = np.isnan(tempos[status == s]).sum(axis=0)
    print(f"{s:<10}{(status == s).sum():>7}" + "".join(f"{v:>10}" for v in vazio))
vazio = np.isnan(tempos).sum(axis=0)
print(f"{'total':<10}{len(tempos):>7}" + "".join(f"{v:>10}" for v in vazio))
