# 06 — CiTO Citation

**Description:** *"Declare citations between papers or other works, using Citation Typing Ontology"*

## Field-by-field draft

<!-- field: work -->
### Identifier for the citing creative work (text input, required)

```
«URI of step 05 (FORRT Replication Outcome), filled by the chain wizard»
```

### List citations (repeatable group, required ≥1)

#### Citation 1 — back to the original paper

##### Citation Type (dropdown)

Outcome is "partially supported", so `qualifies` (from `vocabulary("cito_relation")`, live).

```
qualifies
```

##### DOI or other URL of the cited work (text input)

```
https://doi.org/10.1016/j.dynatmoce.2025.101555
```

#### Additional citations (optional)

Both DOIs resolved on 2026-10-24 (Crossref, DataCite); both relations from `vocabulary("cito_relation")`.

- Type: uses method in → URL: https://doi.org/10.1016/j.pocean.2015.12.014
- Type: cites as data source → URL: https://doi.org/10.48670/moi-00168

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 06.
