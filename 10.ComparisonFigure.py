"""
10.ComparisonFigure.py
Figure 5 of the article: distribution of the absolute hourly BG relative
changes of the meal-based and the peak-based branches for one participant.

Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    Reads the hourly relative changes of both branches (one value per day and
    hour), takes their absolute values over all days and hours, and draws the
    two distributions side by side as box plots (means shown as dots), with a
    secondary axis in mmol/L. The two branches are compared statistically in
    G.BlandAltman.py.

Inputs
    globals.id, globals.idG, globals.path2, globals.path3,
    globals.MGDL_TO_MMOL, globals.FIGURE_TITLES
    <path2>/Boxplot<id>0-24total.csv       (meal branch, 9.Boxplot.py)
    <path2>/BoxplotPeak<id>0-24total.csv   (peak branch, 9.BoxplotPeak.py)

Output
    <path3>/Figure5.png                    only for idG
"""

import os
import pandas as pd
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
import globals

matplotlib.rcParams.update({'font.size': 18})

id = globals.id
path2 = globals.path2
path3 = globals.path3
os.makedirs(path3, exist_ok=True)

MGDL_TO_MMOL = globals.MGDL_TO_MMOL

# -----------------------------------------------------------#
#                    Read input files
# -----------------------------------------------------------#

data1 = pd.read_csv(path2 + "Boxplot" + str(id) + "0-24total.csv")
data2 = pd.read_csv(path2 + "BoxplotPeak" + str(id) + "0-24total.csv")

# Absolute values of every day and hour with data, per branch.
Total_group1 = []
Total_group2 = []
for i in range(24):
    col = "[" + str(i) + "-" + str(i + 1) + "]"
    group1 = data1[col].to_numpy()
    group2 = data2[col].to_numpy()
    group1 = group1[~np.isnan(group1)]
    group2 = group2[~np.isnan(group2)]
    Total_group1.extend(abs(v) for v in group1)
    Total_group2.extend(abs(v) for v in group2)


# -----------------------------------------------------------#
#                     Figure 5
# -----------------------------------------------------------#

# Distribution of the absolute hourly relative changes of each branch.

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
