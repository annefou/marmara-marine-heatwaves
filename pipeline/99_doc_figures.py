"""Rows of the figure shown in the LifeWatch ERIC country file for Turkiye: Sea of Marmara heatwave days per
year with the paper's baseline (1982-2021) and on the detrended series, from results/mhw_annual_marmara_*.csv.
Writes results/doc_figure_marmara_days.json and figures/doc_marmara_days.png.
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

# The country-file figure as PNG, drawn from the same rows (the country file draws it live from them).
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

fig, ax = plt.subplots(figsize=(11, 4.4))
for r in rows:
    if r["mucilage"]:
        ax.axvspan(r["year"] - 0.5, r["year"] + 0.5, color="0.85", zorder=0)
ax.bar([r["year"] for r in rows], [r["days"] for r in rows], color="#2f6fd6", width=0.8,
       label="Heatwave days, baseline 1982-2021 (as in Saçu et al. 2025)")
ax.plot([r["year"] for r in rows], [r["days_detr"] for r in rows], "-o", color="0.4", ms=3, lw=1.4,
        label="Detrended series")
peak = max(rows, key=lambda r: r["days"])
ax.annotate(f"{peak['year']}: {peak['days']} days", (peak["year"], peak["days"]), xytext=(-6, 4),
            textcoords="offset points", ha="right", fontsize=9)
ax.set_ylabel("Heatwave days per year"); ax.set_ylim(0, 260)
ax.legend(frameon=False, fontsize=9, loc="upper left")
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Sea of Marmara: heatwave days reached a record in 2024; beyond the warming trend they barely rose\n"
             "OSTIA SST on HEALPix, Hobday et al. 2016; shaded: mucilage years 2007-08 and 2020-21",
             loc="left", fontsize=10)
fig.tight_layout(); fig.savefig("figures/doc_marmara_days.png", dpi=160); plt.close(fig)
