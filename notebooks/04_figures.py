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
# # 04 — Figures
#
# Written by `pipeline/02_mhw.py`, `pipeline/04_climatedt_mhw.py`, `pipeline/05_subsurface.py` and
# `pipeline/99_doc_figures.py`, and committed in `figures/`.
#
# ## Sea of Marmara: annual heatwave days and events
# ![Marmara annual heatwaves](../figures/marmara_mhw_annual.png)
#
# ## Heatwave days, fixed and detrended baselines
# ![Marmara heatwave days](../figures/doc_marmara_days.png)
#
# ## OSTIA against Climate DT (IFS-FESOM, IFS-NEMO)
# ![Climate DT heatwaves](../figures/marmara_climatedt_mhw.png)
#
# ## Below the surface on heatwave days
# ![Sub-surface profile](../figures/marmara_subsurface.png)

# %% [markdown]
# ## Limits
# - Sub-regions are IHO seas, not the paper's clusters (the paper's Marmara cluster MS-C5 is close to the IHO Sea of
#   Marmara).
# - Our Python detection agrees with the reference Python implementation, not checked against the MATLAB one.
# - Surface temperature only; mucilage itself is not modelled.
