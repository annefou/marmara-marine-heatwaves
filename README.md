# marmara-marine-heatwaves

[![CI](https://github.com/annefou/marmara-marine-heatwaves/actions/workflows/ci.yml/badge.svg)](https://github.com/annefou/marmara-marine-heatwaves/actions/workflows/ci.yml)
[![Jupyter Book](https://github.com/annefou/marmara-marine-heatwaves/actions/workflows/jupyter-book.yml/badge.svg)](https://annefou.github.io/marmara-marine-heatwaves/)
[![Docker](https://github.com/annefou/marmara-marine-heatwaves/actions/workflows/docker.yml/badge.svg)](https://github.com/annefou/marmara-marine-heatwaves/pkgs/container/marmara-marine-heatwaves)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/{{ZENODO_DOI}}.svg)]({{ZENODO_DOI}})
[![FAIR4RS](https://img.shields.io/badge/FAIR4RS-conformant-brightgreen)](docs/fair4rs-checklist.md)
[![FORRT](https://img.shields.io/badge/FORRT-replication-blue)](https://forrt.org/)
[![Science Live](https://img.shields.io/badge/Science%20Live-nanopub%20chain-purple)](nanopubs/PUBLISHED.md)
[![RO-Crate](https://img.shields.io/badge/RO--Crate-1.2-orange)](ro-crate-metadata.json)
[![Software Heritage](https://archive.softwareheritage.org/badge/origin/https://github.com/annefou/marmara-marine-heatwaves/)](https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/annefou/marmara-marine-heatwaves)

> **Sea surface temperature and marine heatwave variability in interconnected basins: The Black-Marmara-Aegean Seas** — replication study.
> Reference paper: [10.1016/j.dynatmoce.2025.101555](https://doi.org/10.1016/j.dynatmoce.2025.101555)

**DRAFT, not reviewed.** LifeWatch ERIC feasibility test prepared for the meeting with HUBIOM (Hacettepe University) and Turkish research-infrastructure representatives on 30 October 2026. Our reading of the published work, open to correction by the authors.

### Claims tested (Saçu, Şen, Erdik and Öztürk 2025, *Dynamics of Atmospheres and Oceans* 110:101555)

| Claim | Paper | Ours, same data and baseline (1982-2021) |
| --- | --- | --- |
| M1. Sea of Marmara heatwave frequency trend, the highest of the three seas | 1.56 events per decade (cluster MS-C5) | **1.46** (95 % CI 1.09-1.84); Black Sea 1.46, Aegean 1.10 |
| M1b. Marmara heatwave days and duration trends | 25.55 days, 5.01 days per decade | **25.0** days (11.6-38.3), 3.3 days |
| M2. SST warming, strongest in the Black Sea then the Marmara | Black Sea up to 0.8, Aegean 0.3 degC per decade (grid points) | Sea means: Black Sea 0.60, Marmara 0.50, Aegean 0.46 degC per decade |
| M3. Mucilage years 2007-08 and 2020-21 coincide with intense, long heatwaves | Qualitative | 2020 ranks 2nd of 44 years (188 heatwave days), 2021 8th, 2007 11th, 2008 22nd |

### What the extension adds

- **Baseline matters.** The frequency trend is 1.32 events per decade with the WMO 1991-2020 normal and 1.89 with 1982-2011.
- **Most of the rise is mean warming.** On the detrended series the Marmara trend falls to 0.29 events per decade (CI -0.04 to 0.62) and heatwave days to 2.3 (not significant); Black Sea 0.05. Absolute heat stress (fixed baseline) matters for organisms; extremes beyond the warming trend have barely increased.
- **Heatwaves alone do not explain mucilage.** 2020 was also the 2nd most extreme year in the Black Sea and 5th in the Aegean, which had no mucilage outbreak; nutrient loads and stratification are the other ingredients.
- **2024 is the Marmara record**: 231 heatwave days (then 2020: 188, 2023: 145). Trend 1982-2025: 1.45 events and 31.2 days per decade.
- **Detection checked** against the reference implementation (Oliver, marineHeatWaves, commit d7292bf): 99.98-100 % daily agreement, thresholds within 0.003 degC (`results/reference_check.json`).

Figure: [Marmara annual heatwave days and events](figures/marmara_mhw_annual.png). Tables: `results/`.

### Method

- OSTIA L4 reprocessed SST (Copernicus Marine SST_GLO_SST_L4_REP_OBSERVATIONS_010_011, 0.05 deg, [doi:10.48670/moi-00168](https://doi.org/10.48670/moi-00168)), the paper's product, 1982-2025.
- Seas: IHO Sea Areas (Marine Regions, CC BY 4.0) instead of the paper's clusters.
- Daily fields resampled onto HEALPix cells (depth 10, ~6.4 km, [healpix-geo](https://github.com/GRID4EARTH/healpix-geo), WGS84 ellipsoid, NESTED) with [healpix-resample](https://github.com/GRID4EARTH/healpix-resample) (conservative bilinear, land excluded); sea means are plain means over equal-area cells.
- Hobday et al. 2016 detection (11-day window, 90th percentile, 31-day smoothing, at least 5 days, gaps of up to 2 days joined), OLS trends with HAC (Newey-West) confidence intervals.

### Limits

- Sub-regions are IHO seas, not the paper's clusters (the paper's Marmara cluster MS-C5 is close to the IHO Sea of Marmara).
- The paper used a MATLAB toolbox (Zhao and Marin 2019); our Python detection agrees with the reference Python implementation, not checked against the MATLAB one.
- Climate Digital Twin projections (planned) are not yet included.
- Surface temperature only; mucilage itself is not modelled.

### Data

Copernicus Marine (Copernicus Marine licence; free account), IHO Sea Areas (Marine Regions, CC BY 4.0). Only code, plots and summary statistics are in this repository.

---

## Quick start

```bash
git clone https://github.com/annefou/marmara-marine-heatwaves.git
cd marmara-marine-heatwaves
pixi install
pixi run download            # needs a free Copernicus Marine account (copernicusmarine login)
pixi run healpix
pixi run mhw
pixi run reference-check
```

(Pixi resolves `pixi.toml` against the per-platform `pixi.lock`, installs the env under `.pixi/`, and provides `pixi run` for any task without needing an `activate` step.)

Or with Docker:

```bash
docker run --rm ghcr.io/annefou/marmara-marine-heatwaves:latest
```

The Jupyter Book version is at <https://annefou.github.io/marmara-marine-heatwaves/>.

## Built from a template

This repository was created from [`sciencelivehub/forrt-replication-template`](https://github.com/sciencelivehub/forrt-replication-template). The template ships an operating manual for AI assistants ([`CLAUDE.md`](CLAUDE.md), [`AGENTS.md`](AGENTS.md)), domain conventions ([`DOMAIN.md`](DOMAIN.md)), and reference docs (`docs/`) so that an AI working only inside this repository can guide a researcher from "paper PDF + GitHub repo" to "published FORRT chain + Zenodo DOI" with no other context.

If you are reading this in a fresh fork, run [`/init-template`](.claude/skills/init-template/SKILL.md) inside Claude Code to substitute the placeholder tokens with your details. (For other AI tools, see [`docs/ai-portability.md`](docs/ai-portability.md).)

After `/init-template`, do these one-time setup steps to enable the full CI/CD path:

- **Enable GitHub Pages** at *Settings → Pages → Source: GitHub Actions*. Until enabled, the Jupyter Book build runs but the deploy step is skipped (CI stays green).
- All three workflows share one **readiness guard** (`.github/actions/check-ready`). Before `/init-template` runs, the `.template-uninitialised` sentinel makes them skip with an informative `::notice::` (badges stay green); `/init-template` deletes the sentinel, which activates them. They also skip while `notebooks/*.py` are still scaffolds (Phase 2). **Once you've published a nanopub chain** (real URIs in `nanopubs/PUBLISHED.md`), a skip is treated as a bug and **fails the run loudly** — so a finished replication can't sit on silently-green-but-empty CI.

## Repository structure

```
.
├── CLAUDE.md / AGENTS.md       # operating manual for AI assistants
├── DOMAIN.md                   # domain flavour (current: biodiversity + earth observation)
├── USER_PREFERENCES.md         # per-user style (edit on first clone)
├── README.md                   # this file
├── LICENSE                     # MIT
├── CITATION.cff                # how to cite
├── codemeta.json               # software metadata (CodeMeta-2.0)
├── ro-crate-metadata.json      # research object packaging (RO-Crate 1.2)
├── pixi.toml + pixi.lock       # pinned dependencies (single source of truth; lockfile is per-platform)
├── Dockerfile                  # container build
├── Snakefile                   # pipeline orchestration
├── myst.yml + index.md         # Jupyter Book scaffold
├── paper/                      # the source paper PDF
├── data/                       # downloaded artefacts (gitignored)
├── notebooks/                  # jupytext .py pipeline (01–04)
├── nanopubs/                   # FORRT chain drafts + published-URI registry
├── docs/                       # reference material
├── figures/                    # curated figures used in the Jupyter Book
├── .github/workflows/          # CI, Jupyter Book, Docker
└── .claude/                    # Claude Code agents, skills, sandbox config
```

## What you get

This template bakes in conventions that took multiple replications to discover. By using it, you inherit:

- **FAIR4RS conformance** — see [`docs/fair4rs-checklist.md`](docs/fair4rs-checklist.md) for the principle-by-principle mapping.
- **Self-contained data downloads** — the first notebook fetches everything; no manual data prep.
- **`pixi.toml` + `pixi.lock` as single source of truth** — local dev, Docker, and CI all install the same per-platform-pinned env.
- **`prefix-dev/setup-pixi`-based CI** — caches the env, runs the pipeline with `pixi run`, executes notebooks via a glob, fails fast on a stale lockfile.
- **Jupyter Book deployment** — auto-deploys to GitHub Pages with `BASE_URL` set correctly. (Don't put `base_url` in `myst.yml` — MyST silently ignores it.)
- **Docker + GHCR + Zenodo image archival** — `release` trigger pushes to GHCR and (optionally) archives to Zenodo for long-term preservation.
- **RO-Crate packaging** — the entire repo is a navigable Research Object via `ro-crate-metadata.json` (Process Run Crate + Workflow RO-Crate profiles).
- **Six-step FORRT chain workspace** — `nanopubs/drafts/` has a field-by-field skeleton for each step. `nanopubs/PUBLISHED.md` is the URI registry.
- **Layered AI guidance** — `CLAUDE.md` (universal) + `DOMAIN.md` (swappable per field) + `USER_PREFERENCES.md` (per-user). See [`docs/ai-portability.md`](docs/ai-portability.md) for non-Claude AI tools.
- **Sandbox by default** — `.claude/settings.json` denies file ops outside the repo, so a fresh AI session can't accidentally read `~/.ssh/` or write to `/etc/`.

## The six FORRT chain steps

A complete FORRT chain has six steps published on [platform.sciencelive4all.org](https://platform.sciencelive4all.org):

```
Quote-with-comment  →  AIDA  →  FORRT Claim  →  Replication Study  →  Replication Outcome  →  CiTO Citation
```

(For question-rooted chains with no upstream paper, replace step 1 with PICO or PCC. See [`docs/chain-decision-tree.md`](docs/chain-decision-tree.md).)

Drafts live in [`nanopubs/drafts/`](nanopubs/drafts/) field-by-field. Published URIs go into [`nanopubs/PUBLISHED.md`](nanopubs/PUBLISHED.md).

Optional further layers:

- **Research Software nanopub** — for reusable upstream tools (not demo repos). See [`docs/forrt-form-fields.md`](docs/forrt-form-fields.md) § Research Software.
- **Research Synthesis nanopub** — when this chain is part of a multi-chain story. See [`docs/forrt-form-fields.md`](docs/forrt-form-fields.md) § Research Synthesis.

## After publishing

When the chain is live and the FAIR4RS checklist is green, drafting an announcement post is the next step. See [`docs/announcement-template.md`](docs/announcement-template.md) for the structural template (vision-piece-first; the worked replication is the payoff, not the lead).

For lower-level nanopub work — retraction, superseding, batch publishing — see [`docs/programmatic-nanopubs.md`](docs/programmatic-nanopubs.md).

## Citation

If you use this work, please cite both:

- This software: [`CITATION.cff`](CITATION.cff) → DOI [{{ZENODO_DOI}}]({{ZENODO_DOI}})
- The original paper: [10.1016/j.dynatmoce.2025.101555](https://doi.org/10.1016/j.dynatmoce.2025.101555)

## Acknowledgements

This repository was built from [`sciencelivehub/forrt-replication-template`](https://github.com/sciencelivehub/forrt-replication-template), part of the [Science Live platform](https://platform.sciencelive4all.org). The template is licensed MIT and contributions (especially new domain flavours under [`docs/domain-flavours/`](docs/domain-flavours/)) are welcome.
