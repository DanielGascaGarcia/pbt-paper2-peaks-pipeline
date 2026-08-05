#Code: G.CGMCoverage.py
#Description: CGM coverage per participant, from the per-day files written by
#             the parsing stage. Reports the proportion of the day for which a
#             sensor reading is present, before any meal- or peak-related
#             exclusion.
#
#             Answers the reviewers' observation about missing datapoints, and
#             provides the descriptive statistics requested for the data used.
#Author: mbaxdg6

import os
import glob
import numpy as np
import pandas as pd
import globals

path2 = globals.path2
path4 = globals.path4
os.makedirs(path4, exist_ok=True)

# The per-minute pivot has 1440 rows per day; CGM samples every 5 minutes, so a
# complete day carries 288 readings. Coverage is expressed against that.
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
