"""
G.CGMCoverage.py
CGM coverage per participant and per day, before any meal-related exclusion.

Author: mbaxdg6 (Daniel Gasca Garcia)

What it does
    For every participant in globals.ids and every daily CGM working copy,
    counts the readings present and expresses them as a percentage of a
    complete day (288 readings, one every 5 minutes). Describes missing
    data points and gives descriptive statistics of
    the data used.

Inputs
    globals.ids (all twelve in paper 2), globals.path2, globals.path4
    <path2>/glucose_level<id>-ws-training_wCN <Weekday>-<YYYY-MM-DD> .csv
    (daily working copies written by 4.MealBolusDetection.py; column BGValue2
    keeps every reading from before the meal-related exclusion)

Outputs
    <path4>/CGMCoverage_summary.csv one row: cohort mean (SD) of days and of
                                    mean coverage, and mean % of days >= 70%
    <path4>/CGMCoverage_byID.csv    days, mean/median/min/max coverage, and
                                    days at or above 70% coverage, per ID
    <path4>/CGMCoverage_byDay.csv   readings and coverage for every day file

Notes
    - Only days that have a CGM file are counted; a day with no readings at
      all has no file and does not appear.
    - The "_wCN " prefix (with the space) excludes the whole-period
      glucose_level<id>-ws-training_wCN.csv written by 1.ColumnNamer.py.
"""

import os
import glob
import numpy as np
import pandas as pd
import globals

path2 = globals.path2
path4 = globals.path4
os.makedirs(path4, exist_ok=True)

# A CGM samples every 5 minutes, so a complete day (1,440 minutes)
# carries 288 readings. Coverage is expressed against that.
READINGS_PER_DAY = 288

rows = []
per_day_rows = []

for pid in globals.ids:
    prefix = f"glucose_level{pid}-ws-training_wCN "
    files = sorted(glob.glob(os.path.join(path2, prefix + "*.csv")))
    if not files:
        print(f"  {pid}: no _wCN files found")
        continue

    day_cov = []
    for f in files:
        d = pd.read_csv(f)
        # BGValue2 carries the readings before meal-related exclusion, so it
        # measures the sensor, not the algorithm.
        col = 'BGValue2' if 'BGValue2' in d.columns else 'BGValue'
        n = int(d[col].notna().sum())
        cov = 100 * n / READINGS_PER_DAY
        day_cov.append(cov)
        per_day_rows.append({'ID': pid,
                             'file': os.path.basename(f),
                             'readings': n,
                             'coverage_pct': round(cov, 1)})

    day_cov = np.array(day_cov)
    rows.append({
        'ID': pid,
        'days': len(day_cov),
        'mean_coverage_pct': round(day_cov.mean(), 1),
        'median_coverage_pct': round(float(np.median(day_cov)), 1),
        'min_coverage_pct': round(day_cov.min(), 1),
        'max_coverage_pct': round(day_cov.max(), 1),
        'days_above_70pct': int((day_cov >= 70).sum()),
        'pct_days_above_70': round(100 * (day_cov >= 70).mean(), 1),
    })

summary = pd.DataFrame(rows)
summary.to_csv(os.path.join(path4, "CGMCoverage_byID.csv"), index=False)
pd.DataFrame(per_day_rows).to_csv(
    os.path.join(path4, "CGMCoverage_byDay.csv"), index=False)

# Cohort summary, one row: the figures quoted in the thesis appendix, written
# here so that they come from the code rather than being computed by hand.
if len(summary):
    pd.DataFrame([{
        'n': len(summary),
        'days_mean': round(summary.days.mean(), 1),
        'days_sd': round(summary.days.std(ddof=1), 1),
        'days_min': int(summary.days.min()),
        'days_max': int(summary.days.max()),
        'mean_coverage_pct_mean': round(summary.mean_coverage_pct.mean(), 1),
        'mean_coverage_pct_sd': round(summary.mean_coverage_pct.std(ddof=1), 1),
        'pct_days_above_70_mean': round(summary.pct_days_above_70.mean(), 1),
    }]).to_csv(os.path.join(path4, "CGMCoverage_summary.csv"), index=False)

print(summary.to_string(index=False))
print()
if len(summary):
    print(f"Cohort mean coverage : {summary.mean_coverage_pct.mean():.1f}%")
    print(f"Lowest participant   : {summary.mean_coverage_pct.min():.1f}% "
          f"(ID {int(summary.loc[summary.mean_coverage_pct.idxmin(), 'ID'])})")
    print(f"Days at or above 70% : "
          f"{summary.days_above_70pct.sum()} of {summary.days.sum()}")
print()
print("Saved:", os.path.abspath(os.path.join(path4, "CGMCoverage_byID.csv")))
print("Saved:", os.path.abspath(os.path.join(path4, "CGMCoverage_byDay.csv")))
print("Saved:", os.path.abspath(os.path.join(path4, "CGMCoverage_summary.csv")))
