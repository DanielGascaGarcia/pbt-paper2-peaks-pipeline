#Code: G.Divergence.py
#Description: How different are the two branches' hourly profiles as
#             distributions? Jensen-Shannon divergence (JS), with
#             Kullback-Leibler (KL) in both directions. The method suggested
#             by the examiners; supporting analysis.
#
#             Step by step:
#               1. For each participant and branch, the 24 hourly medians
#                  (the same values used by G.BlandAltman.py), over the hours
#                  with data in both branches.
#               2. Each profile becomes a histogram with the SAME 8 bins for
#                  everyone: the range is the 1st to 99th percentile of all
#                  profiles pooled. 0.5 is added to every bin so no bin is
#                  empty (KL is undefined with an empty bin).
#               3. JS and KL between the two histograms of each participant.
#                  JS runs from 0 (identical) to 1 (no overlap) and is
#                  symmetric; KL is not, so both directions are given.
#               4. A scale for reading JS (the anchor): the same JS between
#                  every pair of DIFFERENT participants measured with the SAME
#                  method. It says how different two people are when the
#                  method is held fixed. The between-method value of step 3 is
#                  read against it.
#
#Inputs:  processed/Boxplot<id>0-24total.csv, processed/BoxplotPeak<id>0-24total.csv
#         results/tables/Table3.csv  (participants analysed: Quality = 0)
#Outputs: results/tables/Divergence_byID.csv
#         results/tables/Divergence_anchor.csv
#         results/tables/Divergence_summary.csv
#Author: mbaxdg6

import os

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from scipy.stats import entropy

import globals
from pbt_io import included_ids, read_branch

IDS = included_ids(globals.path4)
BINS = 8
SMOOTH = 0.5

# Step 1: hourly medians per participant and branch
meal, peak = {}, {}
for pid in IDS:
    meal[pid] = read_branch(os.path.join(globals.path2, f"Boxplot{pid}0-24total.csv")).median(axis=0, skipna=True)
    peak[pid] = read_branch(os.path.join(globals.path2, f"BoxplotPeak{pid}0-24total.csv")).median(axis=0, skipna=True)

# Step 2: common bins for everyone
pooled = np.concatenate([s.dropna().values for s in list(meal.values()) + list(peak.values())])
low, high = np.percentile(pooled, [1, 99])
edges = np.linspace(low, high, BINS + 1)


def histogram(values):
    counts = np.histogram(np.clip(values, low, high), bins=edges)[0] + SMOOTH
    return counts / counts.sum()


# Step 3: JS and KL per participant
rows = []
for pid in IDS:
    both = meal[pid].notna() & peak[pid].notna()
    p = histogram(meal[pid][both].values)
    q = histogram(peak[pid][both].values)
    rows.append({
        "ID": pid,
        "Hours": int(both.sum()),
        "JS": jensenshannon(p, q, base=2) ** 2,
        "KL_meal_peak": entropy(p, q, base=2),
        "KL_peak_meal": entropy(q, p, base=2),
    })

D = pd.DataFrame(rows)
print(f"Common range {low:.1f} to {high:.1f} mg/dL, {BINS} bins, +{SMOOTH} per bin\n")
print(D.round(3).to_string(index=False))
print(f"\nJS mean {D.JS.mean():.3f}   median {D.JS.median():.3f}")

D.round(4).to_csv(os.path.join(globals.path4, "Divergence_byID.csv"), index=False)

# Descriptives of the three derived variables (mean, SD, median, IQR, range)
rows_s = []
for col in ("JS", "KL_meal_peak", "KL_peak_meal"):
    x = D[col].values
    q1, q3 = np.percentile(x, [25, 75])
    rows_s.append({"variable": col, "n": len(x), "mean": x.mean(),
                   "sd": x.std(ddof=1), "median": np.median(x), "q1": q1,
                   "q3": q3, "min": x.min(), "max": x.max()})
pd.DataFrame(rows_s).round(4).to_csv(
    os.path.join(globals.path4, "Divergence_summary.csv"), index=False)

# Step 4: anchor - JS between every pair of different participants, same method
# (each participant's full profile, with the same bins and smoothing)
anchor = {"meal-based": [], "peak-based": []}
for a_i, a in enumerate(IDS):
    for b in IDS[a_i + 1:]:
        for label, prof in (("meal-based", meal), ("peak-based", peak)):
            p = histogram(prof[a].dropna().values)
            q = histogram(prof[b].dropna().values)
            anchor[label].append(jensenshannon(p, q, base=2) ** 2)

A = pd.DataFrame([
    {"comparison": "between methods, same participant", "pairs": len(D),
     "median_JS": D.JS.median()},
    {"comparison": "between participants, meal-based method", "pairs": len(anchor["meal-based"]),
     "median_JS": float(np.median(anchor["meal-based"]))},
    {"comparison": "between participants, peak-based method", "pairs": len(anchor["peak-based"]),
     "median_JS": float(np.median(anchor["peak-based"]))},
])
print("\nScale (median JS)")
print(A.round(3).to_string(index=False))
A.round(4).to_csv(os.path.join(globals.path4, "Divergence_anchor.csv"), index=False)
