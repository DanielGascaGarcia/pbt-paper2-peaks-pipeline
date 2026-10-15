#Code: G.BlandAltman.py
#Description: Agreement between the meal-based and the peak-based branch
#             (Bland-Altman). Primary comparison of the two branches.
#
#             Step by step:
#               1. For each participant and branch, the median of each hour
#                  across days (24 values: the algorithm's output).
#               2. One number per participant and branch: the mean of the
#                  absolute hourly medians, over the hours that have data in
#                  BOTH branches (588: 22 of 24 hours).
#               3. Difference = peak-based - meal-based, one per participant.
#               4. Bias (mean difference), its 95% CI, and the limits of
#                  agreement (bias +/- 1.96 SD).
#               5. Assumption checks: normality of the differences
#                  (Shapiro-Wilk) and no proportional trend (correlation of
#                  the difference with the mean of the two branches).
#
#             Four rows in the summary table:
#               absolute (primary)   steps 1-4 as above, analysed set (n = 9)
#               signed               step 2 WITHOUT the absolute value: shows
#                                    whether one branch reads systematically
#                                    above the other
#               absolute, all cells  step 2 over every day and hour instead of
#                                    the hourly medians: sensitivity to the
#                                    level of aggregation
#               absolute, all 12     the primary analysis without the exclusion
#                                    criterion: sensitivity to the participant
#                                    set
#               signed, all 12       the signed row without the exclusion
#                                    criterion
#
#Inputs:  processed/Boxplot<id>0-24total.csv, processed/BoxplotPeak<id>0-24total.csv
#         results/tables/Table3.csv  (participants analysed: Quality = 0)
#Outputs: results/tables/BlandAltman_byID.csv
#         results/tables/BlandAltman_summary.csv
#Author: mbaxdg6 (Daniel Gasca Garcia)
import os

import numpy as np
import pandas as pd
from scipy import stats

import globals
from pbt_io import ALL_IDS, included_ids, read_branch

IDS = included_ids(globals.path4)

# ------------------------------------------------------------------
# Steps 1-3: one row per participant
# ------------------------------------------------------------------
rows = []
for pid in ALL_IDS:
    meal = read_branch(os.path.join(globals.path2, f"Boxplot{pid}0-24total.csv"))
    peak = read_branch(os.path.join(globals.path2, f"BoxplotPeak{pid}0-24total.csv"))

    meal_hourly = meal.median(axis=0, skipna=True)      # 24 values
    peak_hourly = peak.median(axis=0, skipna=True)
    both = meal_hourly.notna() & peak_hourly.notna()    # hours in both branches

    rows.append({
        "ID": pid,
        "Hours": int(both.sum()),
        "MealBased": meal_hourly[both].abs().mean(),
        "PeakBased": peak_hourly[both].abs().mean(),
        "MealSigned": meal_hourly[both].mean(),
        "PeakSigned": peak_hourly[both].mean(),
        # every day and hour, not the hourly medians (sensitivity)
        "MealCells": meal.loc[:, both].abs().stack().mean(),
        "PeakCells": peak.loc[:, both].abs().stack().mean(),
        "Analysed": pid in IDS,
    })

T = pd.DataFrame(rows)
T["Difference"] = T.PeakBased - T.MealBased
T["DifferenceSigned"] = T.PeakSigned - T.MealSigned
T["DifferenceCells"] = T.PeakCells - T.MealCells
T["Mean"] = (T.PeakBased + T.MealBased) / 2
T["MeanCells"] = (T.PeakCells + T.MealCells) / 2
A = T[T.Analysed]                       # the analysed set (n = 9)

# ------------------------------------------------------------------
# Step 4: Bland-Altman
# ------------------------------------------------------------------
def bland_altman(d, mean, label):
    n = len(d)
    bias = d.mean()
    sd = d.std(ddof=1)
    t = stats.t.ppf(0.975, n - 1)
    return {
        "analysis": label,
        "n": n,
        "bias": bias,
        "sd": sd,
        "bias_ci_low": bias - t * sd / np.sqrt(n),
        "bias_ci_high": bias + t * sd / np.sqrt(n),
        "loa_low": bias - 1.96 * sd,
        "loa_high": bias + 1.96 * sd,
        # upper end of the 95% CI of the upper limit of agreement
        # (Bland & Altman 1986): how far that limit could plausibly reach
        "loa_high_ci_high": bias + 1.96 * sd
                            + t * sd * np.sqrt(1 / n + 1.96 ** 2 / (2 * (n - 1))),
        "shapiro_p": stats.shapiro(d).pvalue,
        "wilcoxon_p": stats.wilcoxon(d).pvalue,
        # Assumption check: does the difference grow or shrink with the size
        # of the measurement? Only meaningful for the absolute summaries; for
        # the signed ones the mean of the two branches is a near-cancellation.
        "magnitude": mean.mean() if mean is not None else np.nan,
        "trend_r": stats.pearsonr(mean, d)[0] if mean is not None else np.nan,
        "trend_p": stats.pearsonr(mean, d)[1] if mean is not None else np.nan,
    }

summary = pd.DataFrame([
    bland_altman(A.Difference, A.Mean, "absolute (primary)"),
    bland_altman(A.DifferenceSigned, None, "signed"),
    bland_altman(A.DifferenceCells, A.MeanCells, "absolute, all cells"),
    bland_altman(T.Difference, T.Mean, "absolute, all 12 participants"),
    bland_altman(T.DifferenceSigned, None, "signed, all 12 participants"),
])

print("Per participant (mg/dL)")
print(T.round(2).to_string(index=False))
print("\nBland-Altman (difference = peak-based - meal-based, mg/dL)")
print(summary.round(3).to_string(index=False))

T.round(4).to_csv(os.path.join(globals.path4, "BlandAltman_byID.csv"), index=False)
summary.to_csv(os.path.join(globals.path4, "BlandAltman_summary.csv"), index=False)
