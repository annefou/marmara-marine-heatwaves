"""Inputs: daily sea surface temperature from Copernicus Marine and the IHO sea-area outlines.

SST: SST_GLO_SST_L4_REP_OBSERVATIONS_010_011 (OSTIA reprocessed, 0.05 deg, doi:10.48670/moi-00168), the
product used by Sacu et al. 2025, from 1982 to its last day; then SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001
(OSTIA near real time, 0.05 deg) to the end of 2025, used only after the reprocessed record ends.
Three boxes: Sea of Marmara, Aegean Sea, Black Sea (the IHO polygons select the cells later).
Credential read by the toolbox from ~/.copernicusmarine (never printed here).
Sea areas: IHO Sea Areas v3 (Flanders Marine Institute, Marine Regions, CC BY 4.0) via WFS:
Sea of Marmara (MRGID 3369), Aegean Sea (3315), Black Sea (3319).

Usage: python pipeline/00_download.py <ROOT>      (ROOT = work)
Writes <ROOT>/sst/<box>_{rep,nrt}.nc and <ROOT>/seas/iho.geojson (not committed; Copernicus Marine licence).
"""
import json
import os
import sys

import copernicusmarine as cm
import requests

ROOT = sys.argv[1]
BOXES = {"marmara": (26.0, 40.0, 30.2, 41.2), "aegean": (22.0, 35.0, 28.5, 41.1), "black": (27.2, 40.8, 42.0, 47.0)}
PRODUCTS = {"rep": ("METOFFICE-GLO-SST-L4-REP-OBS-SST", "1982-01-01", "2025-12-31"),
            "nrt": ("METOFFICE-GLO-SST-L4-NRT-OBS-SST-V2", "2021-01-01", "2025-12-31")}
WFS = ("https://geo.vliz.be/geoserver/MarineRegions/wfs?service=WFS&version=1.0.0&request=GetFeature"
       "&typeName=MarineRegions:iho&outputFormat=application/json&CQL_FILTER=mrgid%20IN%20(3369,3315,3319)")


def main():
    os.makedirs(f"{ROOT}/sst", exist_ok=True)
    os.makedirs(f"{ROOT}/seas", exist_ok=True)
    if not os.path.exists(f"{ROOT}/seas/iho.geojson"):
        r = requests.get(WFS, timeout=300)
        r.raise_for_status()
        open(f"{ROOT}/seas/iho.geojson", "w").write(r.text)
    log = []
    for box, (x0, y0, x1, y1) in BOXES.items():
        for tag, (ds, t0, t1) in PRODUCTS.items():
            fn = f"{ROOT}/sst/{box}_{tag}.nc"
            if os.path.exists(fn):
                continue
            kw = dict(dataset_id=ds, variables=["analysed_sst"], minimum_longitude=x0, maximum_longitude=x1,
                      minimum_latitude=y0, maximum_latitude=y1, start_datetime=t0, end_datetime=t1)
            cm.subset(**kw, output_directory=f"{ROOT}/sst", output_filename=os.path.basename(fn),
                      overwrite=True, disable_progress_bar=True)
            log.append(kw)
            print("ok", fn, flush=True)
    json.dump(log, open(f"{ROOT}/sst/requests.json", "a"), indent=1)


if __name__ == "__main__":
    main()
