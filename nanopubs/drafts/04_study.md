# 04 — FORRT Replication Study

Method read from `pipeline/00_download.py`, `pipeline/01_healpix.py`, `pipeline/02_mhw.py`, `pipeline/mhw.py` and `pipeline/09_check_reference.py` (2026-10-24).

## Field-by-field draft

<!-- field: study -->
### Short URI suffix for study ID (text input, required)

```
marmara-mhw-replication-study
```

<!-- field: label -->
### Label/name of replication study (text input, required)

```
Replication of the Sea of Marmara marine heatwave frequency trend with OSTIA on HEALPix cells, 1982-2025
```

<!-- field: type -->
### Choose the study type (dropdown, required)

Same data product and heatwave definition as the paper (reproduction), different spatial units and an extended record (replication).

- [ ] Replication Study - replication with different methodology or conditions
- [x] Reproduction/Replication Study - study that is both, reproduction and replication
- [ ] Reproduction Study - direct reproduction: same methodology, same tools

<!-- field: claim -->
### Choose FORRT claim (search/select, required)

```
«URI of step 03 (FORRT Claim), filled by the chain wizard»
```

<!-- field: scope -->
### Describe what part of the claim is reproduced/replicated. (textarea, required)

```
The claim that marine heatwave frequency in the Sea of Marmara rose by about 1.56 events per decade over 1982-2021, the highest trend of the Black, Marmara and Aegean Seas. In scope: the size and significance of the Marmara trend with the paper's data product and heatwave definition, its rank against the Black Sea and the Aegean, and how much of it is the basin's mean warming. Out of scope: the statement that the trend intensified after the 2000s, the correlations with climate indices, and any causal link to mucilage (mucilage years are only ranked by heatwave days).
```

<!-- field: methodology -->
### Describe how the claim is reproduced/replicated. (textarea, required)

```
Daily OSTIA L4 reprocessed sea surface temperature (Copernicus Marine, 0.05 degrees), the paper's product, 1982-2025, resampled onto HEALPix cells of about 6.4 km (depth 10, WGS84 ellipsoid, nested) with conservative bilinear resampling. Each sea is the set of cells whose centre lies in its IHO polygon and which are at least half sea (290 cells for the Sea of Marmara); the sea-mean daily series is analysed. Marine heatwaves follow Hobday et al. (2016): 90th-percentile threshold from an 11-day window smoothed over 31 days, events of at least 5 days, gaps of 2 days or less joined, baseline 1982-2021 as in the paper. Our detection is checked day by day against the marineHeatWaves reference code. Trends of annual event counts and heatwave days are ordinary least squares with Newey-West 95% intervals (2 lags), with Theil-Sen slopes alongside. Variants: WMO baseline 1991-2020, baseline 1982-2011, and detection on the linearly detrended series.
```

<!-- field: deviation -->
### Describe any deviations from original methodology. (textarea, optional)

```
Sub-regions are the IHO seas rather than the paper's k-means clusters: the Sea of Marmara corresponds to the paper's cluster MS-C5, while the paper's Black Sea and Aegean clusters are not reproduced. Temperature is averaged over equal-area HEALPix cells instead of native pixels. Heatwaves are detected with our own implementation of the Hobday definition, verified against the reference code. The record is extended to 2025 and baseline and detrending variants are added.
```

<!-- field: keyword -->
### Search keywords (Wikidata) (search/select, optional)

Checked with `wikidata_lookup` (2026-10-24).

- marine heatwave (Q56321065)
- sea surface temperature (Q1507383)
- Sea of Marmara (Q35367)

<!-- field: discipline -->
### Search discipline (Wikidata) (search/select, optional)

- oceanography (Q43518)

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 04.
