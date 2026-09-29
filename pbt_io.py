#Code: pbt_io.py
#Description: Shared input layer for the paper 2 re-analysis scripts.
#
#             Three things that must be identical across the package live here
#             and nowhere else:
#
#               (1) READ_BRANCH - one reader for the hourly CSVs. Before this
#                   module the package contained four variants (select by name;
#                   drop columns beginning with Unnamed; no filtering at all;
#                   with and without numeric coercion). On the deposited files
#                   all four return identical values - verified 09/08/2026 and
#                   again on 13/08/2026, bias +1.2755, SD 2.0320 in every case -
#                   so this consolidation corrects no reported number. It is
#                   done because the examiners' finding concerned reproducibility,
#                   and a package that reads one file three ways invites the
#                   question of which reading produced the reported figures.
#                   The by-name selector is the variant kept: it is the only one
#                   that fails loudly rather than silently on a reordered or
#                   augmented file.
#
#               (2) LOA_K - the coverage factor for the limits of agreement,
#                   declared once so the package cannot display two values for
#                   one quantity.
#
#               (3) INCLUDED_IDS - the analysed set, read from the quality table
#                   the pipeline writes rather than hard-coded in each script.
#Author: mbaxdg6

import os

import pandas as pd

HOURS = [f"[{h}-{h+1}]" for h in range(24)]

# The twelve participants of the cohort, and the nine of the reported analysis
# (>20% of days without a meal annotation excludes 540, 552, 567). The second
# is a FALLBACK only: prefer included_ids() below, which reads the set the
# pipeline actually produced.
ALL_IDS = [540, 544, 552, 559, 563, 567, 570, 575, 584, 588, 591, 596]
REPORTED_N9 = [544, 559, 563, 570, 575, 584, 588, 591, 596]

# Coverage factor for the Bland-Altman limits of agreement.
#
# The limits estimate the 2.5th and 97.5th PERCENTILES of the population
# distribution of differences - the interval within which 95% of individual
# differences are expected to fall. That is a percentile of a population, not
# the uncertainty of an estimator, so the factor is the normal quantile 1.96
# by definition and does NOT depend on n.
#
# Small-sample uncertainty enters separately, in the CONFIDENCE INTERVAL of
# each limit, which uses t(0.975, n-1). The two are different objects and are
# kept apart wherever they are used.
#
# Substituting t here was tried and reverted: it is neither the conventional
# Bland-Altman limit nor a principled small-sample correction. That would be a
# tolerance-interval factor, which needs both a coverage proportion and a
# confidence level to be stated: for two-sided 95% content at n=9 it is 3.53 at
# 95% confidence (3.13 at 90%), wider than both 1.96 and t = 2.306.
#
# Every script in the package reads the factor from here, including the rough
# outlier screen in G.BADifferences.py, which previously rounded it to 2.
LOA_K = 1.96


def read_branch(path):
    """Days x 24 hourly columns from one branch file.

    Columns are selected BY NAME, so a reordered, augmented or index-carrying
    file raises instead of silently entering the analysis with a 25th column.
    Values are coerced to numeric for the same reason: a stray string becomes
    a missing value rather than turning the column into an object dtype whose
    median is undefined.
    """
    d = pd.read_csv(path)
    d.columns = [c.strip() for c in d.columns]
    missing = [c for c in HOURS if c not in d.columns]
    if missing:
        raise ValueError(f"{os.path.basename(path)}: missing hour columns {missing}")
    return d[HOURS].apply(pd.to_numeric, errors="coerce")


def branch_paths(data_dir, pid):
    """(meal-based, peak-based) file paths for one participant."""
    return (os.path.join(data_dir, f"Boxplot{pid}0-24total.csv"),
            os.path.join(data_dir, f"BoxplotPeak{pid}0-24total.csv"))


def read_pair(data_dir, pid):
    """Both branches of one participant, read the same way."""
    meal_path, peak_path = branch_paths(data_dir, pid)
    return read_branch(meal_path), read_branch(peak_path)


def included_ids(table_dir, quality=0, verbose=True):
    """The analysed set, read from Table3.csv so it cannot drift from the code.

    Falls back to the reported set when the table is absent, and says so, so a
    standalone run is possible without silently analysing a different cohort.
    """
    path = os.path.join(table_dir, "Table3.csv")
    if os.path.isfile(path):
        tab = pd.read_csv(path)
        ids = [int(i) for i in tab.loc[tab.Quality == quality, "ID"]]
        if verbose:
            print(f"Included set read from Table3.csv: {ids}")
        return ids
    if verbose:
        print(f"Table3.csv not found; using the reported set: {REPORTED_N9}")
    return list(REPORTED_N9)
