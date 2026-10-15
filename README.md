# PBT — Paper 2 Peaks Pipeline

**Article:** *Toward a Personalized Basal Tuner for Detecting Basal Rate
Inaccuracies in Type 1 Diabetes Mellitus Without Meal Data: Algorithm
Development and Retrospective Validation Study.* JMIR Diabetes
2025;10:e72769. doi: 10.2196/72769

**Repository:** https://github.com/DanielGascaGarcia/pbt-paper2-peaks-pipeline

This code produces every table and data figure of the article. A single
orchestrator runs every step in order.

---

## What it does

A meal-agnostic method to assess basal rate adequacy from CGM data. Meal-related
glucose excursions are removed by peak detection instead of meal annotation;
the hourly relative change of BG is then summarised over a 24-hour composite
day to flag hours that suggest excessive or insufficient basal insulin.

The pipeline runs two branches over the same data:

| Branch | Exclusion driven by | Produces |
|---|---|---|
| **Peak-based** (the method) | detected peaks whose prominence or width exceeds the participant's 95th percentile | `BoxplotPeak<ID>0-24total.csv` |
| **Meal-based** (reference) | recorded meal events (4-hour window) | `Boxplot<ID>0-24total.csv` |

Meal annotations are used only as the reference standard; the method never
reads them.

**Method in brief**

1. Parse and harmonise CGM, insulin and meal data from the OhioT1DM XML.
2. Apply a low-pass filter and detect BG peaks.
3. Exclude a 4-hour window around each prominent peak, from **1 h before to
   3 h after the peak**.
4. Build 24-hour composites and compute relative BG change by hour.
5. Add a three-level reliability flag based on the number of contributing days.
6. Export per-hour distributions and a 24-hour box plot summary.
7. Compare the two branches, and score peak–meal alignment (precision).

Further technical detail, including the two windows (exclusion and
precision), is in [`docs/NOTES.md`](docs/NOTES.md).

---

## Data

- OhioT1DM training files (`{id}-ws-training.xml`) for participants 540, 544,
  552, 559, 563, 567, 570, 575, 584, 588, 591 and 596, placed in `raw/`.
  The test split is not used. The training split provides between 38 and 47
  days per participant (mean 44); the article refers to this as the 45-day
  retrospective window, and no analysis depends on a fixed number of days.
- The dataset is **not redistributed**; it is available for scientific purposes
  from https://webpages.charlotte.edu/rbunescu/data/ohiot1dm/OhioT1DM-dataset.html
- Without the dataset, the pipeline can be run on **synthetic** files in the
  same schema (see *Running*). Their output is not comparable with any
  reported result.

---

## Installation

Python 3.9.12. Dependencies are pinned in `requirements.txt`.

```bash
conda create -n pbt python=3.9.12
conda activate pbt
pip install -r requirements.txt
python --version                 # expect 3.9.12
```

A `venv` with Python 3.9 also works: create it, activate it and run
`pip install -r requirements.txt`. Reproducibility was verified with conda;
other Python versions have not been tested. The same environment runs the
Paper 1 pipeline.

Before running, confirm the interpreter in use:

```bash
python -c "import sys; print(sys.executable)"
```

---

## Running

```bash
python 17.ScriptforTestExperiment2.py
```

The orchestrator clears `processed/`, runs both branches for every
participant, checks that every participant produced its outputs, and then runs
the aggregate scripts once. It stops with a non-zero exit status if any step
fails.

- **Real data:** `DEMO = False` in `globals.py`, with the XML files in `raw/`.
- **Demo mode:** `DEMO = True`. Synthetic files are generated into
  `sample_data/` and every output goes to `demo_output/`; `raw/` and
  `results/` are never touched.

The generator can also be run on its own:

```bash
python S.GenerateSampleData.py --out ./sample_data --days 5 --ids 559 588
```

If you run individual scripts by hand, clear `processed/` first.

### Execution order

The orchestrator runs four phases per participant, then the aggregate scripts.

**Common** — `0.Parser.py` → `1.ColumnNamer.py` → `2.Disaggregator.py` →
`3.PivotGeneratorBG.py`

**Meal branch** — `4.MealBolusDetection.py` → `5.MergeBGClean.py` →
`6.SplitHours.py` → `7.InterpolationBGHourly.py` → `8.RelativeChange.py` →
`9.Boxplot.py`

**Peak branch** — `4.PeaksDetection.py` → `5.MergePeaksNextDay.py` →
`6.MergePeaks.py` → `7.SplitHoursPeaks.py` → `8.RelativeChangePeaks.py` →
`9.BoxplotPeak.py`

**Comparison** — `10.ComparisonFigure.py` →
`10.PivotGeneratormediansPeak.py` → `12.MergeRChBasalPeakNoAct.py`

**Aggregate, once** — `G.CGMCoverage.py` → `G.PrecisionSummary.py` →
`G.GraphResultsPeak.py` → `G.Graph3DCleanBGPeak.py` →
`G.Graph3DPeaksRemoved.py` → `G.Graph3DComplete.py` → `G.ComposeFigure2.py` →
`G.ComposeFigure3.py`

The agreement analysis runs in the same aggregate block, after
`G.PrecisionSummary.py` (it reads `Table3.csv` for the analysed set):
`G.BADescriptives.py` → `G.BlandAltman.py` → `G.Divergence.py` →
`G.Branches.py`. The four share one reader, `pbt_io.py`, so every script reads
the branch files the same way and takes the analysed set from `Table3.csv`.

The two compose scripts run last because they read panel PNGs written earlier.

---

## Outputs

Figures are written to `results/figures/` and tables to `results/tables/`.

The package writes every table the code computes. The article reports a
selection. Each file is listed here with the use it has.

**Reported in the article**

| File | Contents |
|---|---|
| `Table3.csv` | per participant: precision, successes, scored peaks, days without meal annotation, quality flag |
| `PrecisionSummary.csv` | precision at participant level (mean, SD, *t* interval) and as a pooled count |
| `Figure7_data.csv`, `Figure7_key_values.csv` | hours by insulin condition, and the values quoted in the caption |
| `SumUMedRelChange_byID.csv`, `SummaryStats_UMedRelChange.csv` | per participant, the sum over the day of the absolute hourly median relative changes (the article's daily cumulative value, not a glucose level), and its summary |
| `MedRelChange_extremes.csv` | interindividual range of the relative change |
| `BlandAltman_summary.csv` | agreement between branches; row `absolute (primary)` is the analysis reported in the article |
| `BlandAltman_byID.csv` | per participant: both branch summaries, their differences, and whether the participant is in the analysed set |

**Additional analyses, not reported in the article**

| File | Contents |
|---|---|
| `BlandAltman_summary.csv`, other rows | `signed` (directional offset), `absolute, all cells` (level of aggregation), and the two `all 12 participants` rows (participant set) |
| `BA_descriptives_byID.csv`, `BA_descriptives_cohort.csv`, `BA_descriptives_sensitivity.csv` | descriptive statistics of the data entering the agreement analysis |
| `Divergence_byID.csv`, `Divergence_summary.csv`, `Divergence_anchor.csv` | Jensen-Shannon and Kullback-Leibler divergence per participant, their summary, and the between-participant anchor against which they are read |

**Diagnostic**

| File | Contents |
|---|---|
| `CGMCoverage_byID.csv`, `CGMCoverage_byDay.csv`, `CGMCoverage_summary.csv` | sensor coverage, descriptive |

Every figure that carries a number in the article has a
corresponding CSV here, so the reported values can be checked without
re-running the pipeline.

### Sensitivity analysis

`sensitivity/` holds versions of `4.PeaksDetection.py` and
`7.SplitHoursPeaks.py` in which the peak branch interpolates after the hourly
split, as the meal branch does. To run it, copy the repository, replace those
two scripts with the ones in `sensitivity/`, and run the orchestrator in the
copy. Precision and Table 3 do not change; the agreement and interindividual
tables do.

The tables of that run are included in `results/sensitivity/tables/`. They are
not produced by the main pipeline: running the orchestrator in this repository
never writes or updates them. To regenerate them, run the sensitivity analysis
in a copy as above and copy its `results/tables/` into
`results/sensitivity/tables/`.

### Figure map

| Article item | Produced by |
|---|---|
| Figure 1 (pipeline diagram) | not generated by code |
| Figure 2, panels A and B | `4.PeaksDetection.py` (when `id == idG` and the day index is `FIG2_DAY`) |
| Figure 2, composite | `G.ComposeFigure2.py` |
| Figure 3, panel A — all readings | `G.Graph3DComplete.py` |
| Figure 3, panel B — segments removed | `G.Graph3DPeaksRemoved.py` |
| Figure 3, panel C — remaining readings | `G.Graph3DCleanBGPeak.py` |
| Figure 3, composite | `G.ComposeFigure3.py` |
| Figure 4 (hourly box plots) | `9.BoxplotPeak.py` |
| Figure 5 (branch comparison) | `10.ComparisonFigure.py` |
| Figure 6 (relative change and reliability) | `12.MergeRChBasalPeakNoAct.py` |
| Figure 7 (category histogram) | `G.GraphResultsPeak.py` |
| Figure 8 (box plots by insulin condition) | `G.GraphResultsPeak.py` |
| Both branches, all 12 participants (additional figure, not in the article) | `G.Branches.py` -> `Figure9.png` |

Panel letters of Figures 2 and 3 are added by the compose scripts. The
annotation boxes of Figure 6 are added afterwards in an image editor; the
underlying values are unaffected.

---

## Configuration

`globals.py` holds the paths, the participants, the exclusion criterion, the
unit conversion and the figure switches. The parameters of the algorithm
itself (the 95th-percentile thresholds, the 100 mg/dL peak height, the
exclusion windows, the reliability percentiles) are
set in the scripts that use them and are described in those scripts' headers.
Paths are resolved relative to `globals.py`, so the
repository runs as cloned.

| Name | Purpose |
|---|---|
| `id` | current participant, read from the `PATIENT_ID` environment variable |
| `ids` | the twelve participants |
| `idG` | participant used for the single-subject worked examples (588) |
| `DEMO` | `False` to use `raw/`; `True` to generate and use synthetic data |
| `DEMO_DAYS`, `DEMO_SEED` | days per participant and base seed for the generator |
| `FIG2_DAY` | zero-based day index for the Figure 2 worked example |
| `MISSING_THRESHOLD` | exclusion criterion: more than this fraction of days without meal annotation |
| `MGDL_TO_MMOL` | unit conversion factor (1/18) |
| `FIGURE_TITLES` | `False` for submission figures; `True` to render titles for local review |
| `path1`-`path4` | input, `processed/`, `results/figures/`, `results/tables/` (all four under `demo_output/` when `DEMO` is True) |

---

## Repository layout

```
pbt-paper2-peaks-pipeline/
├─ globals.py                        configuration
├─ 0.Parser.py … 12.*.py             per-participant pipeline, both branches
├─ G.*.py                            aggregate scripts
├─ pbt_io.py                         shared reader for the agreement scripts
├─ S.GenerateSampleData.py           synthetic data generator
├─ sensitivity/                      two scripts for the interpolation sensitivity analysis
├─ 17.ScriptforTestExperiment2.py    orchestrator
├─ requirements.txt
├─ CITATION.cff
├─ docs/NOTES.md                     implementation notes
├─ LICENSE
├─ raw/                              input data (not distributed)
├─ sample_data/                      synthetic data (regenerated; not versioned)
├─ processed/                        intermediates (cleared on each run)
├─ demo_output/                      all demo-mode output (not versioned)
└─ results/
   ├─ figures/
   ├─ tables/
   └─ sensitivity/tables/            tables of the interpolation sensitivity run
```

`sample_data/`, `processed/`, `demo_output/` and `results/figures/` are created
by the code and are listed in `.gitignore`. `raw/` is the only directory you need to create
yourself, and only when running against the real dataset.

---

## Reproducibility

Two runs of the full pipeline from a clean state give identical results: the
eighteen tables in `results/tables/` are identical byte for byte.

---

## Citation

**Article:** Gasca Garcia D, Thabit H, Nutter PW, Harper S. Toward a
Personalized Basal Tuner for Detecting Basal Rate Inaccuracies in Type 1
Diabetes Mellitus Without Meal Data: Algorithm Development and Retrospective
Validation Study. *JMIR Diabetes.* 2025;10:e72769. doi: 10.2196/72769

**Software:** Gasca García D. *PBT — Paper 2 Peaks Pipeline* [Computer
software]. Zenodo. doi: **10.5281/zenodo.17393514**

The DOI above is the concept DOI: it always resolves to the most recent
version. See `CITATION.cff`.

```bibtex
@software{gasca_garcia_pbt_paper2_peaks,
  author  = {Gasca García, Daniel},
  title   = {PBT — Paper 2 Peaks Pipeline},
  year    = {2026},
  doi     = {10.5281/zenodo.17393514},
  url     = {https://doi.org/10.5281/zenodo.17393514}
}
```

Related deposits, by concept DOI:

- Paper 1 pipeline — 10.5281/zenodo.17392920
- Software compendium — 10.5281/zenodo.17675141

---

## License

MIT. See `LICENSE`.
