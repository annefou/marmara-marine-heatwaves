"""Sea of Marmara marine heatwaves to 2049 in the Climate DT (IFS-FESOM, IFS-NEMO; SSP3-7.0), set against OSTIA.

Inputs: OSTIA on the 290 Marmara cells (<ROOT>/hp/marmara.nc, 01_healpix.py) and the Climate DT daily SST on the
same cells (<ROOT>/dt/<MODEL>/<year>.npz, 03_climatedt.py). All sources are averaged over the same cells: those at
least half covered by sea in both models.
1. Evaluation, 1991-2020: mean bias, monthly climatology, spread of daily anomalies, SST trend (1991-2025 for
   OSTIA and for the model's historical + SSP3-7.0 run). The Climate DT runs are free climate simulations: their
   weather does not follow the observed days, so only statistics are compared.
2. Heatwaves (Hobday et al. 2016, pipeline/mhw.py) with a fixed baseline 1991-2020, each source against its own
   climatology (removes the model's mean bias): heatwave days per year and per decade, 1991-2049.
3. The same on the detrended series (linear trend of the whole record removed): change in variability alone.
Writes results/climatedt_mhw_annual_<source>_<variant>.csv, results/climatedt_claims.json,
results/doc_figure_marmara_climatedt.json and figures/marmara_climatedt_mhw.png.
Usage: python pipeline/04_climatedt_mhw.py <ROOT>
"""
import glob
import json
import os
import sys

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mhw  # noqa: E402

ROOT = sys.argv[1]
MODELS = ["IFS-FESOM", "IFS-NEMO"]
BASE = (1991, 2020)
DECADES = [(1991, 2000), (2001, 2010), (2011, 2020), (2021, 2030), (2031, 2040), (2040, 2049)]


def load_model(model):
    files = sorted(glob.glob(f"{ROOT}/dt/{model}/*.npz"))
    d = [np.load(f) for f in files]
    dates = pd.to_datetime(np.concatenate([x["dates"] for x in d]))
    return dates, np.concatenate([x["sst"] for x in d]), d[0]["share"], d[0]["cells"]


def run(t, x, detr):
    if detr:
        x, _ = mhw.detrend(t, x)
    seas, thr = mhw.climatology(t, x, BASE)
    ev, inm, anom = mhw.detect(t, x, seas, thr)
    return mhw.annual(t, x, inm, anom, ev, thresholds=())


def main():
    os.makedirs("results", exist_ok=True)
    ost = xr.open_dataset(f"{ROOT}/hp/marmara.nc")
    models = {m: load_model(m) for m in MODELS}
    cells = ost.cell.values.astype(np.uint64)
    keep = np.ones(cells.size, bool)
    for m, (_, _, share, mc) in models.items():
        assert np.array_equal(np.sort(cells), mc)
        keep &= pd.Series(share, index=mc).reindex(cells).values >= 0.5
    series = {"OSTIA": ost.sst.isel(cell=np.flatnonzero(keep)).mean("cell").to_series()}
    series["OSTIA"] = series["OSTIA"][series["OSTIA"].index.year <= 2025]
    pos = {m: np.searchsorted(models[m][3], cells[keep]) for m in MODELS}
    for m in MODELS:
        t, s, _, _ = models[m]
        series[m] = pd.Series(np.nanmean(s[:, pos[m]], 1), index=t)

    claims = {"cells_used": int(keep.sum()), "cells_total": int(cells.size), "baseline": list(BASE),
              "evaluation_1991_2020": {}, "sst_trend_degC_per_decade": {}, "mhw_days_per_decade": {},
              "mhw_days_per_decade_detrended": {}}
    annual = {}
    ref = series["OSTIA"]["1991":"2020"]
    ref_clim = ref.groupby(ref.index.month).mean()
    for src, s in series.items():
        b = s["1991":"2020"]
        clim = b.groupby(b.index.month).mean()
        anom = b - b.groupby(b.index.dayofyear).transform("mean")
        claims["evaluation_1991_2020"][src] = {
            "mean_degC": round(float(b.mean()), 2), "bias_vs_ostia_degC": round(float(b.mean() - ref.mean()), 2),
            "warmest_month_degC": round(float(clim.max()), 2), "coldest_month_degC": round(float(clim.min()), 2),
            "monthly_clim_bias_degC": [round(float(v), 2) for v in (clim - ref_clim).values],
            "daily_anomaly_sd_degC": round(float(anom.std()), 2)}
        ann = s.groupby(s.index.year).mean()
        per = {"1991_2025": (1991, 2025)} if src == "OSTIA" else {"1991_2025": (1991, 2025), "1991_2049": (1991, 2049),
                                                                 "2021_2049": (2021, 2049)}
        claims["sst_trend_degC_per_decade"][src] = {
            k: round(mhw.trend(ann.loc[a:b].index, ann.loc[a:b].values)["ols"], 3) for k, (a, b) in per.items()}
        for detr, key in ((False, "mhw_days_per_decade"), (True, "mhw_days_per_decade_detrended")):
            a = run(s.index, s.values.astype(float), detr)
            a.to_csv(f"results/climatedt_mhw_annual_{src}_{'detrended' if detr else 'fixed_1991_2020'}.csv")
            claims[key][src] = {f"{y0}-{y1}": round(float(a.mhw_days.loc[y0:y1].mean()), 1)
                                for y0, y1 in DECADES if a.index.max() >= y1}
            if not detr:
                annual[src] = a
    json.dump(claims, open("results/climatedt_claims.json", "w"), indent=1)
    print(json.dumps(claims, indent=1))

    rows = [{"source": src, "year": int(y), "days": int(annual[src].loc[y, "mhw_days"])}
            for src in ["OSTIA"] + MODELS for y in annual[src].index if y >= 1991]
    json.dump(rows, open("results/doc_figure_marmara_climatedt.json", "w"), indent=1)

    fig, ax = plt.subplots(figsize=(11, 4.4))
    col = {"OSTIA": "0.25", "IFS-FESOM": "#2f6fd6", "IFS-NEMO": "#8fb3ea"}
    for src in ["OSTIA"] + MODELS:
        a = annual[src].loc[1991:]
        ax.plot(a.index, a.mhw_days, "-o", ms=3, lw=1.4, color=col[src],
                label="OSTIA (observed)" if src == "OSTIA" else f"Climate DT {src}, SSP3-7.0 from 2015")
    ax.axvspan(BASE[0] - 0.5, BASE[1] + 0.5, color="0.93", zorder=0)
    ax.set_ylabel("Heatwave days per year")
    ax.set_title("Sea of Marmara heatwave days, each source against its own 1991-2020 climatology (shaded)",
                 loc="left", fontsize=10)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig("figures/marmara_climatedt_mhw.png", dpi=160); plt.close(fig)


if __name__ == "__main__":
    main()
