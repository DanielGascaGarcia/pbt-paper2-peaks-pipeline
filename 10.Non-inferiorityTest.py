# Code: 10.Non-inferiorityTest.py
# Description: Non-inferiority test between the meal-based and peak-based
#              branches, plus the descriptive comparison of the two
#              distributions (Figure 5).
# Created 14th November 2023
# Author: mbaxdg6

# NOTE ON STATUS
# --------------
# The non-inferiority framing reported in the published article has been
# superseded. It is retained here so that the analysis behind the published
# Table 2 remains documented, and because the corrected pipeline no longer
# yields the published values. The replacement analysis is an agreement
# analysis at participant level; see the correction notice.
#
# Figure 5 is unaffected: it is a descriptive comparison of the two
# distributions, not part of the test.
#
# KNOWN LIMITATIONS OF THIS TEST
# ------------------------------
# These are properties of the published design, not implementation faults.
# They are the reason the framing was superseded, and they are declared
# rather than corrected:
#
#   1. The test is unpaired, but the two branches are the same participant
#      over the same days. Missing values are dropped per branch, so
#      n_meal != n_peak by construction.
#   2. Observations are pooled across all hours and all days, so the degrees
#      of freedom treat every hourly value as independent.
#   3. The margin is derived from the data: it is 20% of that participant's
#      own meal-branch mean, so the threshold differs between participants.
#   4. One test is run per participant with no adjustment for multiplicity.

import os
import pandas as pd
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from scipy.stats import t as t_dist
import globals

matplotlib.rcParams.update({'font.size': 18})


# -----------------------------------------------------------#
#                    Global configuration
# -----------------------------------------------------------#

id = globals.id
path2 = globals.path2
path3 = globals.path3
path4 = globals.path4

os.makedirs(path3, exist_ok=True)
os.makedirs(path4, exist_ok=True)

fileToRead1 = "Boxplot" + str(id)
fileToRead2 = "BoxplotPeak" + str(id)
fileToSave = "ComparisonPeakNoPeak" + str(id)


# -----------------------------------------------------------#
#                    Unit conversion
# -----------------------------------------------------------#

# Source values are in mg/dL.
# Factor lives in globals.py so every script shares one value.

MGDL_TO_MMOL = globals.MGDL_TO_MMOL


# -----------------------------------------------------------#
#               Non-inferiority margin
# -----------------------------------------------------------#

# Published margin: 20% relative to the reference (meal-based) mean.
#
# Lower BG relative change is considered better.
#
# Therefore:
#
# H0: mean_peak >= mean_meal * (1 + margin)
# H1: mean_peak <  mean_meal * (1 + margin)
#
# Rejecting H0 supports non-inferiority.

MARGIN = 0.20


# -----------------------------------------------------------#
#             Non-inferiority test function
# -----------------------------------------------------------#

def non_inferiority_ttest(
    mean_ref,
    sd_ref,
    n_ref,
    mean_new,
    sd_new,
    n_new,
    relative_difference
):
    """
    One-sided Welch-type non-inferiority test from summary statistics.

    Lower values are assumed to be better.

    Parameters
    ----------
    mean_ref : float
        Mean of the reference (meal-based) method.

    sd_ref : float
        Standard deviation of the reference method.

    n_ref : int
        Number of observations in the reference method.

    mean_new : float
        Mean of the new (peak-based / without-meal-data) method.

    sd_new : float
        Standard deviation of the new method.

    n_new : int
        Number of observations in the new method.

    relative_difference : float
        Relative non-inferiority margin.
        Example: 0.20 means the new method may be up to
        20% worse than the reference mean.

    Hypotheses
    ----------
    H0:
        mean_new >= mean_ref * (1 + relative_difference)

    H1:
        mean_new < mean_ref * (1 + relative_difference)

    Returns
    -------
    tstat : float
        Test statistic. Positive values favour non-inferiority.

    df : float
        Welch-Satterthwaite degrees of freedom.

    pvalue : float
        Correct one-sided p-value.

    threshold : float
        Maximum acceptable mean for the new method.

    Notes
    -----
    Two things in this function are easy to get wrong and both are
    anti-conservative, so neither fails loudly:

    1. The p-value is taken directly from the upper tail of the t
       distribution at the SIGNED statistic. It must never be obtained by
       halving a two-sided p-value: halving discards the sign, so a result
       far on the wrong side of the threshold would be reported as strong
       evidence of non-inferiority.

    2. The variance of the reference term is scaled by
       (1 + relative_difference) ** 2, because the margin is a fraction of
       the estimated reference mean. See the comment at the standard-error
       block.

    The Welch-Satterthwaite degrees of freedom are computed from the same
    scaled variance components, so they inherit point 2 automatically.
    """

    # -------------------------------------------------------#
    # Non-inferiority threshold
    # -------------------------------------------------------#

    delta = relative_difference * mean_ref
    threshold = mean_ref + delta

    # -------------------------------------------------------#
    # Standard error
    #
    # The contrast being tested is not a plain difference of means. It is
    #
    #     D = (1 + margin) * mean_ref - mean_new
    #
    # Because the margin is expressed as a fraction of the ESTIMATED
    # reference mean, that term enters the contrast multiplied by
    # (1 + margin), and its variance therefore enters multiplied by the
    # SQUARE of that factor. Omitting the square understates the standard
    # error and inflates the statistic, which is anti-conservative for a
    # non-inferiority claim.
    #
    # If the margin were ever redefined as an absolute quantity in mg/dL,
    # this scale factor would become 1 and the plain difference-of-means
    # standard error would be correct.
    # -------------------------------------------------------#

    scale = (1.0 + relative_difference) ** 2

    var_ref = scale * (sd_ref ** 2) / n_ref
    var_new = (sd_new ** 2) / n_new

    se = np.sqrt(var_ref + var_new)

    if se == 0:
        raise ValueError(
            "Standard error is zero; the non-inferiority test "
            "cannot be calculated."
        )

    # -------------------------------------------------------#
    # Test statistic
    #
    # Positive t means the observed new-method mean is below
    # the non-inferiority threshold.
    # -------------------------------------------------------#

    tstat = (threshold - mean_new) / se

    # -------------------------------------------------------#
    # Welch-Satterthwaite degrees of freedom
    # -------------------------------------------------------#

    numerator = (var_ref + var_new) ** 2

    denominator = (
        (var_ref ** 2) / (n_ref - 1)
        +
        (var_new ** 2) / (n_new - 1)
    )

    df = numerator / denominator

    # -------------------------------------------------------#
    # Correct one-sided p-value
    #
    # H1 is in the positive-t direction:
    # threshold > mean_new
    #
    # sf = survival function = 1 - CDF
    # -------------------------------------------------------#

    pvalue = t_dist.sf(tstat, df)

    return tstat, df, pvalue, threshold


# -----------------------------------------------------------#
#                  Read input files
# -----------------------------------------------------------#

# Total_group1 / Total_group2 accumulate ABSOLUTE deviations,
# which is the quantity described by the published analysis.
#
# The hourly loop below is a console-only diagnostic: it is printed while
# the script runs and is never written to disk. The only file this script
# produces is Table2_NonInferiority.csv, built from the participant-level
# Total comparison.

Total_group1 = []
Total_group2 = []

data1 = pd.read_csv(
    str(path2)
    + str(fileToRead1)
    + str(0)
    + str("-")
    + str(24)
    + "total.csv"
)

data2 = pd.read_csv(
    str(path2)
    + str(fileToRead2)
    + str(0)
    + str("-")
    + str(24)
    + "total.csv"
)


# -----------------------------------------------------------#
#                    Hourly diagnostic
# -----------------------------------------------------------#

# DIAGNOSTIC ONLY, printed to the console and not saved. These 24 tests per
# participant are not part of the record, were never reported, and carry no
# adjustment for multiplicity. Nothing here is exported, so there is no file
# that could be mistaken for a result.

for i in range(24):

    group1 = data1["[" + str(i) + "-" + str(i + 1) + "]"].to_numpy()
    group2 = data2["[" + str(i) + "-" + str(i + 1) + "]"].to_numpy()

    group1 = group1[~np.isnan(group1)]
    group2 = group2[~np.isnan(group2)]

    # Accumulate absolute deviations for historical Total analysis
    for value in group1:
        Total_group1.append(abs(value))

    for value in group2:
        Total_group2.append(abs(value))

    label = "[" + str(i) + "-" + str(i + 1) + "]"

    if len(group1) > 1 and len(group2) > 1:

        # Use absolute values for consistency with the stated quantity.
        abs_group1 = np.abs(group1)
        abs_group2 = np.abs(group2)

        mean_group1 = np.mean(abs_group1)
        mean_group2 = np.mean(abs_group2)

        stddev_group1 = np.std(abs_group1, ddof=1)
        stddev_group2 = np.std(abs_group2, ddof=1)

        tstat_h, df_h, pval_h, threshold_h = non_inferiority_ttest(
            mean_ref=mean_group1,
            sd_ref=stddev_group1,
            n_ref=len(abs_group1),
            mean_new=mean_group2,
            sd_new=stddev_group2,
            n_new=len(abs_group2),
            relative_difference=MARGIN
        )

        print(
            "One-sided NI test {}: "
            "t = {:.4f}, df = {:.2f}, p = {:.5f}, "
            "threshold = {:.5f}".format(
                label,
                tstat_h,
                df_h,
                pval_h,
                threshold_h
            )
        )

    else:

        print(
            "One-sided NI test {}: "
            "t = N/A, df = N/A, p = N/A".format(label)
        )


# -----------------------------------------------------------#
#        Total historical participant-level comparison
# -----------------------------------------------------------#

mean_total_group1 = np.mean(Total_group1)
mean_total_group2 = np.mean(Total_group2)

stddev_total_group1 = np.std(Total_group1, ddof=1)
stddev_total_group2 = np.std(Total_group2, ddof=1)

tstat, df_welch, pval, threshold = non_inferiority_ttest(
    mean_ref=mean_total_group1,
    sd_ref=stddev_total_group1,
    n_ref=len(Total_group1),
    mean_new=mean_total_group2,
    sd_new=stddev_total_group2,
    n_new=len(Total_group2),
    relative_difference=MARGIN
)

# Retained only for reference to the original pooled-df reporting.
# It is not used by any p-value in this script.
df_pooled = len(Total_group1) + len(Total_group2) - 2


# -----------------------------------------------------------#
#                 Formatting function
# -----------------------------------------------------------#

def p_to_str(p):
    """JMIR-style compact p-value, bounded at both ends."""

    if p < 0.001:
        return "P<.001"

    if p > 0.99:
        return "P>.99"

    return f"P={p:.3f}".lstrip("0").replace("P=0.", "P=.").replace("=0.", "=.")


# -----------------------------------------------------------#
#                       Console output
# -----------------------------------------------------------#

print()
print("--------------------------------------------------")
print("Historical non-inferiority analysis")
print("--------------------------------------------------")

print("Participant ID:", id)

print(
    "Mean, meal branch: {:.5f}".format(
        mean_total_group1
    )
)

print(
    "Mean, peak branch: {:.5f}".format(
        mean_total_group2
    )
)

print(
    "20% non-inferiority threshold: {:.5f}".format(
        threshold
    )
)

print(
    "One-sided Welch NI test:"
)

print(
    "t({:.2f}) = {:.5f}, {}".format(
        df_welch,
        tstat,
        p_to_str(pval)
    )
)

print(
    "Non-inferiority criterion met:",
    pval < 0.05
)

print("--------------------------------------------------")
print()


# -----------------------------------------------------------#
#                         Export
# -----------------------------------------------------------#

# Historical Table 2: one row per participant.
#
# The table is REBUILT on the first participant of the run and appended to
# thereafter. Without this, a partial or reordered run would silently keep
# rows written by an earlier version of the code, and nothing in the file
# would reveal that its rows came from different runs.

row = pd.DataFrame({
    'ID': [id],
    'n_meal': [len(Total_group1)],
    'n_peak': [len(Total_group2)],

    'mean_meal_mgdL': [mean_total_group1],
    'mean_peak_mgdL': [mean_total_group2],

    'sd_meal_mgdL': [stddev_total_group1],
    'sd_peak_mgdL': [stddev_total_group2],

    'margin': [MARGIN],
    'NI_threshold_mgdL': [threshold],

    't': [tstat],
    'df_welch': [df_welch],
    'df_pooled': [df_pooled],

    'p_onesided': [pval],

    'meets_criterion': [
        int(pval < 0.05)
    ]
})

out_table = path4 + "Table2_NonInferiority.csv"

# First participant of the configured run order. Falls back to the current
# participant if globals does not expose a list, in which case the table is
# rebuilt on every run.
try:
    first_id = list(globals.ids)[0]
except (AttributeError, IndexError, TypeError):
    first_id = id

rebuild = (id == first_id)

if os.path.isfile(out_table) and not rebuild:

    table = pd.read_csv(out_table)

    table = table[
        table['ID'] != id
    ]

    table = pd.concat(
        [table, row],
        ignore_index=True
    )

else:

    if os.path.isfile(out_table):
        print(
            "First participant of the run: "
            "rebuilding", os.path.basename(out_table),
            "from scratch."
        )

    table = row


table = (
    table
    .sort_values('ID')
    .reset_index(drop=True)
)

table.to_csv(
    out_table,
    index=False
)

print(
    "Saved:",
    os.path.abspath(out_table)
)


# -----------------------------------------------------------#
#        Figure 5 — descriptive comparison only
# -----------------------------------------------------------#

# Figure 5 is not part of the inferential test.
# It simply describes the two distributions.

data = [
    Total_group1,
    Total_group2
]

fig, ax = plt.subplots(
    figsize=(8, 6)
)

boxplot = ax.boxplot(
    data,
    patch_artist=True,
    showmeans=True
)


# -----------------------------------------------------------#
#                   Box appearance
# -----------------------------------------------------------#

colors = [
    '#87CEEB',
    '#FFCCCB'
]

for patch, color in zip(
    boxplot['boxes'],
    colors
):
    patch.set_facecolor(color)
    patch.set_edgecolor('black')


# -----------------------------------------------------------#
#                    Whiskers / caps
# -----------------------------------------------------------#

for whisker in boxplot['whiskers']:

    whisker.set(
        color='black',
        linewidth=1.5,
        linestyle='--'
    )


for cap in boxplot['caps']:

    cap.set(
        color='black',
        linewidth=1.5
    )


# -----------------------------------------------------------#
#                         Medians
# -----------------------------------------------------------#

for median in boxplot['medians']:

    median.set(
        color='red',
        linewidth=2
    )


# -----------------------------------------------------------#
#                           Means
# -----------------------------------------------------------#

for mean in boxplot['means']:

    mean.set(
        marker='o',
        markerfacecolor='black',
        markeredgecolor='black',
        markersize=7
    )


# -----------------------------------------------------------#
#                         Labels
# -----------------------------------------------------------#

plt.xticks(
    [1, 2],
    [
        'With meal data',
        'Without meal data'
    ],
    fontsize=12
)

plt.xlabel(
    'Comparison of approaches with versus without meal data',
    fontsize=14
)

plt.ylabel(
    'BG relative change (mg/dL)',
    fontsize=14
)

if globals.FIGURE_TITLES:

    plt.title(
        f'Cumulative deviation of blood glucose: {id}',
        fontsize=16
    )


# -----------------------------------------------------------#
#                           Grid
# -----------------------------------------------------------#

plt.grid(
    color='gray',
    linestyle='--',
    linewidth=0.5,
    alpha=0.7
)


# -----------------------------------------------------------#
#                   Secondary mmol/L axis
# -----------------------------------------------------------#

def mg_dL_to_mmol(y):

    return y * MGDL_TO_MMOL


def mmol_to_mg_dL(y):

    return y / MGDL_TO_MMOL


secax = ax.secondary_yaxis(
    'right',
    functions=(
        mg_dL_to_mmol,
        mmol_to_mg_dL
    )
)

secax.set_ylabel(
    'BG relative change (mmol/L)',
    fontsize=14
)

secax.yaxis.set_major_formatter(
    plt.FuncFormatter(
        lambda x, _: f'{x:.1f}'
    )
)


# -----------------------------------------------------------#
#                       Minor ticks
# -----------------------------------------------------------#

ax.yaxis.set_minor_locator(
    plt.MultipleLocator(5)
)

ax.tick_params(
    axis='both',
    which='major',
    labelsize=12
)

plt.tight_layout()


# -----------------------------------------------------------#
#                         Save figure
# -----------------------------------------------------------#

# Only the worked example used in the article is written.

if id == globals.idG:

    out = (
        path3
        + 'Figure5.png'
    )

    plt.savefig(
        out,
        dpi=300,
        bbox_inches='tight'
    )

    print(
        "Saved:",
        os.path.abspath(out)
    )


plt.close(fig)
