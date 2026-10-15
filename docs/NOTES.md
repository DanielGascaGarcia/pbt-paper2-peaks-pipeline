# Implementation notes — PBT, Paper 2 Peaks Pipeline

Technical notes on how the code works, for readers who want more detail than
the README gives. Nothing here is needed to run the pipeline.

## The two windows

| | Span | Used for |
|---|---|---|
| **Exclusion window** | 1 h before the peak to 3 h after it | removing the glucose excursion from the analysis |
| **Precision window** | 1 h before the estimated base point (peak time minus half the peak width) to 1 h after the peak | deciding whether a detected peak matches a recorded meal |

They serve different purposes and are not interchangeable. The exclusion window
is deliberately wide, so that the postprandial rise and its decay are removed.
The precision window is anchored on the base point rather than the peak,
because the meal precedes the rise, and it is narrower because it is a matching
criterion rather than a removal rule.

## Intermediate files

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

- **`BGValue2`** — the readings before any exclusion. In the meal-branch
  (`_wCN `) files these are the readings as parsed; in the peak-branch
  (`_wCNF `) files they are already on the per-minute grid and interpolated
  (gaps of up to 10 minutes filled), because the peak branch interpolates
  before removing anything.
- **`BGValue`** — the readings that survive exclusion. Blank where the meal
  window or the peak window removed the reading.
- **`ValueCh`** — the readings that were removed. In the peak-branch files it
  is blank for kept readings; in the meal-branch files kept readings carry 0.

`BGValue` feeds the hourly relative change; `ValueCh` is what the "segments
removed" panel of Figure 3 plots.

## Running on a clean state

Several steps read the per-day files present in `processed/`, and the
midnight-overflow step rewrites those files in place, so the orchestrator
clears `processed/` before each run. **Clear it by hand if you run individual
steps**, so that the days entering the analysis are exactly those of the input
data.

## Implementation details

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
unchanged across the nine included participants and does not alter the
included set.

### Midnight-overflow trimming (both branches)

Both branches can exclude minutes past midnight when a window extends beyond
23:59, but they do it by different mechanisms.

In the **meal branch**, `4.MealBolusDetection.py` splits the post-meal window
at midnight and writes directly into the following day's file
(`Matrix[i+1]`), setting `BGValue` to `NaN` for the affected minutes. No mask
is involved; the following day's file is modified in place, the same way the
current day's file is.

In the **peak branch**, when an exclusion window extends past midnight the
detection step writes a 0/1 mark for each CGM reading of the following day, and
`5.MergePeaksNextDay.py` applies it, rewriting that day's file in place.

When the peak-branch mask is applied it is first aligned onto a per-minute
grid and interpolated. Because it carries values only at CGM sample times, the
interpolation assigns fractional values to the minutes in between, and the
threshold used (`> 0`) treats any fractional value as masked. The excluded
window is therefore widened by a few minutes at each boundary. This
interpolation step has no equivalent in the meal branch, since the meal
branch never interpolates a mask — it writes `NaN` directly at the minutes it
identifies.

This is conservative and applied identically to all participants and days,
and it is the behaviour that produces the reported figures. Adaptations of the
peak-branch code may forward-fill the mask instead, or threshold at `>= 0.5`. The marks are joined to the grid on the full
`HH:MM:SS` time, which assumes whole-minute timestamps, as in OhioT1DM.

In both branches the overflow is carried only when the next CGM file is the
next calendar day; after a gap in the record, or on the last day, nothing is
carried.

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
This affects tests of exact equality: a value of exactly zero is far more likely
to arise in the meal branch, so the count of "optimal" hours depends on this
detail.

An additional sensitivity analysis, not reported in the article, uses the two scripts in
`sensitivity/`, which replace their namesakes in a copy of the repository and
make the peak branch interpolate after the split, as the meal branch does. With
them the primary bias is +0.75 mg/dL (95% CI −0.76 to +2.27), the signed offset
stays positive in all 12 participants, and 274 of 288 hourly intervals remain
off target; precision and Table 3 are unchanged.

### Exclusion criterion

Participants are excluded from the precision analysis when **more than 20% of
their days carry no meal annotation** (`globals.MISSING_THRESHOLD`).
`4.PeaksDetection.py` writes `FilesMissing`, `FilesTotal`, `MissingPct` and a
`Quality` flag per participant into `Table3.csv`.

The counts are taken directly from the days without meal annotation of each
participant.

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

### Other details

- **Input handling.** Column names are assigned by the position of each
  element in the XML (`1.ColumnNamer.py`, `2.Disaggregator.py`), following the
  structure of the OhioT1DM files. File names are parsed assuming a three-digit
  participant identifier, as in all twelve.
- **Day order.** The merge steps list the per-day files in file-name order, so
  the day columns of the joined tables, the rows of the box-plot files and the
  "Day number" axis of Figure 3 follow that order rather than the calendar. No
  reported statistic depends on it.
- **Meal-branch reference.** The exclusion window is a fixed 4 hours from each
  recorded meal. The script also classifies each meal as high, medium or low
  glycaemic, from the time to the peak of the low-pass filtered glucose after
  the meal. This classification is reported in the console and is not used by
  later steps: the same 4-hour window is applied to every meal.
- **Environment.** pandas 2.2.2 is required: pandas 3 does not support
  interpolation of a frame with a text column or position-based access by
  integer, both used in the pipeline. Figure rendering can differ slightly
  across systems.
- **Figure annotations.** The "A", "B" and "C" markers and boxes of Figure 6 are
  added afterwards in an image editor and are not reproduced by a run.
