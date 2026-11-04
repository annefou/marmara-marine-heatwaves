# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 03 — Claims tested
#
# | Claim | Paper |
# |---|---|
# | M1. Sea of Marmara heatwave frequency trend, the highest of the three seas | 1.56 events per decade (cluster MS-C5) |
# | M1b. Marmara heatwave days and duration trends | 25.55 days, 5.01 days per decade |
# | M2. SST warming, strongest in the Black Sea then the Marmara | Black Sea up to 0.8, Aegean 0.3 °C per decade (grid points) |
# | M3. Mucilage years 2007–08 and 2020–21 coincide with intense, long heatwaves | qualitative |

# %%
import json
from pathlib import Path

import pandas as pd

R = Path("../results")
claims = json.loads((R / "claims.json").read_text())
print("Paper values:", json.dumps(claims["paper"], ensure_ascii=False))

# %% [markdown]
# ## M1, M1b — trends per decade (OLS with Newey–West 95 % CI; Sen slope alongside)
# Variants: `paper` (1982–2021 climatology), `wmo_1991_2020`, `hobday_1982_2011`, and `detrended` (mean warming
# removed, what is left is the change in extremes).

# %%
tr = pd.read_csv(R / "mhw_trends.csv")
tr[tr.metric.isin(["frequency", "mhw_days", "duration"])].round(2)

# %% [markdown]
# ## M2 — SST trend per sea (°C per decade, sea means)

# %%
pd.DataFrame({s: v["sst_trend_degC_per_decade"] for s, v in claims["seas"].items()}).T

# %% [markdown]
# ## M3 — mucilage years, rank among 44 years (Sea of Marmara)

# %%
pd.DataFrame(claims["seas"]["marmara"]["mucilage_years_rank_of_44"]).T

# %% [markdown]
# ## Extension: Climate DT generation 2, evaluated against OSTIA (1991–2020) and to 2049
# One realisation per model, one scenario (SSP3-7.0); both models warm more slowly than observed over 1991–2025.

# %%
dt = json.loads((R / "climatedt_claims.json").read_text())
print("cells used:", dt["cells_used"], "of", dt["cells_total"], "| baseline", dt["baseline"])
pd.DataFrame({m: {k: v for k, v in e.items() if not isinstance(v, list)} for m, e in dt["evaluation_1991_2020"].items()}).T

# %%
print(json.dumps({k: v for k, v in dt.items() if k not in ("evaluation_1991_2020",)}, indent=1)[:3000])

# %% [markdown]
# ## Extension: below the surface (Copernicus Marine 500 m model, 2022–2025)
# Basin means only; on surface heatwave days the anomaly fades with depth.

# %%
sub = json.loads((R / "subsurface_claims.json").read_text())
print("model at 1 m vs OSTIA:", sub["model_1m_vs_ostia"])
pd.DataFrame(sub["anomaly_by_depth_degC"]).T
