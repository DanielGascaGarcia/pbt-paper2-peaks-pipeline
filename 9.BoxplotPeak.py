#Code: 9.BoxplotPeak.py
#Description: Generating pivot with relative changes on peaks + boxplot figure.
#Created 14th November 2023
#Author: mbaxdg6

import os
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib
import globals

# --- Font configuration (smaller, balanced for 1200 px) ---
matplotlib.rcParams.update({
    'font.size': 10,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9
})

# --- Configurable variables from globals ---
pid = globals.id
path2 = globals.path2
path3 = globals.path3
fileToRead = f"BGHourRelativeChangePeak{pid}"
fileToSave = f"BoxplotPeak{pid}"

# -----------------------------------------------------------#
# Unit conversion. Source values are in mg/dL.
# Factor lives in globals.py so every script shares one value.
# -----------------------------------------------------------#
MGDL_TO_MMOL = globals.MGDL_TO_MMOL

# Reference band, in mmol/L, shaded on the figure. Kept as a constant so the
# band and the axis conversion cannot drift apart.
BAND_MMOL = 2

ref_cols = pd.read_csv(f"{path2}{fileToRead}0To1.csv").columns
n_rows = len(ref_cols) - 1


def read_last_values(hour):
    """Read one lastValues file, one row per day, keeping day positions.

    Step 8 writes a blank entry for days with no valid reading. pandas skips
    whitespace-only lines by default, which would shift every later value up
    one row and break the correspondence between row index and day. Reading
    with skip_blank_lines=False keeps the row; to_numeric turns the blank into
    NaN without dropping it.
    """
    df = pd.read_csv(f"{path2}{fileToRead}{hour}To{hour+1}lastValues.csv",
                     skip_blank_lines=False)
    df['Last_values'] = pd.to_numeric(df['Last_values'], errors='coerce')
    return df


# -----------------------------------------------------------#
# Obtain the last values (reversed order — used for the figure)
# -----------------------------------------------------------#
total = pd.DataFrame(index=range(n_rows))
for i in reversed(range(24)):
    df_i = read_last_values(i)
    df_i.rename(columns={'Last_values': f"{i}-{i+1}"}, inplace=True)
    total[f"{i}-{i+1}"] = df_i[f"{i}-{i+1}"]

# -----------------------------------------------------------#
# Saving in the correct order (forward, bracketed) — consumed
# by the comparison stage, which looks up "[0-1]", "[1-2]"...
# -----------------------------------------------------------#
total1 = pd.DataFrame(index=range(n_rows))
for i in range(24):
    df_i = read_last_values(i)
    df_i.rename(columns={'Last_values': f"[{i}-{i+1}]"}, inplace=True)
    total1[f"[{i}-{i+1}]"] = df_i[f"[{i}-{i+1}]"]

total1.to_csv(f"{path2}{fileToSave}0-24total.csv", index=False)

# ---------------- Figure ---------------- #
fig, ax = plt.subplots(figsize=(6, 4), dpi=200)

# Boxplot horizontal
pd.DataFrame.boxplot(
    total, vert=False, patch_artist=True, ax=ax, grid=False,
    boxprops=dict(facecolor='lightblue', color='black'),
    whiskerprops=dict(color='black', linewidth=1.0),
    capprops=dict(color='black', linewidth=1.0),
    medianprops=dict(color='red', linewidth=1.2)
)

# Subtle grid
ax.grid(color='gray', linestyle='--', linewidth=0.4, alpha=0.6)

# Labels (sentence case)
ax.set_xlabel("BG relative change (mg/dL)")
ax.set_ylabel("Hours")

# Highlight region +/-2 mmol/L, expressed in the mg/dL of the primary axis
highlight_start = -BAND_MMOL / MGDL_TO_MMOL
highlight_end = BAND_MMOL / MGDL_TO_MMOL
ax.axvspan(highlight_start, highlight_end, color="blue", alpha=0.20,
           label="No significant change")

# Secondary x-axis in mmol/L
def mg_dL_to_mmol(x): return x * MGDL_TO_MMOL
def mmol_to_mg_dL(x): return x / MGDL_TO_MMOL

secax = ax.secondary_xaxis('top', functions=(mg_dL_to_mmol, mmol_to_mg_dL))
secax.set_xlabel("BG relative change (mmol/L)")

# --- Force en dash for negative tick labels ---
def fmt_en_dash(x, pos=None, decimals=None):
    """Return tick labels with EN DASH for negative values."""
    s_abs = f"{abs(x):g}" if decimals is None else f"{abs(x):.{decimals}f}"
    return f"\u2013{s_abs}" if x < 0 else s_abs

ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: fmt_en_dash(x, p)))
secax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: fmt_en_dash(x, p, decimals=1)))

# Legend in sentence case
ax.legend(loc='upper right', frameon=False, title=None)

# -----------------------------------------------------------#
# Patient identifier, inside the axes as in the published figure.
# -----------------------------------------------------------#
ax.text(0.01, 0.98, f"patient ID: {pid}", transform=ax.transAxes,
        ha="left", va="top", fontsize=9, color="black")

yticklabels = [t.get_text().replace("-", "\u2013").replace("\u2212", "\u2013")
               for t in ax.get_yticklabels()]
ax.set_yticklabels(yticklabels)

plt.tight_layout()

# -----------------------------------------------------------#
# Save the figure (do NOT use plt.show(): it blocks the runner)
#
# Only the worked example used in the article is written. The panel is built
# for every participant because the CSV above is, but the other panels are
# not part of the record.
# -----------------------------------------------------------#
os.makedirs(path3, exist_ok=True)

if pid == globals.idG:
    out = os.path.join(path3, "Figure4.png")
    plt.savefig(out, dpi=300, bbox_inches='tight')
    print("Saved:", os.path.abspath(out))

plt.close(fig)
