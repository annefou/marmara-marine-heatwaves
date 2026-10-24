# Snakefile: the whole Sea of Marmara replication, in the order the results in results/ were produced.
#
#   pixi run snakemake --cores 1              # OSTIA heatwaves and the reference check (Copernicus Marine account)
#   pixi run snakemake --cores 1 climatedt    # adds the Climate DT projection (DestinE upgraded access)
#   pixi run snakemake --cores 1 subsurface   # adds the Marmara 500 m model test (Copernicus Marine account)
#   pixi run snakemake --cores 1 -n           # dry run
#
# Downloads go to work/ (not committed). Accounts are read by the Copernicus Marine toolbox and by
# polytope-client (~/.polytopeapirc), never copied here.

W = "work"
DT_MODELS = ["IFS-FESOM", "IFS-NEMO"]


rule all:
    input:
        "results/claims.json", "results/mhw_trends.csv", "results/reference_check.json",
        "results/doc_figure_marmara_days.json",


rule climatedt:
    input: rules.all.input, "results/climatedt_claims.json", "results/doc_figure_marmara_climatedt.json"


rule subsurface:
    input: rules.all.input, "results/subsurface_claims.json", "results/doc_figure_marmara_subsurface.json"


rule download:                      # OSTIA L4 reprocessed (then near real time) and the IHO sea polygons
    output: f"{W}/seas/iho.geojson"
    shell: "python pipeline/00_download.py {W}"

rule healpix:
    input: f"{W}/seas/iho.geojson"
    output: f"{W}/hp/marmara.nc", f"{W}/hp/aegean.nc", f"{W}/hp/black.nc", "results/cells.json"
    shell: "python pipeline/01_healpix.py {W}"

rule mhw:
    input: f"{W}/hp/marmara.nc"
    output: "results/claims.json", "results/mhw_trends.csv", "results/mhw_annual_marmara_paper.csv",
            "results/mhw_annual_marmara_detrended.csv"
    shell: "python pipeline/02_mhw.py {W}"

rule reference_check:               # our detection against Oliver's marineHeatWaves reference implementation
    input: f"{W}/hp/marmara.nc"
    output: "results/reference_check.json"
    shell: "python pipeline/09_check_reference.py {W}"

rule climatedt_download:            # region cut out by Polytope; resumable, one file per model and year
    input: f"{W}/hp/marmara.nc"
    output: expand(f"{W}/dt/{{model}}/{{year}}.npz", model=DT_MODELS, year=range(1990, 2050))
    shell: " && ".join(f"python pipeline/03_climatedt.py {W} {m}" for m in DT_MODELS)

rule climatedt_mhw:
    input: rules.climatedt_download.output
    output: "results/climatedt_claims.json", "results/doc_figure_marmara_climatedt.json", "figures/marmara_climatedt_mhw.png"
    shell: "python pipeline/04_climatedt_mhw.py {W}"

rule subsurface_test:
    input: f"{W}/hp/marmara.nc"
    output: "results/subsurface_claims.json", "results/doc_figure_marmara_subsurface.json", "figures/marmara_subsurface.png"
    shell: "python pipeline/05_subsurface.py {W}"


# ---------- figure of the country file (rows + PNG; the chart code is in docs/country_file/) ----------
rule doc_figures:
    input: "results/mhw_annual_marmara_paper.csv", "results/mhw_annual_marmara_detrended.csv"
    output: "results/doc_figure_marmara_days.json", "figures/doc_marmara_days.png"
    shell: "python pipeline/99_doc_figures.py"
