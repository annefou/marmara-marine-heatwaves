"""Rows of the figure shown in the LifeWatch ERIC country file for Turkiye: Sea of Marmara heatwave days per
year with the paper's baseline (1982-2021) and on the detrended series, from results/mhw_annual_marmara_*.csv.
Writes results/doc_figure_marmara_days.json.
"""
import json

import pandas as pd

MUCILAGE = (2007, 2008, 2020, 2021)
p = pd.read_csv("results/mhw_annual_marmara_paper.csv", index_col=0)
d = pd.read_csv("results/mhw_annual_marmara_detrended.csv", index_col=0)
rows = [{"year": int(y), "days": int(p.loc[y, "mhw_days"]), "days_detr": int(d.loc[y, "mhw_days"]),
         "mucilage": int(y in MUCILAGE)} for y in p.index]
json.dump(rows, open("results/doc_figure_marmara_days.json", "w"), indent=1)
print(len(rows), "rows")
