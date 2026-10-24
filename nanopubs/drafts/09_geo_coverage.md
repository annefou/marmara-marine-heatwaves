# 09 — Geographical coverage (optional)

One pooled coverage: the paper treats the three connected seas as one study area.

## Shared field

<!-- field: paper -->
### Cited DOI (text input, required — same for every location)

```
10.1016/j.dynatmoce.2025.101555
```

---

## Per-location block

### Location A

<!-- field: quoteType -->
**Quote type** (radio: whole | ends, required)

```
whole
```

<!-- field: quotation -->
**Quoted Text** (textarea, required) — verified with `verify_quote` on `paper/sacu2025.pdf`: page 1, characters 847–1048 (match after whitespace and hyphenation normalisation).

```
This study investigates the spatiotemporal variability of SST and MHW characteristics across the interconnected Black, Marmara, and Aegean Seas using satellite-derived daily SST data from 1982 to 2021.
```

<!-- field: quotation-end -->
**Quoted Text End** (textarea, optional — only if quote type = ends). Leave blank for `whole`.

```

```

<!-- field: location -->
**Short ID for location** (text input, required)

```
black-marmara-aegean-seas
```

<!-- field: location-label -->
**Area name** (text input, required) — add each sea in the form's location search: Black Sea, Sea of Marmara, Aegean Sea.

```
Black Sea, Sea of Marmara and Aegean Sea
```

<!-- field: geometry -->
**Short ID for geometry** (text input, optional)

```
coverage
```

<!-- field: wkt -->
**Geometry as Well-known Text (WKT)** — left to the form's geocoder; the paper states no coordinates.

```

```

<!-- field: comment -->
**Comment** (textarea, required)

```
The quoted sentence names the three connected seas as the study area of the paper, analysed together with daily satellite sea surface temperature for 1982-2021.
```

## Publication note

Each location block is a **standalone** nanopub, not one of the six FORRT chain steps.
Publish it via the platform's **"Document geographical coverage"** template. After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` under a "Geographical coverage" row.
