# Release notes — PBT, Paper 2 Peaks Pipeline

DOI (this version): assigned on publication.
Concept DOI, always resolving to the latest version: **10.5281/zenodo.17393514**

This release updates the analysis code following a reproducibility exercise.
The values in the current version of the article (*JMIR Diabetes*
2025;10:e72769) are produced by this version.

## Changes that affect reported values

- `4.PeaksDetection.py` resets the meal-annotation table for each day and
  counts the days without meal annotation directly (Table 3 and the excluded
  participants 540, 552 and 567).
- `9.Boxplot.py` and `9.BoxplotPeak.py` take their row count from the per-hour
  files they read, so every available day enters the hourly summaries.
- Exclusion windows that pass midnight are applied to the next calendar day
  only, and the meal branch processes the last day of each record in full.

## Statistical treatment

- The two branches are compared at participant level with a Bland-Altman
  analysis (`G.BlandAltman.py`). Figure 5 is drawn by `10.ComparisonFigure.py`.
- Intervals are *t* intervals on participant-level values; pooled fractions are
  reported as counts.
- Exclusion criterion: more than 20% of days without meal annotation
  (`globals.MISSING_THRESHOLD`).

## Additional analyses, not reported in the article

Sensitivity rows of the agreement analysis, descriptive statistics of its data,
a distributional comparison (Jensen-Shannon and Kullback-Leibler divergence),
the hourly profiles of both branches for all 12 participants, and the
sensitivity to the interpolation point (`sensitivity/`). See the README.

## Reproducibility

The orchestrator clears `processed/` before every run and stops if any step
fails or any participant is missing an output. Two runs from a clean state
give identical results: the eighteen tables in `results/tables/` are identical
byte for byte. A demo mode runs the pipeline on synthetic data.

## License

MIT
