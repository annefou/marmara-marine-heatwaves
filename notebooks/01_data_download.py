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
# # 01 — Data
#
# **DRAFT, not reviewed.** LifeWatch ERIC feasibility test, our reading of the published work (Saçu, Şen, Erdik and
# Öztürk 2025, *Dynamics of Atmospheres and Oceans* 110:101555,
# [doi:10.1016/j.dynatmoce.2025.101555](https://doi.org/10.1016/j.dynatmoce.2025.101555)), open to correction by the
# authors.
#
# The pipeline is in `pipeline/` and `Snakefile` (see *How to reproduce* in the README). It is **not** rerun when this
# book is built: it needs a Copernicus Marine account and DestinE upgraded access (Climate DT). These pages read the
# summary results committed in `results/` and the figures in `figures/`.
#
# | Input | Source | Licence | Pipeline step |
# |---|---|---|---|
# | OSTIA L4 reprocessed SST, 0.05°, 1982–2025 (the paper's product) | Copernicus Marine SST_GLO_SST_L4_REP_OBSERVATIONS_010_011, [doi:10.48670/moi-00168](https://doi.org/10.48670/moi-00168) | Copernicus Marine licence (free account) | `pipeline/00_download.py`, `pipeline/01_healpix.py` |
# | IHO Sea Areas (instead of the paper's clusters) | Marine Regions | CC BY 4.0 | `pipeline/01_healpix.py` |
# | Climate DT generation 2 daily SST (avg_tos), IFS-FESOM and IFS-NEMO, 1990–2049 | DestinE upgraded access | DestinE terms: derived statistics only | `pipeline/03_climatedt.py` |
# | Marmara physics model at 500 m, from November 2021 | Copernicus Marine BLKSEA_ANALYSISFORECAST_PHY_007_001 | Copernicus Marine licence | `pipeline/05_subsurface.py` |
#
# Grid: HEALPix depth 10 (~6.4 km; healpix-geo, WGS84 ellipsoid, NESTED), resampled with healpix-resample
# (conservative bilinear, land excluded). Sea means are plain means over equal-area cells.

# %%
import json
from pathlib import Path

import pandas as pd

R = Path("../results")
cells = json.loads((R / "cells.json").read_text())
print("HEALPix depth", cells["healpix_depth"])
pd.DataFrame(cells["seas"]).T
