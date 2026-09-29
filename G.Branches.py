#Code: G.Branches.py
#Description: Hourly BG relative change for both algorithmic approaches,
#             all 12 participants - one panel each.
#             Answers the examiners' request to see the data visualised for
#             the outcomes of both approaches for all participants.
#
#             FIGURE SIZE. The figure is drawn at its final printed size
#             (6.3 in of text width) with the font sizes it will be read at,
#             so that no reduction happens at typesetting. Setting a large
#             figure and letting the page shrink it is what produced labels
#             under 6 pt in the version the examiners complained about.
#             Every value below is therefore a PRINTED size: change the
#             figure width only together with the fonts.
#
#             sharey is kept: across the twelve participants the interquartile
#             envelope spans 62 to 123 mg/dL, with no participant extreme
#             enough to compress the others, so a common axis aids comparison
#             at no cost. Verified on the data, not assumed.
#Author: mbaxdg6

import os

import matplotlib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from pbt_io import ALL_IDS, HOURS, read_branch

try:
    import globals
    PATH_IN, PATH_FIG, PATH_TAB = globals.path2, globals.path3, globals.path4
    FIGURE_TITLES = globals.FIGURE_TITLES
except ImportError:                       # standalone use
    PATH_IN = PATH_FIG = PATH_TAB = "./"
    FIGURE_TITLES = False

# All twelve participants: this figure shows the data, so nothing is excluded.
IDS = ALL_IDS

# Participants excluded from the paired comparison (>20% of days without a
# meal annotation), flagged in the panel titles. Read from Table3.csv when
# available so the figure cannot drift away from the criterion the pipeline
# applied.
_t3 = os.path.join(PATH_TAB, "Table3.csv")
if os.path.isfile(_t3):
    EXCLUDED = set(pd.read_csv(_t3).query("Quality == 1")["ID"].astype(int))
    print("Excluded set read from Table3.csv:", sorted(EXCLUDED))
else:
    EXCLUDED = {540, 552, 567}
    print("Table3.csv not found; using the reported set:", sorted(EXCLUDED))

MEAL_COLOUR = "#2980b9"
PEAK_COLOUR = "#c0392b"
MGDL_PER_MMOL = 18.0

# Printed sizes. The figure is saved at these dimensions and placed at 1:1.
FIG_W, FIG_H = 6.3, 8.4
matplotlib.rcParams.update({
    'font.size': 8,
    'axes.titlesize': 9,
    'axes.labelsize': 8.5,
    'xtick.labelsize': 7.5,
    'ytick.labelsize': 7.5,
    'legend.fontsize': 8,
    'axes.linewidth': 0.6,
})


def gapped(hours, *series):
    """Hourly points for line drawing, with one-hour gaps around missing hours.

    Each present hour keeps its own x position, so the line joins consecutive
    hours as usual. Where a neighbouring hour has no data, the present hour is
    extended half an hour towards it and the series is then broken, so the
    blank covers only the absent hour rather than the two segments touching it.
    """
    present = ~np.isnan(series[0])
    xs = []
    idx = []          # index into the original arrays, or None for a break
    for h in range(len(hours)):
        if present[h]:
            xs.append(float(h)); idx.append(h)
            if h + 1 < len(hours) and not present[h + 1]:
                xs.append(h + 0.5); idx.append(h)
                xs.append(np.nan); idx.append(None)
        elif h + 1 < len(hours) and present[h + 1]:
            xs.append(h + 0.5); idx.append(h + 1)
    out = [np.array(xs, dtype=float)]
    for arr in series:
        out.append(np.array([np.nan if i is None else arr[i] for i in idx],
                            dtype=float))
    return out


hours = np.arange(24)
fig, axes = plt.subplots(4, 3, figsize=(FIG_W, FIG_H), sharex=True, sharey=True)

for ax, pid in zip(axes.ravel(), IDS):
    meal = read_branch(os.path.join(PATH_IN, f"Boxplot{pid}0-24total.csv"))
    peak = read_branch(os.path.join(PATH_IN, f"BoxplotPeak{pid}0-24total.csv"))

    for df, colour, label in [(meal, MEAL_COLOUR, "Meal-based"),
                              (peak, PEAK_COLOUR, "Peak-based")]:
        median = df.median(axis=0, skipna=True).values
        q1 = df.quantile(0.25).values
        q3 = df.quantile(0.75).values
        # Lines between hourly points, with a missing hour leaving a gap
        # exactly one hour wide. A plain NaN would break both adjoining
        # segments and the gap would read as two hours; instead each
        # neighbour of an absent hour is extended half an hour towards it,
        # so the blank spans only the hour that has no data. Affects ID 588
        # only (hours 13 and 20 of the meal branch).
        xs, ys, lo, hi = gapped(hours, median, q1, q3)
        ax.fill_between(xs, lo, hi, color=colour, alpha=0.15, linewidth=0)
        ax.plot(xs, ys, color=colour, linewidth=1.3, label=label)

    ax.axhline(0, color="0.4", linewidth=0.7, linestyle="--")
    ax.set_title(f"ID {pid}" + ("  (excluded)" if pid in EXCLUDED else ""),
                 color="0.45" if pid in EXCLUDED else "black", pad=3)
    ax.grid(color="0.9", linewidth=0.4)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(length=2.5, width=0.6)

axes[0, 0].legend(frameon=False, loc="upper left", handlelength=1.4,
                  borderaxespad=0.2)
for ax in axes[-1]:
    ax.set_xlabel("Hour of day")
    ax.set_xticks([0, 6, 12, 18, 23])
for ax in axes[:, 0]:
    ax.set_ylabel("BG relative change (mg/dL)")

# Secondary axis in mmol/L on the right-hand column, matching the other
# figures in the article. Drawn last so it inherits the shared y limits.
for ax in axes[:, -1]:
    sec = ax.secondary_yaxis(
        'right', functions=(lambda v: v / MGDL_PER_MMOL,
                            lambda v: v * MGDL_PER_MMOL))
    sec.set_ylabel("(mmol/L)")
    sec.tick_params(length=2.5, width=0.6)
    sec.spines['right'].set_linewidth(0.6)

if FIGURE_TITLES:
    fig.suptitle("Hourly BG relative change by branch, all 12 participants",
                 fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
else:
    fig.tight_layout()

os.makedirs(PATH_FIG, exist_ok=True)
# Figure 9 of paper 2. PNG only.
out = os.path.join(PATH_FIG, "Figure9.png")
plt.savefig(out, dpi=600)
print("SAVED:", os.path.abspath(out))
plt.close(fig)

# The definition of line and band belongs in the manuscript caption, not in a
# figure title that is not drawn. Printed here so it travels with the figure.
print("\nCaption to use:\n"
      "  Hourly BG relative change for both algorithmic branches, all 12 "
      "participants.\n  The line is the median across days and the band the "
      "interquartile range.\n  Participants excluded from the paired "
      "comparison (>20% of days without a\n  meal annotation) are marked in "
      "the panel titles. Gaps mark hours with no\n  data in that branch.")
