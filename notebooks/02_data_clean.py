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
# # 02 — Heatwave detection and its check
#
# Hobday et al. 2016 detection: 11-day window, 90th percentile, 31-day smoothing, at least 5 days, gaps of up to
# 2 days joined. The paper used a MATLAB toolbox (Zhao and Marin 2019); ours is checked against the reference Python
# implementation (Oliver, marineHeatWaves, commit d7292bf) by `pipeline/09_check_reference.py`.

# %%
import json
from pathlib import Path

import pandas as pd

R = Path("../results")
ref = json.loads((R / "reference_check.json").read_text())
print("reference:", ref["reference"])
pd.DataFrame({k: v for k, v in ref.items() if isinstance(v, dict)}).T

# %% [markdown]
# Annual series for the Sea of Marmara, paper baseline (1982–2021 climatology):

# %%
pd.read_csv(R / "mhw_annual_marmara_paper.csv").tail(10)
