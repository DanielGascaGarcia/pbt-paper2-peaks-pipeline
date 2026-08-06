# PBT — Paper 2 Peaks Pipeline

**Article:** *Toward a Personalized Basal Tuner for Detecting Basal Rate
Inaccuracies in Type 1 Diabetes Mellitus Without Meal Data: Algorithm
Development and Retrospective Validation Study*
JMIR Diabetes 2025;10:e72769 — doi: 10.2196/72769

**Repository:** https://github.com/DanielGascaGarcia/pbt-paper2-peaks-pipeline

Pipeline to detect and characterise post-meal glucose peaks from CGM, compute
hourly relative change around those peaks, and summarise their distribution.
A single orchestrator executes every step in order.

> **This release accompanies a correction notice.** The version archived with
> the original article executes but does not regenerate the published values.
> Two defects were found and are fixed here; the reported figures were
> recomputed. See *Changes in this release*.

---

## Manuscript context

A meal-agnostic approach to assessing basal rate (BR) adequacy from CGM data.
It removes meal-related glucose excursions by peak detection rather than by
meal annotation, computes hourly relative BG change, and summarises 24-hour
behaviour to flag hours indicative of excessive or insufficient basal insulin.
It addresses scenarios in which closed-loop systems revert to manual mode or
are unavailable, and supports periodic BR review.

Meal annotations are used **only as the reference standard** for evaluating the
method. The method itself never reads them.

---

## The two branches

The pipeline runs two branches over the same data and compares them:

| Branch | Exclusion driven by | Produces |
|---|---|---|
| **Meal-based** | recorded meal events (4-hour window) | `Boxplot<ID>0-24total.csv` |
| **Peak-based** | detected peaks above the 95th percentile of height or width | `BoxplotPeak<ID>0-24total.csv` |

The meal branch is the reference the peak branch is measured against. It is
**not** an optional upstream artefact: the orchestrator runs both, so no file
from another repository is required. Earlier releases obtained the meal-branch
file from the Paper 1 repository and skipped the comparison when it was
absent; that dependency is gone.

---

## Method in brief

1. Parse and harmonise CGM, insulin and meal data from the OhioT1DM XML.
2. Apply a low-pass filter and detect BG peaks.
3. Exclude a 4-hour window around each prominent peak, from **1 h before to
   3 h after the peak**.
4. Build 24-hour composites and compute relative BG change by hour.
5. Add a three-level reliability flag based on the number of contributing days.
6. Export per-hour distributions and a 24-hour box plot summary.
7. Compare the two branches, and score peak–meal alignment (precision).

### Two windows, easily confused

| | Span | Used for |
|---|---|---|
| **Exclusion window** | 1 h before the peak to 3 h after it | removing the glucose excursion from the analysis |
| **Precision window** | 1 h before the estimated base point (peak time minus half the peak width) to 1 h after the peak | deciding whether a detected peak matches a recorded meal |

They serve different purposes and are not interchangeable. The exclusion window
is deliberately wide, so that the postprandial rise and its decay are removed.
The precision window is anchored on the base point rather than the peak,
because the meal precedes the rise, and it is narrower because it is a matching
criterion rather than a removal rule.

The precision window was defined from exploratory analysis of the variability
in the timing and quality of meal annotations. Widening it by one hour on the
matching side changes mean precision by a few percentage points in either
direction across participants and does not alter the included set.

---

## Inputs

- OhioT1DM per-participant XML files — **training split only**
  (`{id}-ws-training.xml`) — placed in `raw/`. The test split is not used at
  any stage.
- Intermediate files produced by the pipeline itself, written to `processed/`
- Configuration in `globals.py`

The OhioT1DM dataset is **not redistributed here**. It is freely available for
scientific purposes from
https://webpages.charlotte.edu/rbunescu/data/ohiot1dm/OhioT1DM-dataset.html

Because the dataset cannot be redistributed, the repository ships
`S.GenerateSampleData.py`, which produces **fully synthetic** files in the same
XML schema, so the pipeline can be executed end to end without access to the
real data. See *Demo mode*.

Participant identifiers: 540, 544, 552, 559, 563, 567, 570, 575, 584, 588,
591, 596. The training split provides between 38 and 47 days per participant
(mean 44); the article refers to this as the 45-day retrospective window, and
no analysis depends on a fixed number of days.

---

## Key outputs

### Intermediate, in `processed/`

| File | Contents |
|---|---|
| `glucose_level<ID>-ws-training_wCN <date>.csv` | meal branch, one file per day |
| `glucose_level<ID>-ws-training_wCNF <date>.csv` | peak branch, one file per day |
| `glucose_level<ID>-ws-training_Merge <date>.csv` | mask for a peak window crossing midnight |
| `BGwNMLeftJoinedPeak<ID>.csv` | left-joined table of filtered days |
| `BGHourRelativeChangePeak<ID><h>To<h+1>lastValues.csv` | last point per day and hour |
| `BoxplotPeak<ID>0-24total.csv` | 24-hour summary, peak branch |
| `Boxplot<ID>0-24total.csv` | 24-hour summary, meal branch |
| `BGHourRelativeChangePeak<ID>0To24medians_wCN.csv` | 24-hour medians plus reliability flag |
| `ComparisonJoinedPeakNoActivity<ID>.csv` | median relative change only |

Note the trailing space in `_wCN ` and `_wCNF `: a prefix match on `_wCN`
alone would also match the peak-branch files.

Within a day file, three columns carry glucose and each means something
different:

- **`BGValue2`** — the readings as parsed, before any exclusion. The sensor
  record for that day.
- **`BGValue`** — the readings that survive exclusion. Blank where the meal
  window or the peak window removed the reading.
- **`ValueCh`** — the readings that were removed; the complement of `BGValue`.

`BGValue` feeds the hourly relative change; `ValueCh` is what the "segments
removed" panel of Figure 3 plots.

### Reported tables, in `results/tables/`

| File | Contents |
|---|---|
| `Table3.csv` | per participant: precision, successes, scored peaks, missing meal files, quality flag |
| `PrecisionSummary.csv` | precision at participant level (mean, SD, *t* interval) and as a pooled count |
| `Figure7_data.csv`, `Figure7_key_values.csv` | hours by insulin condition, and the values quoted in the caption |
| `SumUMedRelChange_byID.csv`, `SummaryStats_UMedRelChange.csv` | daily cumulative average per participant and its summary |
| `MedRelChange_extremes.csv` | interindividual range of the relative change |
| `Table2_NonInferiority.csv` | the superseded noninferiority analysis, one row per participant |
| `CGMCoverage_byID.csv`, `CGMCoverage_byDay.csv` | sensor coverage, descriptive |

Every figure that carries a number in the article has a corresponding CSV
here, so the reported values can be checked without re-running the pipeline.

---

## Environment

**Python 3.9.12**, conda, Windows. Dependencies are pinned in
`requirements.txt`:

```
numpy==2.0.2
pandas==2.2.2
scipy==1.13.1
matplotlib==3.9.2
seaborn==0.13.2
pillow==9.0.1
```

```bash
conda create -n pbt python=3.9.12
conda activate pbt
pip install -r requirements.txt
```

This is the environment in which the **corrected** values reproduce, verified
by independent runs from a clean state. It is the same specification used for
the Paper 1 pipeline, so both repositories run under one environment. It is
not a record of the environment used for the originally published run, which
was not preserved.

Before running, confirm the interpreter actually in use — a mismatched
environment is the most common cause of a run that behaves unexpectedly:

```bash
python -c "import sys; print(sys.executable)"
```

---

## Running the pipeline

```bash
python 17.ScriptforTestExperiment2.py
```

The orchestrator loops over the participant IDs in `globals.py`, setting
`PATIENT_ID` for each subprocess, then runs the aggregate scripts once. It
clears `processed/` before starting, and exits with a non-zero status if any
step fails — without running the aggregate scripts, which read all
participants at once and would otherwise produce output from an incomplete
set.

### With the real dataset

Leave `DEMO = False` in `globals.py` and place the `{id}-ws-training.xml`
files directly in `raw/`. If any expected file is absent the run stops
immediately and names what is missing, rather than failing several steps
later. This is what produced the `SET_ME-ws-training.xml` failure reported
against the earlier deposit.

### Demo mode

Set `DEMO = True` in `globals.py`. The orchestrator regenerates synthetic
files into `sample_data/` and runs on those. Demo mode never reads or writes
`raw/`, so leaving the flag set by accident cannot overwrite data obtained
under the Data Use Agreement.

The generator can also be run on its own:

```bash
python S.GenerateSampleData.py --out ./sample_data --days 5 --ids 559 588
```

**Demo output is meaningless.** It exists to show that the code runs, not to
approximate any result. With the default five days per participant the figures
are sparse and the last day of each participant is incomplete, because the
midnight-overflow trimming needs the following day to close. That is expected.

### A note on state

**Run against an empty `processed/`.** Several steps collect their inputs by
listing whatever per-day files are present rather than regenerating a known
list, and the midnight-overflow step rewrites those files in place. A file
left behind by an earlier or partial run is therefore picked up as if it
belonged to the current one, and the number of days entering the analysis
reflects the state of the directory instead of the input data.

This is the single most important operational note in this package: it is the
defect behind the divergence between the originally published outputs and a
clean run. The orchestrator clears `processed/` for this reason; **clear it by
hand if you run individual steps.**

---

## Execution order

The orchestrator runs four phases per participant, then the aggregate scripts.

**Common** — `0.Parser.py` → `1.ColumnNamer.py` → `2.Disaggregator.py` →
`3.PivotGeneratorBG.py`

**Meal branch** — `4.MealBolusDetection.py` → `5.MergeBGClean.py` →
`6.SplitHours.py` → `7.InterpolationBGHourly.py` → `8.RelativeChange.py` →
`9.Boxplot.py`

**Peak branch** — `4.PeaksDetection.py` → `5.MergePeaksNextDay.py` →
`6.MergePeaks.py` → `7.SplitHoursPeaks.py` → `8.RelativeChangePeaks.py` →
`9.BoxplotPeak.py`

**Comparison** — `10.Non-inferiorityTest.py` →
`10.PivotGeneratormediansPeak.py` → `12.MergeRChBasalPeakNoAct.py`

**Aggregate, once** — `G.CGMCoverage.py` → `G.PrecisionSummary.py` →
`G.GraphResultsPeak.py` → `G.Graph3DCleanBGPeak.py` →
`G.Graph3DPeaksRemoved.py` → `G.Graph3DComplete.py` → `G.ComposeFigure2.py` →
`G.ComposeFigure3.py`

The two compose scripts run last because they read panel PNGs written earlier.

---

## Configuration

All configuration lives in `globals.py`. Nothing is hardcoded in the
individual scripts. Paths are resolved relative to that file, so the
repository runs as cloned; the previous version carried absolute Windows
paths, which is why the deposited code did not run elsewhere.

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
| `path1`-`path4` | input, `processed/`, `results/figures/`, `results/tables/` |

---

## Repository layout

```
pbt-paper2-peaks-pipeline/
├─ globals.py                        configuration
├─ 0.Parser.py … 12.*.py             per-participant pipeline, both branches
├─ G.*.py                            aggregate scripts
├─ S.GenerateSampleData.py           synthetic data generator
├─ 17.ScriptforTestExperiment2.py    orchestrator
├─ requirements.txt
├─ CITATION.cff
├─ LICENSE
├─ raw/                              input data (not distributed)
├─ sample_data/                      synthetic data (regenerated; not versioned)
├─ processed/                        intermediates (cleared on each run)
└─ results/
   ├─ figures/
   └─ tables/
```

`sample_data/` and `processed/` are regenerated and are listed in
`.gitignore`.

---

## Figure map

| Article item | Produced by |
|---|---|
| Figure 1 (pipeline diagram) | not generated by code |
| Figure 2, panels a and b | `4.PeaksDetection.py` (when `id == idG` and the day index is `FIG2_DAY`) |
| Figure 2, composite | `G.ComposeFigure2.py` |
| Figure 3, panel a — all readings | `G.Graph3DComplete.py` |
| Figure 3, panel b — segments removed | `G.Graph3DPeaksRemoved.py` |
| Figure 3, panel c — remaining readings | `G.Graph3DCleanBGPeak.py` |
| Figure 3, composite | `G.ComposeFigure3.py` |
| Figure 4 (hourly box plots) | `9.BoxplotPeak.py` |
| Figure 5 (branch comparison) | `10.Non-inferiorityTest.py` |
| Figure 6 (relative change and reliability) | `12.MergeRChBasalPeakNoAct.py` |
| Figure 7 (category histogram) | `G.GraphResultsPeak.py` |
| Figure 8 (box plots by insulin condition) | `G.GraphResultsPeak.py` |

Panel letters and the annotation boxes used in the article are applied
afterwards in an image editor. The underlying values are unaffected.

---

## Changes in this release

### Corrections that change reported values

- **Meal-annotation table not reset between days.** A day without annotations
  inherited the previous day's table and raised an exception; the exception
  counter was then reported as the number of missing meal files. This inflated
  the exclusion counts and changed which participants were excluded from the
  precision analysis.
- **Off-by-one in the box plot step.** The row count was derived from the
  column count of a file with a different number of non-data columns, silently
  discarding the last day of every participant. Present in both branches.
- **Off-by-one in the relative-change step, peak branch.** The loop writing the
  per-hour last-value files used the offset of the loop above it, which reads a
  file with a different number of non-data columns, leaving those files one row
  short.
- **Blank-line handling, peak branch.** Days with no data were written as a
  single space and dropped when the file was read back, because blank lines are
  skipped by default; every later value then moved up one position and the row
  index no longer identified the day. The files are now read with
  `skip_blank_lines=False` and coerced to numeric. The set of values was
  unchanged; only their position was.

Every reported figure was recomputed. The central finding is unchanged.

### Statistical treatment

- The noninferiority analysis is **superseded**. It treated hourly intervals
  within participants as independent observations, which produced degrees of
  freedom in the hundreds to low thousands. It is replaced by an agreement
  analysis at participant level. The script is retained so that the published
  analysis remains inspectable; its output on corrected data differs from the
  published table.
- **All intervals are now *t* intervals on participant-level values.** The
  Wilson score method applies to a single binomial proportion; the reported
  precision is a mean of per-participant precisions. Pooled fractions are
  reported as counts, without intervals, because the underlying observations
  are clustered within participants.
- The exclusion criterion is **declared**: more than 20% of a participant's
  days without meal annotation. It was not stated explicitly in the article.

### Reproducibility

- The orchestrator clears `processed/` before every run.
- Missing input files are reported up front; a failed step exits non-zero and
  the aggregate scripts are not run on an incomplete set.
- Both branches now run from this repository; no artefact from the Paper 1
  repository is required.
- A synthetic data generator allows the pipeline to be executed without the
  dataset.
- Paths resolved relative to `globals.py`; thresholds, unit conversion and
  figure switches centralised there.

### Metadata

- Table 1: the participant-selection column described what participants
  reported rather than which sensor band they wore. Pump model for 552 and age
  group for 596 corrected against the dataset documentation.
- Textbox 1: a pseudocode line subtracted zero rather than one day.
- Figure 3 caption: described the panel as a single day of 45 readings.

---

## Implementation notes and known limitations

### Peak detection filter

A 9th-order Butterworth low-pass filter, normalised cutoff **0.4 of Nyquist**
in the detection stage and **0.8 of Nyquist** in the preliminary pass used to
derive the 95th-percentile thresholds. At the 5-minute CGM sampling interval,
0.4 attenuates oscillations with periods shorter than about 25 minutes.

The variables `fs` and `cutoff` in `4.PeaksDetection.py` are expressed in
nominal Hz. These are **not** physical frequencies — the sampling rate is one
sample per 5 minutes. Only the ratio `cutoff / (fs / 2)` is meaningful.

The first 10 filtered samples of each day are replaced by their unfiltered
values, to suppress the filter's start-up transient. Filtering uses
`scipy.signal.lfilter`, which is causal and introduces a small phase lag, so
detected peaks sit slightly later than the underlying maximum. This is one
reason the meal-matching window extends further before the peak than after it.

Using the same cutoff in both stages leaves mean precision essentially
unchanged (70.65% against 70.64% across the nine included participants) and
does not alter the included set, although individual precisions shift by up to
five percentage points in either direction and between-participant dispersion
increases.

### Midnight-overflow trimming (peak branch only)

The branches are not symmetric by construction. All trimming in the meal
branch is intra-day. In the peak branch, when an exclusion window extends past
midnight the detection step writes a per-minute 0/1 mask for the following day,
and `5.MergePeaksNextDay.py` applies it, rewriting that day's file in place.

When the mask is applied it is first aligned onto a per-minute grid and
interpolated. Because it carries values only at CGM sample times, the
interpolation assigns fractional values to the minutes in between, and the
threshold used (`> 0`) treats any fractional value as masked. The excluded
window is therefore widened by a few minutes at each boundary.

This is conservative and applied identically to all participants and days. It
is documented rather than altered, so that the deposited code reproduces the
reported figures exactly. Users adapting the code may prefer to forward-fill
the mask rather than interpolate it, or to threshold at `>= 0.5`.

### Interpolation and hourly boundaries

The two branches interpolate the glucose series at different points, and this
is why their hourly values differ in numeric type.

- **Peak branch:** interpolation is applied in the detection step, on the
  continuous per-minute grid for the whole day, before the hourly split.
- **Meal branch:** interpolation is applied after the split, to each hourly
  segment independently.

Both use `limit=5, limit_direction='both'`. The difference lies in what those
parameters do at an hour boundary. In the meal branch the leading and trailing
minutes of each segment are filled by backward and forward fill — exact copies
of the nearest CGM reading. In the peak branch the first minute of an hour
falls between two readings and receives a genuine linear interpolation.

Because the hourly relative change is the last value of the hour minus the
first, meal-branch values are integers and peak-branch values carry decimals.
The magnitudes are equivalent; only the representation differs. This affects
tests of exact equality: a value of exactly zero is far more likely to arise in
the meal branch, which is why the count of "optimal" hours is fragile.

### Day ordering and column indexing

The detection and overflow steps sort per-day files chronologically. The two
merge steps do not — they enumerate files in filesystem order. The day columns
of the joined tables (`BGValue0`, `BGValue1`, …) are therefore indexed in
filesystem order rather than by date, and the two branches need not use the
same ordering. A naive `sorted()` would not fix this, because the filenames
carry the weekday before the date.

No reported statistic depends on that order: all summaries are computed per
hour of day or per participant, and none pairs the branches day by day. The
same applies to the row index of the box plot files, which reflects the day's
column position rather than the calendar date.

Filenames are parsed with fixed character offsets that assume a three-digit
participant identifier. This holds for all twelve OhioT1DM identifiers.

### Input schema sensitivity

The XML parser assigns column names by the **position** of each child element
within the patient record, not by its tag name. A valid OhioT1DM file whose
`basis_*` elements appear in a different order will produce silently
mislabelled columns, with no error raised until several steps later. The
expected order is `basis_heart_rate`, `basis_gsr`, `basis_skin_temperature`,
`basis_air_temperature`, `basis_steps`, `basis_sleep`. The synthetic generator
emits them in that order for the same reason.

### Parsing failures are silent

The parsing and column-naming steps wrap each variable in a bare `except` and
print a message rather than stopping. Check the console output of the first
steps before trusting a run.

### Exclusion criterion

Participants are excluded from the precision analysis when **more than 20% of
their days carry no meal annotation** (`globals.MISSING_THRESHOLD`).
`4.PeaksDetection.py` writes `FilesMissing`, `FilesTotal`, `MissingPct` and a
`Quality` flag per participant into `Table3.csv`.

The criterion was not stated explicitly in the article and is declared here.
The corrected counts are lower than those printed in the original Table 3,
because that column was populated from an exception counter that conflated
genuinely absent meal files with a code fault; the rule itself is unchanged.

Meal annotations are required only as the reference standard, not by the
method. Excluded participants remain in the descriptive interindividual
analyses.

### CGM coverage

`G.CGMCoverage.py` reports, per participant, the proportion of each day for
which a sensor reading is present. It is descriptive: no day is excluded on
that basis and no reported value depends on it.

Coverage is counted from `BGValue2`, the column before meal-related exclusion,
so the figure measures the sensor record and not the effect of the algorithm.
Counts are expressed against 288, the number of readings a complete day holds
at 5-minute sampling.

Incomplete days are kept. An hour with no reading contributes nothing to the
median for that hour, so it is neither imputed nor allowed to shift the
composite day. The three-level reliability measure marks hours supported by
few days, which is how sparse coverage becomes visible rather than being
silently dropped.

Consensus guidance recommends at least 70% CGM coverage over a 14-day period
before deriving metrics such as time in range. That guidance concerns metrics
computed over a continuous window. The composite day used here aggregates each
hour across the whole record, so a day with an interrupted sensor contributes
fewer values rather than distorting a continuous series. The coverage tables
are reported so that readers can apply their own threshold.

### Panel letters and annotation boxes

Figure 6 carries "A", "B" and "C" markers and the boxes around the intervals
they identify. The code produces the plot; those annotations are applied
afterwards in an image editor and are not reproduced by a run. The underlying
values are unaffected.

### Rendering

Font availability and backend differences change pixel output. The values are
reproducible; the rendering is not bit-identical.

---

## Reproducibility statement

Reproducibility was verified by executing the full pipeline from a clean state
and comparing the resulting artefacts across independent runs, which were
identical.

The code archived with the original article executes but does not regenerate
the outputs reported there. The most likely explanation is that the original
outputs were produced across several partial runs accumulating in a shared
output directory — no stage removes outputs from a previous run, and the merge
stage consumes whatever intermediate files it finds — a condition that cannot
be recreated. This package supersedes that archive.

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
- Software compendium — 10.5281/zenodo.17675142

---

## License

MIT. See `LICENSE`.
