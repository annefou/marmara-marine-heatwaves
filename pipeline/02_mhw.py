"""Marine heatwave claims of Sacu et al. 2025 tested on the sea-mean SST series (HEALPix, 01_healpix.py).

The paper (Dyn. Atmos. Oceans 110:101555): Hobday et al. 2016 definition (Zhao and Marin 2019 toolbox),
baseline 1982-2021 (the whole record), OSTIA REP 0.05 deg, MHW metrics on the spatial-mean SST of each
sub-region; Marmara (cluster MS-C5) trends per decade 1982-2021: frequency 1.56 events, days 25.55,
duration 5.01 (Table 2); mucilage outbreaks 2007-2008 and 2020-2021.
Our sub-regions are the IHO seas (the paper's Black Sea and Aegean clusters are not reproduced; their
cluster ranges are given for comparison). Detection: pipeline/mhw.py (checked against Oliver's
marineHeatWaves reference, pipeline/09_check_reference.py).
Variants (the paper's is "paper"): baseline 1982-2021 (paper) | 1991-2020 (WMO normal) | 1982-2011
(Hobday's 30-year default) | 1982-2021 on the detrended series (extremes beyond the warming trend).
Periods: 1982-2021 (paper) and 1982-2025 (extended).

Usage: python pipeline/02_mhw.py <ROOT>
Writes results/mhw_trends.csv, results/mhw_annual_<sea>_<variant>.csv, results/claims.json, figures/*.png.
"""
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
SEAS = ["marmara", "black", "aegean"]
VARIANTS = {"paper": ((1982, 2021), False), "wmo_1991_2020": ((1991, 2020), False),
            "hobday_1982_2011": ((1982, 2011), False), "detrended": ((1982, 2021), True)}
PAPER = {"marmara": {"frequency": 1.56, "mhw_days": 25.55, "duration": 5.01},
         "black": {"frequency": [1.23, 1.55], "mhw_days": [20.89, 28.31], "duration": [2.54, 11.28]},
         "aegean": {"frequency": [1.06, 1.21], "mhw_days": [23.45, 27.62], "duration": [5.38, 17.05]}}
MUCILAGE = [2007, 2008, 2020, 2021]


def run(t, x, base, detr):
    if detr:
        x, _ = mhw.detrend(t, x)
    seas, thr = mhw.climatology(t, x, base)
    ev, inm, anom = mhw.detect(t, x, seas, thr)
    ann = mhw.annual(t, x, inm, anom, ev, thresholds=())
    dur = ev.groupby(ev.start.dt.year).duration.mean() if len(ev) else pd.Series(dtype=float)
    ann["duration"] = dur.reindex(ann.index)
    return ann, ev


def main():
    os.makedirs("results", exist_ok=True)
    os.makedirs("figures", exist_ok=True)
    rows, claims, series = [], {"paper": PAPER, "seas": {}}, {}
    for sea in SEAS:
        ds = xr.open_dataset(f"{ROOT}/hp/{sea}.nc")
        s = ds.sst.mean("cell").to_series()
        s = s[s.index.year <= 2025]
        t, x = s.index, s.values.astype(float)
        ann_t = s.groupby(s.index.year).mean()
        sst_tr = {p: mhw.trend(ann_t.loc[y0:y1].index, ann_t.loc[y0:y1].values) for p, (y0, y1) in
                  {"1982_2021": (1982, 2021), "2000_2021": (2000, 2021), "1982_2025": (1982, 2025)}.items()}
        claims["seas"][sea] = {"cells": int(ds.sizes["cell"]),
                               "sst_trend_degC_per_decade": {k: round(v["ols"], 3) for k, v in sst_tr.items()}}
        for vname, (base, detr) in VARIANTS.items():
            ann, ev = run(t, x, base, detr)
            ann.to_csv(f"results/mhw_annual_{sea}_{vname}.csv")
            if vname == "paper":
                series[sea] = ann
            for per, (y0, y1) in {"1982_2021": (1982, 2021), "1982_2025": (1982, 2025)}.items():
                a = ann.loc[y0:y1]
                for metric, col in (("frequency", "n_events"), ("mhw_days", "mhw_days"), ("duration", "duration"),
                                    ("cum_intensity", "mhw_i_cum")):
                    v = a[col].values.astype(float)
                    if col != "duration":
                        v = np.nan_to_num(v, nan=0.0)
                    tr = mhw.trend(a.index, v)
                    rows.append({"sea": sea, "variant": vname, "period": per, "metric": metric,
                                 "ols_per_decade": round(tr["ols"], 3), "ci_lo": round(tr["ols_lo"], 3),
                                 "ci_hi": round(tr["ols_hi"], 3), "p": round(tr["ols_p"], 4),
                                 "sen_per_decade": round(tr["sen"], 3)})
        a = series[sea]
        rank = a.mhw_days.rank(ascending=False, method="min")
        rank_c = a.mhw_i_cum.rank(ascending=False, method="min")
        claims["seas"][sea][f"mucilage_years_rank_of_{len(a)}"] = {
            int(y): {"mhw_days": int(a.loc[y, "mhw_days"]), "rank_days": int(rank.loc[y]),
                     "cum_intensity": round(float(a.loc[y, "mhw_i_cum"]), 1), "rank_cum": int(rank_c.loc[y])}
            for y in MUCILAGE if y in a.index}
    tr = pd.DataFrame(rows)
    tr.to_csv("results/mhw_trends.csv", index=False)
    pick = lambda sea, v, m: float(tr[(tr.sea == sea) & (tr.variant == v) & (tr.period == "1982_2021") & (tr.metric == m)].ols_per_decade.iloc[0])
    claims["trends_1982_2021"] = {sea: {v: {m: pick(sea, v, m) for m in ("frequency", "mhw_days", "duration")}
                                        for v in VARIANTS} for sea in SEAS}
    json.dump(claims, open("results/claims.json", "w"), indent=1, default=float)
    print(json.dumps(claims, indent=1, default=float))

    m = series["marmara"]
    md = pd.read_csv("results/mhw_annual_marmara_detrended.csv", index_col=0)
    fig, axs = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    axs[0].bar(m.index, m.mhw_days, color="#1f5fbf", width=0.8, label="Baseline 1982-2021 (as in the paper)")
    axs[0].plot(md.index, md.mhw_days, color="0.3", marker="o", ms=3, lw=1, label="Detrended series (extremes beyond warming)")
    axs[0].set_ylabel("Heatwave days per year")
    axs[0].legend(frameon=False, fontsize=9)
    axs[1].bar(m.index, m.n_events, color="#1f5fbf", width=0.8)
    axs[1].plot(md.index, md.n_events, color="0.3", marker="o", ms=3, lw=1)
    axs[1].set_ylabel("Events per year")
    for ax in axs:
        for y in MUCILAGE:
            ax.axvspan(y - 0.5, y + 0.5, color="#e8a33d", alpha=0.25, lw=0)
        ax.spines[["top", "right"]].set_visible(False)
    axs[0].set_title("Sea of Marmara marine heatwaves, OSTIA on HEALPix (orange: mucilage years 2007-08, 2020-21)")
    fig.tight_layout(); fig.savefig("figures/marmara_mhw_annual.png", dpi=160); plt.close(fig)


if __name__ == "__main__":
    main()
