#Code: G.BADescriptives.py
#Description: Descriptive statistics for the data entering the Bland-Altman
#             analysis, at the level at which it is analysed. Answers the
#             examiners' request to see the descriptive statistics associated
#             with the data being analysed, for this analysis specifically.
#
#             Two blocks:
#               (1) per participant - each branch summary, their mean and
#                   difference, and the hours contributing;
#               (2) cohort - n, mean, SD, median, Q1-Q3 and range for each of
#                   those columns.
#
#             Aggregation, unchanged from the reported analysis:
#               days -> median per hour of day   (the quantity the algorithm
#                                                 produces; robust to outliers)
#               24 hours -> mean of |median|     (one value per participant;
#                                                 removes pseudo-replication)
#
#             The reader is the shared one in pbt_io, the by-name selector,
#             which fails loudly on a reordered or augmented file.
#Author: mbaxdg6

import os

import numpy as np
import pandas as pd

from pbt_io import ALL_IDS, HOURS, included_ids, read_branch

try:
    import globals
    PATH_IN, PATH_OUT = globals.path2, globals.path4
except ImportError:                      # standalone use
    PATH_IN = PATH_OUT = "./"

# The nine participants of the reported analysis (Quality = 0), read from
# Table3.csv so this table and the analysis never drift apart.
IDS = included_ids(PATH_OUT)


def participant_row(pid):
    """One row: both branch summaries over the hours present in BOTH branches."""
    meal = read_branch(os.path.join(PATH_IN, f"Boxplot{pid}0-24total.csv"))
    peak = read_branch(os.path.join(PATH_IN, f"BoxplotPeak{pid}0-24total.csv"))
    m, p = meal.median(axis=0, skipna=True), peak.median(axis=0, skipna=True)
    ok = m.notna() & p.notna()
    return {
        "ID": pid,
        "Days_meal": int(meal.shape[0]),
        "Days_peak": int(peak.shape[0]),
        "Hours": int(ok.sum()),
        "MealBased": m[ok].abs().mean(),
        "PeakBased": p[ok].abs().mean(),
        "Mean": (m[ok].abs().mean() + p[ok].abs().mean()) / 2,
        "Difference": p[ok].abs().mean() - m[ok].abs().mean(),
        "DifferenceSigned": p[ok].mean() - m[ok].mean(),
    }


def describe(series):
    """The six descriptors reported for every column, in one place."""
    q1, q3 = np.percentile(series, [25, 75])
    return {
        "n": len(series),
        "Mean": series.mean(),
        "SD": series.std(ddof=1),
        "Median": float(np.median(series)),
        "Q1-Q3": f"{q1:.2f} to {q3:.2f}",
        "Range": f"{series.min():.2f} to {series.max():.2f}",
    }


ALL = pd.DataFrame([participant_row(pid) for pid in ALL_IDS]).set_index("ID")
D = ALL.loc[IDS].drop(columns="DifferenceSigned")

print("\n=== PER PARTICIPANT (mg/dL, mean of the |hourly medians|) ===")
print(D.round(2).to_string())

for pid, h in D.Hours.items():
    if h != 24:
        print(f"  note: {pid} contributes {h} of 24 hours "
              f"(hours absent in one branch are dropped from both)")

print("\n=== COHORT ===")
C = pd.DataFrame({c: describe(D[c].values)
                  for c in ["Days_meal", "Days_peak", "Hours",
                            "MealBased", "PeakBased", "Mean", "Difference"]}).T
C[["Mean", "SD", "Median"]] = C[["Mean", "SD", "Median"]].astype(float).round(2)
print(C.to_string())

os.makedirs(PATH_OUT, exist_ok=True)
D.round(3).to_csv(os.path.join(PATH_OUT, "BA_descriptives_byID.csv"))
C.to_csv(os.path.join(PATH_OUT, "BA_descriptives_cohort.csv"))
# Sensitivity rows use a different set or a different quantity from the
# primary analysis, so their data are described separately.
S = pd.DataFrame({
    "Difference in absolute-magnitude summaries, n=12": describe(ALL["Difference"].values),
    "Difference in signed summaries, n=9": describe(ALL.loc[IDS, "DifferenceSigned"].values),
    "Difference in signed summaries, n=12": describe(ALL["DifferenceSigned"].values),
}).T
S[["Mean", "SD", "Median"]] = S[["Mean", "SD", "Median"]].astype(float).round(2)
print("\n=== SENSITIVITY ===")
print(S.to_string())
S.to_csv(os.path.join(PATH_OUT, "BA_descriptives_sensitivity.csv"))

print("\nSaved:", os.path.abspath(os.path.join(PATH_OUT,
                                               "BA_descriptives_byID.csv")))
print("Saved:", os.path.abspath(os.path.join(PATH_OUT,
                                             "BA_descriptives_sensitivity.csv")))
print("Saved:", os.path.abspath(os.path.join(PATH_OUT,
                                             "BA_descriptives_cohort.csv")))
