# 02 — AIDA Sentence

**Form heading:** *"AIDA Sentence — Make structured scientific claims following the AIDA model"*

## Field-by-field draft

<!-- field: aida -->
### AIDA sentence (text input, required)

Atomic (one comparative finding), no numbers, no method names.

```
Marine heatwaves have become more frequent in the Sea of Marmara since the early 1980s, faster than in the adjacent Black Sea and Aegean Sea.
```

<!-- field: topic -->
### Select related topics/tags (search/select, optional)

Checked with `wikidata_lookup` (2026-10-24): both are concepts (subclass of heat wave; subclass of temperature).

```
marine heatwave (Q56321065)
sea surface temperature (Q1507383)
```

<!-- field: project -->
### Relates to this nanopublication (search/select, required)

```
«URI of step 01 (Quote-with-comment), filled by the chain wizard»
```

<!-- field: dataset -->
### Supported by datasets (text input, optional)

OSTIA sea surface temperature reprocessed, Copernicus Marine (the paper's product).

- _DOI 1: https://doi.org/10.48670/moi-00168

<!-- field: publication -->
### Supported by other publications (text input, optional)

*(skip — the paper is cited through the Quote; leaving this empty also avoids the dataset + publication publish bug)*

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 02.
