# Release notes — PBT, Paper 2 Peaks Pipeline

DOI (this version): assigned on publication.
Concept DOI, always resolving to the latest version: **10.5281/zenodo.17393514**

This release accompanies a correction notice for *JMIR Diabetes*
2025;10:e72769. It corrects the defects that change reported values, replaces
the statistical treatment of the branch comparison, adds a distributional
comparison and a figure of both branches for all participants, and makes the
pipeline runnable from a clean clone.

---

## Corrections that change reported values

- **Meal-annotation table not reset between days.** A day without annotations
  inherited the previous day's table and raised an exception. The exception
  counter was then reported as the number of missing meal files, which
  inflated the exclusion counts in Table 3 and changed which participants were
  excluded from the precision analysis.
- **Off-by-one in the box plot step.** The row count was derived from the
  column count of a file with a different number of non-data columns, silently
  discarding the last day of every participant. Present in both branches.
- **Off-by-one in the relative-change step, peak branch.** The loop writing the
  per-hour last-value files used the offset of the loop above it, leaving those
  files one row short. Superseded by the corrected row count; no reported value
  depends on it.
- **Blank-line handling, peak branch.** Days with no data were written as a
  single space and skipped when read back, so later values moved up one
  position. The files are now read with `skip_blank_lines=False` and coerced to
  numeric. The set of values was unchanged; only their position was.
- **Midnight overflow.** Both detection steps carried the part of an exclusion
  window that passes midnight into the next CGM file in date order, whatever
  its date, and the meal branch failed on the last day of a record. The
  overflow is now carried only to the next calendar day, and the last day is
  processed completely. The peak branch does not change; the meal branch
  changes by 1 to 3 values in 6 participants.
- **Noninferiority test implementation.** The one-sided p-value was obtained by
  halving a two-sided p-value, which discards the sign of the statistic, so
  participants failing the criterion were counted as meeting it; and the
  variance of the reference term was not scaled by (1 + margin)². Both are
  corrected: 5 of the 12 participants meet the criterion, not 9. The analysis
  itself is superseded (below).

Every reported figure was recomputed from this release. The central finding —
that basal rates are off target in almost every hourly interval — is unchanged.

## Statistical treatment

- The **noninferiority analysis is superseded**. It treated hourly intervals
  within participants as independent observations, producing degrees of freedom
  in the hundreds to low thousands. It is replaced by an agreement analysis at
  participant level, where each participant contributes one value.
  `10.Non-inferiorityTest.py` is retained so the published analysis remains
  inspectable; its output on corrected data differs from the published table.
- **Agreement analysis.** Hourly medians per participant and branch, averaged
  in absolute value over the hours with data in both branches; Bland-Altman
  analysis over participants (`G.BlandAltman.py`), with Shapiro-Wilk, a
  proportional-trend check and a Wilcoxon signed-rank test. Sensitivity rows:
  signed values, all cells, and all 12 participants. Descriptive statistics of
  the data entering it: `G.BADescriptives.py`.
- **Distributional comparison.** Jensen-Shannon and Kullback-Leibler divergence
  between the branches' hourly medians (8 common bins, smoothing +0.5), read
  against a between-participant anchor (`G.Divergence.py`).
- **All confidence intervals are now t intervals over participant-level
  values.** The Wilson score method applies to a single binomial proportion,
  whereas the reported precision is a mean of per-participant precisions.
  Pooled fractions are reported as counts, without intervals, because the
  underlying observations are clustered within participants. The proportion
  of off-target hours (287 of 288) is reported without an interval, because a
  t interval on the participant-level values exceeds 100%.
- The **exclusion criterion is declared**: more than 20% of a participant's
  days without meal annotation, held in `globals.MISSING_THRESHOLD`.
- **Sensitivity to the interpolation point.** The two branches interpolate at
  different points relative to the hourly split. The two scripts in
  `sensitivity/` make the peak branch interpolate after the split, as the meal
  branch does; with them the primary bias is +0.75 mg/dL (95% CI −0.76 to
  +2.27), the signed offset stays positive in all 12 participants, and 274 of
  288 hourly intervals remain off target. Precision and Table 3 are unchanged.

## Reproducibility

- The orchestrator clears `processed/` before every run. Several steps collect
  their inputs by listing that directory, so files left by an earlier run were
  previously picked up as if they belonged to the current one. This is the
  defect behind the divergence between the published outputs and a clean run.
- Missing input files are reported up front instead of surfacing as an
  unrelated error several steps later.
- A failed step stops the run with a non-zero exit status, and the aggregate
  scripts are not executed on an incomplete participant set.
- The per-participant summary files for both branches are checked after the
  loop. A run stops if any of them is absent or empty.
- **Both branches now run from this repository.** Earlier releases obtained the
  meal-branch box plot from the Paper 1 repository and skipped the comparison
  when it was absent; that dependency is gone.
- Verified by two independent runs from a clean state with the final code:
  ten output artefacts compared, identical byte for byte.

## Running without the dataset

`S.GenerateSampleData.py` generates fully synthetic files in the OhioT1DM
schema, so the pipeline can be executed end to end without access to the real
data. Enabled with `DEMO = True` in `globals.py`, which never reads or writes
`raw/`. Synthetic output is not comparable with any reported result.

Demo mode redirects its output as well as its input, under `demo_output/`.
Previously only the input path was redirected, so a demo run overwrote the
tracked tables under `results/tables/` with synthetic values.

## Configuration

Paths are resolved relative to `globals.py`; the repository runs as cloned. The
previous version carried absolute Windows paths, which is why the deposited
code did not run elsewhere and produced the reported `SET_ME-ws-training.xml`
failure.

Centralised in `globals.py`: participant identifiers, the worked-example
participant and day, the exclusion threshold, the unit conversion factor, the
figure-title switch, and the demo settings.

## New outputs

- `PrecisionSummary.csv` — precision at participant level (mean, SD, t
  interval) and as a pooled count, for the included set and for all twelve.
- `CGMCoverage_byID.csv`, `CGMCoverage_byDay.csv` — sensor coverage per
  participant and per day, reported descriptively.
- `BlandAltman_summary.csv`, `BlandAltman_byID.csv` — the agreement analysis
  and its sensitivity rows.
- `BA_descriptives_byID.csv`, `BA_descriptives_cohort.csv`,
  `BA_descriptives_sensitivity.csv` — the data entering it.
- `Divergence_byID.csv`, `Divergence_summary.csv`, `Divergence_anchor.csv` —
  the distributional comparison.
- `Figure9.png` — hourly profiles of both branches for all
  12 participants (`G.Branches.py`).
- `Table2_NonInferiority.csv` — the superseded analysis, one row per
  participant, including both the Welch and pooled degrees of freedom.
- The tables behind every reported figure, under `results/tables/`.

## Metadata corrections

- Table 1: the participant-selection column described what participants
  reported rather than which sensor band they wore. Pump model for 552 and age
  group for 596 corrected against the dataset documentation.
- Textbox 1: a pseudocode line subtracted zero rather than one day, and the
  95th percentiles were shown inside the per-day loop instead of once per
  participant.
- Figure 3 caption: described the panel as a single day of 45 readings.
- Figure 4 legend: the reference band was labelled "No significant change";
  it is a fixed visual reference and is now labelled
  "Reference range (±36 mg/dL)".
- Figure 6 caption: "C" is described as marking occasional extreme values,
  not values in periods of low reliability.

---

## Execution order

Four phases per participant, then the aggregate scripts.

**Common** — `0.Parser` → `1.ColumnNamer` → `2.Disaggregator` →
`3.PivotGeneratorBG`

**Meal branch** — `4.MealBolusDetection` → `5.MergeBGClean` → `6.SplitHours` →
`7.InterpolationBGHourly` → `8.RelativeChange` → `9.Boxplot`

**Peak branch** — `4.PeaksDetection` → `5.MergePeaksNextDay` → `6.MergePeaks` →
`7.SplitHoursPeaks` → `8.RelativeChangePeaks` → `9.BoxplotPeak`

**Comparison** — `10.Non-inferiorityTest` → `10.PivotGeneratormediansPeak` →
`12.MergeRChBasalPeakNoAct`

**Aggregate, once** — `G.CGMCoverage` → `G.PrecisionSummary` →
`G.BADescriptives` → `G.BlandAltman` → `G.Divergence` → `G.Branches` →
`G.GraphResultsPeak` → `G.Graph3DCleanBGPeak` → `G.Graph3DPeaksRemoved` →
`G.Graph3DComplete` → `G.ComposeFigure2` → `G.ComposeFigure3`

## How to run

```bash
python 17.ScriptforTestExperiment2.py
```

## Note on the dataset

The pipeline uses the training split of the OhioT1DM dataset only (files named
`{id}-ws-training.xml`). The test split is not used at any stage. The dataset
itself is not redistributed here; it is freely available for scientific
purposes from its custodians.

## Requirements

Python 3.9.12, conda, Windows. Versions are pinned in `requirements.txt`:
numpy 2.0.2, pandas 2.2.2, scipy 1.13.1, matplotlib 3.9.2, seaborn 0.13.2,
pillow 9.0.1. This is the same specification as the Paper 1 pipeline, so both
repositories run under one environment.

```bash
conda create -n pbt python=3.9.12
conda activate pbt
pip install -r requirements.txt
```

## License

MIT