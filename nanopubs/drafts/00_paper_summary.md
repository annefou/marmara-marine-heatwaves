# Paper summary

> Working scratchpad for the paper-analysis phase; it feeds the Quote / AIDA / Claim drafts and is not itself a nanopub.

**Reference paper:** Sea surface temperature and marine heatwave variability in interconnected basins: The Black-Marmara-Aegean Seas

**DOI:** 10.1016/j.dynatmoce.2025.101555

**Authors:** Şehriban Saçu, Olgay Şen, Tarkan Erdik, İzzet Öztürk (Istanbul Technical University)

**Year:** 2025

## Headline claim

> The highest trend in MHW frequency is observed in the Marmara Sea, with an increase of 1.56 events/decade which further intensified after the 2000s.

Verified verbatim with `verify_quote` against `paper/sacu2025.pdf` (page 1, abstract).

## Methodology summary

- **Data sources:** OSTIA L4 reprocessed daily sea surface temperature (Copernicus Marine, 0.05°), 1982–2021, over the Black, Marmara and Aegean Seas.
- **Model:** marine heatwaves after Hobday et al. (2016), 90th-percentile threshold, baseline 1982–2021; linear trends of annual event frequency and heatwave days.
- **Sample:** sub-regions from k-means clustering of SST; the Sea of Marmara is cluster MS-C5. 40 years.
- **Headline numbers:** Marmara frequency trend 1.56 events/decade (highest of the clusters); heatwave days 25.55 days/decade.

## Replication design choice

- [ ] **Reproduction Study**
- [ ] **Replication Study**
- [x] **Reproduction/Replication Study**

Same product and heatwave definition (reproduction), but IHO seas on HEALPix cells instead of clusters, our own detection code checked against the reference implementation, the record extended to 2025 and baseline and detrending variants added (replication).

## Notes for downstream drafts

- The paper's Marmara cluster maps one-to-one onto the IHO Sea of Marmara; its Black Sea and Aegean clusters do not, so the rank comparison is approximate.
- Results: 1.462 events/decade (95% CI 1.086–1.839) — the paper's 1.56 lies inside; Black Sea 1.456, Aegean 1.100; detrended 0.292 (not significant). Outcome: partially supported, high confidence.
- Paper PDF is local only (`paper/*.pdf` is git-ignored; publisher copyright).
