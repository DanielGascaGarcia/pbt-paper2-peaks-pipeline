DOI: https://doi.org/YOUR-DOI-HERE

## What’s included
- End-to-end **peaks** pipeline for CGM (Paper 2): LPF smoothing, prominence/width discrimination (95th pct), next-day merge, hourly split, relative change, and 24-h boxplots.
- Scripts: 0–12 in the order listed below. Outputs include filtered BG day files, hourly stacks, relative changes, per-hour “last values”, a 24-h boxplot table, 24-h medians with reliability flag, and a final plot of median relative change.

## Dependency
This release optionally uses a Paper 1 artifact with the same `id` **only for `10.Non-inferiorityTest.py`**:
- `Boxplot{id}0-24total.csv`
If it’s not found under `globals.path2`, the runner skips that step and proceeds.
Paper 1 (Zenodo): https://doi.org/10.5281/zenodo.17392921

## Execution order
globals.py → 0.Parser → 1.ColumnNamer → 2.Disaggregator → 3.PivotGeneratorBG →
4.PeaksDetection → 5.MergePeaksNextDay → 6.MergePeaks → 7.SplitHoursPeaks →
8.RelativeChangePeaks → 9.BoxplotPeak → 10.Non-inferiorityTest →
10.PivotGeneratormediansPeak → 12.MergeRChBasalPeakNoAct

## How to run
```bash
python 17.ScriptforTestExperiment2.py
```

## Requirements
Python ≥ 3.10 · pandas · numpy · scipy · matplotlib · seaborn

## License
MIT
