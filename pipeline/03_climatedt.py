"""Daily sea surface temperature of the Destination Earth Climate DT (generation 2) on the Sea of Marmara cells.

Source: Climate DT generation 2, stream clte, levtype o2d, param 263101 avg_tos (daily mean SST, K), resolution
high (HEALPix depth 10 on a sphere), realization 1; historical 1990-2014 ("baseline"/"hist"), SSP3-7.0 2015-2049
("projections"). Two models with different ocean components: IFS-FESOM (FESOM2, unstructured mesh, about 5 km;
LUMI) and IFS-NEMO (NEMO, 1/12 deg; MareNostrum 5). Account: DestinE upgraded access, read by polytope-client
from ~/.polytopeapirc (never copied here).
Only the region is requested (Polytope bounding-box feature, about 15 MB of CoverageJSON per model and year), so
no global field is downloaded. The samples are the sphere cell centres; they are put onto the same WGS84 cells as
OSTIA (work/hp/marmara.nc, 01_healpix.py) with healpix-connector's BilinearConservative (sphere -> WGS84, normalised
conservative bilinear; never by matching ids). A cell is kept when at least half of it is covered by model sea.

Usage: python pipeline/03_climatedt.py <ROOT> <MODEL> [<Y0> <Y1>]
Writes <ROOT>/dt/<MODEL>/<year>.npz: dates, sst (days x 290 cells, degC), share (valid share per cell).
Raw responses are deleted after processing; Climate DT data are not redistributed (DestinE terms).
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import xarray as xr
from healpix_connector.resampling import BilinearConservative

ROOT, MODEL = sys.argv[1], sys.argv[2]
Y0, Y1 = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1990, 2049)
OUT = f"{ROOT}/dt/{MODEL}"
ENDPOINT = {"IFS-NEMO": "polytope.mn5.apps.dte.destination-earth.eu",
            "IFS-FESOM": "polytope.lumi.apps.dte.destination-earth.eu"}[MODEL]
BOX = [[41.5, 25.9], [39.7, 30.2]]          # [lat, lon] north-west and south-east corners, around the 290 cells
BASE = {"class": "d1", "dataset": "climate-dt", "type": "fc", "expver": "0001", "generation": "2",
        "realization": "1", "model": MODEL, "resolution": "high", "stream": "clte", "levtype": "o2d",
        "param": "263101", "time": "0000"}


def experiment(year):
    return ({"activity": "baseline", "experiment": "hist"} if year <= 2014 else
            {"activity": "projections", "experiment": "SSP3-7.0"})


def retrieve(client, year, target):
    req = {**BASE, **experiment(year), "date": f"{year}0101/to/{year}1231",
           "feature": {"type": "boundingbox", "points": BOX}}
    for attempt in range(5):
        try:
            client.retrieve("destination-earth", req, target)
            return
        except (Exception, SystemExit) as e:          # the polytope client exits on a refusal
            print("retry", MODEL, year, attempt, type(e).__name__, str(e)[:200], flush=True)
            time.sleep(60 * (attempt + 1))
    raise RuntimeError(f"Climate DT request failed: {MODEL} {year}")


def read_covjson(path):
    d = json.load(open(path))
    dates, rows, pts = [], [], None
    for c in d["coverages"]:
        p = np.array([q[:2] for q in c["domain"]["axes"]["composite"]["values"]], float)   # lat, lon
        if pts is None:
            pts = p
        assert np.array_equal(p, pts), "sample points change between days"
        dates.append(c["domain"]["axes"]["t"]["values"][0][:10])
        rows.append(np.array(c["ranges"]["avg_tos"]["values"], float))
    order = np.argsort(dates)
    return np.array(dates)[order], np.stack(rows)[order] - 273.15, pts


def main():
    from polytope.api import Client
    os.makedirs(OUT, exist_ok=True)
    cells = np.sort(xr.open_dataset(f"{ROOT}/hp/marmara.nc").cell.values.astype(np.uint64))
    client = Client(address=ENDPOINT, quiet=True)
    op, grid = None, None
    for year in range(Y0, Y1 + 1):
        fn = f"{OUT}/{year}.npz"
        if os.path.exists(fn):
            continue
        t0 = time.time()
        raw = f"{OUT}/{year}.covjson"
        retrieve(client, year, raw)
        dates, sst, pts = read_covjson(raw)
        n = 366 if pd.Timestamp(f"{year}-12-31").dayofyear == 366 else 365
        assert len(dates) == n, f"{MODEL} {year}: {len(dates)} days"
        if op is None:
            op = BilinearConservative(pts[:, 1], pts[:, 0], cells, 10)
            grid = pts
        assert np.array_equal(pts, grid)
        mean, share = op(sst)
        np.savez_compressed(fn, dates=dates, sst=mean.astype(np.float32), share=share[0].astype(np.float32),
                            cells=cells)
        os.remove(raw)
        print("OK", MODEL, year, f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
