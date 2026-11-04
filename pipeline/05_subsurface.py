"""How deep do Sea of Marmara surface heatwaves reach? Copernicus Marine Marmara model, 2022-2025 (test).

Source: Copernicus Marine BLKSEA_ANALYSISFORECAST_PHY_007_001, dataset cmems_mod_blk_phy-tem_anfc_mrm-500m_P1D-m
(Marmara Sea and Turkish Straits, 500 m, daily mean potential temperature; available from November 2021, so too
short for a heatwave climatology at depth), depths 1, 5, 10, 15, 20, 25 and 30 m. Every model level is put on the same
290 Sea of Marmara cells as OSTIA (HEALPix depth 10, healpix-geo WGS84, NESTED; 01_healpix.py) with healpix-connector's
BilinearConservative (normalised conservative bilinear, area = cos(lat), land excluded, valid share per cell), from a
box that contains every cell completely (the cells' outline plus 0.05 deg). A cell enters the depth profile when it is
at least half water at 30 m on every day, so every depth is the mean over the same cells; the 1 m comparison with
OSTIA uses the cells at least half water at 1 m on every day, with OSTIA averaged over the same cells. Equal-area
cells: basin means are plain means over cells. Only the per-cell daily means are kept (<ROOT>/cmems/cells/, not
committed); no model field is stored. Copernicus Marine account read by the toolbox (never copied here).
Surface heatwave days come from OSTIA with the paper's baseline 1982-2021 (Hobday et al. 2016, pipeline/mhw.py),
on the 290 Marmara cells of 01_healpix.py.
(Until 4 November 2026 the model was averaged over a lon/lat box, 26.6-29.95 E, 40.25-41.08 N, every 6th point,
which did not match the 290 cells; see the README.)
1. Model at 1 m against OSTIA, 2022-2025: bias, RMSE, correlation of the daily basin means.
2. Anomaly at each depth: daily value minus the model's own 2022-2025 mean for that day of year (31-day running
   mean); averaged over OSTIA surface heatwave days and over other days, May-October.
3. Stratification: temperature at 1 m minus 10 m and minus 30 m, on heatwave days and other days, May-October;
   also 1-30 m with its seasonal cycle removed, since heatwave days fall mostly in July-October.
Writes <ROOT>/cmems/cells/<YYYY-MM>.npz (per-cell daily means), results/subsurface_claims.json,
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
DEPTH_IDX = [0, 4, 9, 14, 19, 24, 29]                   # 1, 5, ..., 30 m (the model has 1 m levels near the surface)
MARGIN = 0.05                                           # deg around the cells' outline
CELLDIR = f"{ROOT}/cmems/cells"
MIN_SHARE = 0.5


def marmara_cells():
    import healpix_geo.nested as hn
    cells = np.sort(xr.open_dataset(f"{ROOT}/hp/marmara.nc").cell.values.astype(np.uint64))
    vlon, vlat = hn.vertices(cells, 10, ellipsoid="WGS84", step=2)
    box = dict(minimum_longitude=float(np.min(vlon)) - MARGIN, maximum_longitude=float(np.max(vlon)) + MARGIN,
               minimum_latitude=float(np.min(vlat)) - MARGIN, maximum_latitude=float(np.max(vlat)) + MARGIN)
    return cells, box


def download():
    """Per-cell daily means of every model level on the 290 cells, one file per month (resumable)."""
    import copernicusmarine as cm
    from healpix_connector.resampling import BilinearConservative
    cells, box = marmara_cells()
    os.makedirs(CELLDIR, exist_ok=True)
    op, grid = None, None
    for start in pd.date_range("2022-01-01", "2025-12-01", freq="MS"):
        fn = f"{CELLDIR}/{start:%Y-%m}.npz"
        if os.path.exists(fn):
            continue
        end = start + pd.offsets.MonthEnd(0)
        for attempt in range(5):
            try:
                ds = cm.open_dataset(dataset_id=DATASET, variables=["thetao"], service="arco-time-series",
                                     start_datetime=str(start.date()), end_datetime=str(end.date()),
                                     minimum_depth=0, maximum_depth=31, **box)
                v = ds.thetao.isel(depth=DEPTH_IDX).load()
                break
            except Exception as e:                       # network or service hiccup
                print("retry", start.date(), attempt, type(e).__name__, str(e)[:150], flush=True)
                time.sleep(30 * (attempt + 1))
        else:
            raise RuntimeError(f"failed: {start.date()}")
        g = (v.longitude.values.copy(), v.latitude.values.copy())
        if grid is None:
            grid = g
            lon2, lat2 = np.meshgrid(*grid)
            op = BilinearConservative(lon2.ravel(), lat2.ravel(), cells, 10, area=np.cos(np.radians(lat2.ravel())))
        elif not (np.array_equal(g[0], grid[0]) and np.array_equal(g[1], grid[1])):
            raise RuntimeError(f"model grid changed in {start:%Y-%m}")
        a = v.values.reshape(v.sizes["time"] * v.sizes["depth"], -1).astype(float)   # (time*depth, pixels)
        mean, share = op(a)
        shape = (v.sizes["time"], v.sizes["depth"], len(cells))
        np.savez_compressed(fn, dates=v.time.values.astype("datetime64[D]"), depth=v.depth.values,
                            cells=cells, temp=mean.reshape(shape).astype(np.float32),
                            share=share.reshape(shape).astype(np.float32))
        print("OK", f"{start:%Y-%m}", "cells with water at 30 m:", int((share.reshape(shape)[:, -1] >= MIN_SHARE).all(0).sum()),
              flush=True)
    parts = [np.load(f"{CELLDIR}/{m:%Y-%m}.npz") for m in pd.date_range("2022-01-01", "2025-12-01", freq="MS")]
    dates = pd.to_datetime(np.concatenate([p["dates"] for p in parts]))
    return (dates, np.round(parts[0]["depth"]).astype(float), cells,
            np.concatenate([p["temp"] for p in parts]), np.concatenate([p["share"] for p in parts]))


def ostia_heatwave_days():
    """Heatwave days from the OSTIA mean over all 290 cells, as in 02_mhw.py."""
    s = xr.open_dataset(f"{ROOT}/hp/marmara.nc").sst.mean("cell").to_series()
    s = s[s.index.year <= 2025]
    t, x = s.index, s.values.astype(float)
    seas, thr = mhw.climatology(t, x, (1982, 2021))
    _, inm, _ = mhw.detect(t, x, seas, thr)
    return s, pd.Series(np.asarray(inm, bool), index=t)


def main():
    os.makedirs("results", exist_ok=True)
    dates, depths, cells, temp, share = download()
    ok30 = (share[:, -1, :] >= MIN_SHARE).all(0)             # at least half water at 30 m on every day
    ok1 = (share[:, 0, :] >= MIN_SHARE).all(0)
    prof = pd.DataFrame(np.nanmean(temp[:, :, ok30], axis=2), index=dates, columns=depths)
    m1 = pd.Series(np.nanmean(temp[:, 0, ok1], axis=1), index=dates)
    hp = xr.open_dataset(f"{ROOT}/hp/marmara.nc")
    o1 = hp.sst.sel(cell=cells[ok1].astype(np.int64)).mean("cell").to_series()
    sst, hw = ostia_heatwave_days()
    days = prof.index.intersection(sst.index).intersection(o1.index)
    prof, sst, hw, m1, o1 = prof.loc[days], sst.loc[days], hw.loc[days], m1.loc[days], o1.loc[days]
    d = m1 - o1
    claims = {"period": [str(days.min().date()), str(days.max().date())],
              "grid": "290 OSTIA cells (HEALPix depth 10, WGS84, NESTED), healpix-connector BilinearConservative",
              "cells_profile_water_at_30m": int(ok30.sum()), "cells_1m": int(ok1.sum()), "cells_total": int(len(cells)),
              "model_1m_vs_ostia": {"bias_degC": round(float(d.mean()), 2), "rmse_degC": round(float(np.sqrt((d ** 2).mean())), 2),
                                    "r": round(float(np.corrcoef(m1, o1)[0, 1]), 3),
                                    "note": "model 1 m and OSTIA averaged over the same cells"}}
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
    ax.set_title("Sea of Marmara, May-October 2022-2025\n(Copernicus Marine Marmara model, 500 m, on the 290 cells)", fontsize=10)
    ax.legend(frameon=False, fontsize=9); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig("figures/marmara_subsurface.png", dpi=160); plt.close(fig)


if __name__ == "__main__":
    main()
