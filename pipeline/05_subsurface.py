"""How deep do Sea of Marmara surface heatwaves reach? Copernicus Marine Marmara model, 2022-2025 (test).

Source: Copernicus Marine BLKSEA_ANALYSISFORECAST_PHY_007_001, dataset cmems_mod_blk_phy-tem_anfc_mrm-500m_P1D-m
(Marmara Sea and Turkish Straits, 500 m, daily mean potential temperature; available from November 2021, so too
short for a heatwave climatology at depth). Box 26.6-29.95 E, 40.25-41.08 N, every 6th grid point (about 3 km),
depths 1, 5, 10, 15, 20, 25 and 30 m; only water columns with a value at 30 m are averaged, so every depth is
the mean over the same columns. Copernicus Marine account read by the toolbox (never copied here).
Surface heatwave days come from OSTIA with the paper's baseline 1982-2021 (Hobday et al. 2016, pipeline/mhw.py),
on the 290 Marmara cells of 01_healpix.py.
1. Model at 1 m against OSTIA, 2022-2025: bias, RMSE, correlation of the daily basin means.
2. Anomaly at each depth: daily value minus the model's own 2022-2025 mean for that day of year (31-day running
   mean); averaged over OSTIA surface heatwave days and over other days, May-October.
3. Stratification: temperature at 1 m minus 10 m and minus 30 m, on heatwave days and other days, May-October;
   also 1-30 m with its seasonal cycle removed, since heatwave days fall mostly in July-October.
Writes <ROOT>/cmems/marmara_profile_daily.csv (basin means), results/subsurface_claims.json,
results/doc_figure_marmara_subsurface.json and figures/marmara_subsurface.png.
Usage: python pipeline/05_subsurface.py <ROOT>
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mhw  # noqa: E402

ROOT = sys.argv[1]
DATASET = "cmems_mod_blk_phy-tem_anfc_mrm-500m_P1D-m"
BOX = dict(minimum_longitude=26.6, maximum_longitude=29.95, minimum_latitude=40.25, maximum_latitude=41.08)
DEPTH_IDX = [0, 4, 9, 14, 19, 24, 29]                   # 1, 5, ..., 30 m (the model has 1 m levels near the surface)
STRIDE = 6
OUT = f"{ROOT}/cmems/marmara_profile_daily.csv"


def download():
    import copernicusmarine as cm
    if os.path.exists(OUT):
        return pd.read_csv(OUT, parse_dates=["date"])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rows = []
    for start in pd.date_range("2022-01-01", "2025-12-01", freq="MS"):
        end = start + pd.offsets.MonthEnd(0)
        for attempt in range(5):
            try:
                ds = cm.open_dataset(dataset_id=DATASET, variables=["thetao"], service="arco-time-series",
                                     start_datetime=str(start.date()), end_datetime=str(end.date()),
                                     minimum_depth=0, maximum_depth=31, **BOX)
                v = ds.thetao.isel(latitude=slice(None, None, STRIDE), longitude=slice(None, None, STRIDE),
                                   depth=DEPTH_IDX).load()
                break
            except Exception as e:                       # network or service hiccup
                print("retry", start.date(), attempt, type(e).__name__, str(e)[:150], flush=True)
                time.sleep(30 * (attempt + 1))
        else:
            raise RuntimeError(f"failed: {start.date()}")
        deep_ok = np.isfinite(v.isel(depth=-1)).all("time")          # columns at least 30 m deep, valid all month
        m = v.where(deep_ok).mean(["latitude", "longitude"])
        for t in range(m.sizes["time"]):
            for k, z in enumerate(m.depth.values):
                rows.append({"date": pd.Timestamp(m.time.values[t]).normalize(), "depth_m": float(z),
                             "t_degC": round(float(m.values[t, k]), 4), "columns": int(deep_ok.sum())})
        print("OK", start.strftime("%Y-%m"), int(deep_ok.sum()), "columns", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)
    return df


def ostia_heatwave_days():
    s = xr.open_dataset(f"{ROOT}/hp/marmara.nc").sst.mean("cell").to_series()
    s = s[s.index.year <= 2025]
    t, x = s.index, s.values.astype(float)
    seas, thr = mhw.climatology(t, x, (1982, 2021))
    _, inm, _ = mhw.detect(t, x, seas, thr)
    return s, pd.Series(np.asarray(inm, bool), index=t)


def main():
    os.makedirs("results", exist_ok=True)
    df = download()
    prof = df.pivot_table(index="date", columns="depth_m", values="t_degC")
    sst, hw = ostia_heatwave_days()
    days = prof.index.intersection(sst.index)
    prof, sst, hw = prof.loc[days], sst.loc[days], hw.loc[days]
    d = prof[1.0] - sst
    claims = {"period": [str(days.min().date()), str(days.max().date())], "columns_median": int(df["columns"].median()),
              "model_1m_vs_ostia": {"bias_degC": round(float(d.mean()), 2), "rmse_degC": round(float(np.sqrt((d ** 2).mean())), 2),
                                    "r": round(float(np.corrcoef(prof[1.0], sst)[0, 1]), 3)}}
    doy = prof.index.dayofyear
    clim = prof.groupby(doy).mean()
    clim = pd.concat([clim.iloc[-15:], clim, clim.iloc[:15]]).rolling(31, center=True).mean().iloc[15:-15]
    anom = prof - clim.loc[doy].set_index(prof.index)
    season = prof.index.month.isin(range(5, 11))
    hot, other = season & hw.values, season & ~hw.values
    claims["heatwave_days_may_oct"] = int(hot.sum())
    claims["other_days_may_oct"] = int(other.sum())
    claims["anomaly_by_depth_degC"] = {f"{int(z)} m": {"heatwave": round(float(anom[z][hot].mean()), 2),
                                                        "other": round(float(anom[z][other].mean()), 2)} for z in prof.columns}
    strat = {"1-10 m": prof[1.0] - prof[10.0], "1-30 m": prof[1.0] - prof[30.0]}
    claims["stratification_degC_may_oct"] = {k: {"heatwave": round(float(v[hot].mean()), 2), "other": round(float(v[other].mean()), 2)}
                                             for k, v in strat.items()}
    sa = strat["1-30 m"] - (strat["1-30 m"].groupby(doy).mean().pipe(
        lambda c: pd.concat([c.iloc[-15:], c, c.iloc[:15]]).rolling(31, center=True).mean().iloc[15:-15]).loc[doy].values)
    claims["stratification_anomaly_1_30m_degC_may_oct"] = {"heatwave": round(float(sa[hot].mean()), 2),
                                                           "other": round(float(sa[other].mean()), 2),
                                                           "note": "1 m minus 30 m, minus its own 2022-2025 seasonal cycle"}
    claims["heatwave_days_by_month"] = {int(k): int(v) for k, v in pd.Series(prof.index[hot].month).value_counts().sort_index().items()}
    json.dump(claims, open("results/subsurface_claims.json", "w"), indent=1)
    print(json.dumps(claims, indent=1))
    rows = [{"depth": int(z), "kind": k, "anom": round(float(anom[z][mask].mean()), 2)}
            for z in prof.columns for k, mask in (("heatwave", hot), ("other", other))]
    json.dump(rows, open("results/doc_figure_marmara_subsurface.json", "w"), indent=1)

    fig, ax = plt.subplots(figsize=(5.5, 5))
    for k, c in (("heatwave", "#2f6fd6"), ("other", "0.6")):
        r = [x for x in rows if x["kind"] == k]
        ax.plot([x["anom"] for x in r], [x["depth"] for x in r], "-o", color=c,
                label="OSTIA surface heatwave days" if k == "heatwave" else "Other days", ms=4)
    ax.axvline(0, color="0.3", lw=0.8)
    ax.invert_yaxis(); ax.set_xlabel("Temperature anomaly (degC)"); ax.set_ylabel("Depth (m)")
    ax.set_title("Sea of Marmara, May-October 2022-2025\n(Copernicus Marine Marmara model, 500 m)", fontsize=10)
    ax.legend(frameon=False, fontsize=9); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig("figures/marmara_subsurface.png", dpi=160); plt.close(fig)


if __name__ == "__main__":
    main()
