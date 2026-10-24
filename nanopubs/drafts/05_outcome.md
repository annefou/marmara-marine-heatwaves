# 05 — FORRT Replication Outcome

Numbers read from `results/mhw_trends.csv`, `results/claims.json`, `results/reference_check.json` and `results/cells.json` (2026-10-24).

## Field-by-field draft

<!-- field: outcome -->
### Short URI suffix for outcome ID (text input, required)

```
marmara-mhw-frequency-outcome
```

<!-- field: label -->
### Plain-text label for the outcome (text input, required)

```
Sea of Marmara heatwave frequency trend reproduced; most of it is the basin's mean warming
```

<!-- field: study -->
### Choose study (search/select, required)

```
«URI of step 04 (FORRT Replication Study), filled by the chain wizard»
```

<!-- field: repo -->
### Repository URL (text input, required)

The Zenodo version DOI of the release the results come from; substituted by the release workflow.

```
https://doi.org/{{ZENODO_VERSION_DOI}}
```

<!-- field: date -->
### Choose completion date (text input, required)

```
2026-10-23
```

<!-- field: validationStatus -->
### Choose validation status (dropdown, required)

From `vocabulary("validation_status")`: the trend's size is reproduced, its rank only marginally, and the post-2000 intensification is not tested.

- [ ] contradicted
- [ ] inconclusive
- [ ] not tested
- [x] partially supported
- [ ] validated

<!-- field: confidenceLevel -->
### Choose confidence level (dropdown, required)

From `vocabulary("confidence_level")`: the paper's number lies inside our interval with the same data and definition, and the detection matches the reference code.

- [x] high - Strong evidence, mostly agrees with original
- [ ] low - Limited evidence, significant disagreement
- [ ] moderate - Adequate evidence, partial agreement
- [ ] very high - Extensive evidence, high agreement with original
- [ ] very low - Minimal evidence, major disagreement

<!-- field: conclusion -->
### Describe the overall conclusion about the original claim (textarea, required)

```
The paper's Sea of Marmara trend is reproduced: 1.46 heatwave events per decade over 1982-2021 (95% interval 1.09-1.84) against the paper's 1.56, which lies inside the interval, and 25.0 heatwave days per decade against the paper's 25.6. The Marmara trend is the highest of the three seas, but only just ahead of the Black Sea (1.462 against 1.456 events per decade) and clearly above the Aegean (1.10). Once the series is detrended, the Marmara trend falls to 0.29 events per decade and is not significant: the rising frequency is mostly the basin's mean warming rather than more extreme departures from it. The claim is supported for the size of the trend, partially for its rank, and not tested for the intensification after the 2000s.
```

<!-- field: evidence -->
### Describe the evidence that supports your conclusion (textarea, required)

```
Sea of Marmara, 290 HEALPix cells, OSTIA 1982-2021, baseline 1982-2021 (as in the paper): event frequency +1.462 per decade (Newey-West 95% interval 1.086-1.839, p < 0.001; Theil-Sen 1.25); heatwave days +24.96 per decade (11.61-38.31, p = 0.0002). Other baselines: WMO 1991-2020 +1.315 (0.931-1.699); 1982-2011 +1.886 (1.465-2.308). Detrended series: +0.292 (-0.039 to 0.622, p = 0.084). Black Sea +1.456 and Aegean +1.100 events per decade with the paper's baseline. Sea surface temperature trend +0.503 degC per decade (1982-2021). Detection check against the marineHeatWaves reference code, 1982-2025: 95 events in both, daily agreement 99.994%, threshold difference at most 0.003 degC. Files: results/mhw_trends.csv, results/claims.json, results/reference_check.json.
```

<!-- field: limitations -->
### Describe what limits the conclusions of the study (textarea, optional)

```
The sub-regions are IHO seas, not the paper's clusters, so the Black Sea and Aegean comparison is approximate. One data product only. Event-based trends depend on the baseline (1.32 to 1.89 events per decade across the three tested), which is why the detrended result matters for interpretation. The post-2000 intensification and the climate-index correlations were not tested. Mucilage years are ranked, not modelled: 2020 has the second-highest heatwave days of 44 years and 2021 the eighth, but 2007 ranks eleventh and 2008 twenty-second.
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 05.
