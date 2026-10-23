"""Daily SST onto HEALPix cells of each sea (depth 10, ~6.4 km, healpix-geo WGS84 ellipsoid, NESTED).

The 0.05 deg OSTIA grid is resampled with healpix-resample, bilinear in conservative mode (area = cos(lat);
land pixels excluded), all days of a year in one batch. Reprocessed record first; near-real-time days only
after the last reprocessed day. Cells are kept when their centre lies inside the IHO sea polygon and at least
half of their area is sea. Equal-area cells: a sea's mean SST is the plain mean over its cells.

Usage: python pipeline/01_healpix.py <ROOT>
Writes <ROOT>/hp/<sea>.nc (time x cell, degC, float32; not committed) and results/cells.json.
"""
import json
import os
import sys

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
import healpix_geo.nested as hn
import shapely

ROOT = sys.argv[1]
DEPTH = 10
SEAS = {"marmara": ("marmara", 3369), "aegean": ("aegean", 3315), "black": ("black", 3319)}


def main():
    from healpix_resample import BilinearResampler
    os.makedirs(f"{ROOT}/hp", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    iho = gpd.read_file(f"{ROOT}/seas/iho.geojson")
    info = {}
    for sea, (box, mrgid) in SEAS.items():
        fn = f"{ROOT}/hp/{sea}.nc"
        poly = iho[iho.mrgid == mrgid].geometry.union_all()
        rep = xr.open_dataset(f"{ROOT}/sst/{box}_rep.nc")["analysed_sst"]
        nrt = xr.open_dataset(f"{ROOT}/sst/{box}_nrt.nc")["analysed_sst"]
        last_rep = pd.Timestamp(rep.time.values[-1])
        nrt = nrt.sel(time=nrt.time > np.datetime64(last_rep))
        lon2, lat2 = np.meshgrid(rep.longitude.values, rep.latitude.values)
        lon, lat = lon2.ravel(), lat2.ravel()
        op = BilinearResampler(lon_deg=lon, lat_deg=lat, level=DEPTH, nest=True, ellipsoid="WGS84",
                               verbose=False, area=np.cos(np.radians(lat)))
        sea_px = np.isfinite(rep.isel(time=0).values.ravel())
        ones = op.resample(np.where(sea_px, 1.0, 0.0), conservative=True)
        full = op.resample(np.ones(len(lon)), conservative=True)
        cid = np.asarray(ones.cell_ids, np.uint64)
        frac = np.asarray(ones.cell_data, float) / np.asarray(full.cell_data, float)
        clon, clat = hn.healpix_to_lonlat(cid, DEPTH, ellipsoid="WGS84")
        keep = (frac >= 0.5) & shapely.contains_xy(poly, np.asarray(clon), np.asarray(clat))
        sel = np.flatnonzero(keep)
        sel = sel[np.argsort(cid[sel])]
        out, times = [], []
        for src in (rep, nrt):
            if src.sizes["time"] == 0:
                continue
            for y in np.unique(src.time.dt.year.values):
                blk = src.sel(time=src.time.dt.year == y)
                a = blk.values.reshape(blk.sizes["time"], -1).astype(float) - 273.15
                m = np.isfinite(a)
                num = np.asarray(op.resample(np.where(m, a, 0.0), conservative=True).cell_data, float)
                den = np.asarray(op.resample(m.astype(float), conservative=True).cell_data, float)
                with np.errstate(invalid="ignore", divide="ignore"):
                    v = (num / den)[:, sel]
                out.append(v.astype(np.float32))
                times.append(blk.time.values)
        ds = xr.Dataset({"sst": (("time", "cell"), np.concatenate(out))},
                        coords={"time": np.concatenate(times), "cell": cid[sel].astype(np.int64),
                                "lon": ("cell", np.asarray(clon)[sel]), "lat": ("cell", np.asarray(clat)[sel])})
        ds.attrs.update(source="OSTIA L4 REP then NRT (Copernicus Marine)", last_rep_day=str(last_rep.date()),
                        healpix_depth=DEPTH, ellipsoid="WGS84", indexing="nested")
        ds.to_netcdf(fn)
        info[sea] = {"cells": int(len(sel)), "first_day": str(pd.Timestamp(ds.time.values[0]).date()),
                     "last_day": str(pd.Timestamp(ds.time.values[-1]).date()), "last_rep_day": str(last_rep.date())}
        print(sea, info[sea], flush=True)
    json.dump({"healpix_depth": DEPTH, "seas": info}, open("results/cells.json", "w"), indent=1)


if __name__ == "__main__":
    main()
