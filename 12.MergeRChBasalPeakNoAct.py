# Description: Plot hourly relative BG change WITHOUT basal info (colors preserved).
# Created: 19 Oct 2025 (refactor to remove basal dependency)
# Author: mbaxdg6

import os
import numpy as np
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
matplotlib.rcParams.update({'font.size': 15})

import globals

# --- Configurable globals ---
id = globals.id
path2 = globals.path2
path3 = globals.path3
os.makedirs(path3, exist_ok=True)
file_rel = f"BGHourRelativeChangePeak{id}0To24medians_wCN.csv"
file_out = f"ComparisonJoinedPeakNoActivity{id}.csv"   # mantenemos el nombre para compatibilidad
Sampling_time_hours = 0.1  # ~6 minutos

# -----------------------------------------------------------#
# Unit conversion. Source values are in mg/dL.
# Factor lives in globals.py so every script shares one value.
# -----------------------------------------------------------#
MGDL_TO_MMOL = globals.MGDL_TO_MMOL

# -----------------------------
# Read relative-change only
# -----------------------------
p_rel = os.path.join(path2, file_rel)
if not os.path.isfile(p_rel):
    raise FileNotFoundError(f"[Paper 2] Missing required file: {p_rel}")

data = pd.read_csv(p_rel)
data['Key'] = data['Key'].astype(str).str.strip()

# Comprobación de columnas mínimas
needed_cols = {'Key', 'MedRelChange', 'Flag'}
missing = needed_cols - set(data.columns)
if missing:
    raise ValueError(f"[Paper 2] Missing columns in {p_rel}: {sorted(missing)}")

# Convierte HH:MM:SS -> horas decimales
def hhmmss_to_hours(s: str) -> float:
    h, m, sec = s.split(':')
    return (int(h) * 3600 + int(m) * 60 + int(sec)) / 3600.0

data['TimeHours'] = data['Key'].apply(hhmmss_to_hours)

# -----------------------------
# Guardar salida (sin basal)
# -----------------------------
data[['Key', 'MedRelChange', 'Flag', 'TimeHours']].to_csv(os.path.join(path2, file_out), index=False)

# -----------------------------
# Muestreo (cada ~Sampling_time_hours)
# -----------------------------
data = data.sort_values('TimeHours').reset_index(drop=True)
step = max(1, int(round(Sampling_time_hours * 60)))  # 0.1 h ≈ 6 minutos
data_plot = data.iloc[::step, :].copy()

# -----------------------------
# Colores por confiabilidad
# Flag: 1 -> "Red" (Low), 2 -> "Yellow" (Medium), else -> "Green" (High)
# -----------------------------
col = np.where(
    np.array(data_plot['Flag']) == 1, "Red",
    np.where(np.array(data_plot['Flag']) == 2, "Yellow", "Green")
)
data_plot['Color'] = col

# -----------------------------
# Plot
# -----------------------------
fig, ax2 = plt.subplots(nrows=1, sharex=True, figsize=(12, 6),
                        constrained_layout=True)

# Journals put the title in the caption, not in the image.
if globals.FIGURE_TITLES:
    plt.title(f"BG dynamics without meal announcement, patient ID: {id}")

# Main curve (black dotted) + baseline at 0
ax2.plot(data_plot['TimeHours'], data_plot['MedRelChange'], 'o--', color="Black")
ax2.axhline(y=0, linewidth=2, color='Black')

# Sentence case axis labels. Units are split across the two axes below.
ax2.set_xlabel("Time (h)")
ax2.set_ylabel("BG relative change\n(mg/dL)")

ax2.grid(which='major', color='#DDDDDD', linewidth=0.8)
ax2.grid(which='minor', color='#DDDDDD', linestyle=':', linewidth=0.5)

# Legend labels in sentence case, spelling fixed
legend_added = {'Low': False, 'Medium': False, 'High': False}

for _, row in data_plot.iterrows():
    flag = int(row['Flag'])
    color = row['Color']
    x = row['TimeHours']
    y = row['MedRelChange']

    if flag == 1:
        lbl = 'Low reliability of BG'
        if not legend_added['Low']:
            ax2.plot(x, y, 'o', color=color, label=lbl)
            legend_added['Low'] = True
        else:
            ax2.plot(x, y, 'o', color=color)
    elif flag == 2:
        lbl = 'Medium reliability of BG'
        if not legend_added['Medium']:
            ax2.plot(x, y, 'o', color=color, label=lbl)
            legend_added['Medium'] = True
        else:
            ax2.plot(x, y, 'o', color=color)
    else:
        lbl = 'High reliability of BG'
        if not legend_added['High']:
            ax2.plot(x, y, 'o', color=color, label=lbl)
            legend_added['High'] = True
        else:
            ax2.plot(x, y, 'o', color=color)

# -----------------------------------------------------------#
# Legend ordered Low / Medium / High regardless of the order in
# which the categories first appear in the series.
# -----------------------------------------------------------#
wanted = ['Low reliability of BG',
          'Medium reliability of BG',
          'High reliability of BG']
handles, labels = ax2.get_legend_handles_labels()
pairs = dict(zip(labels, handles))
ordered = [(lbl, pairs[lbl]) for lbl in wanted if lbl in pairs]
if ordered:
    ax2.legend([h for _, h in ordered], [l for l, _ in ordered],
               loc='upper right', fontsize=11, framealpha=0.9)

# -----------------------------------------------------------#
# Patient identifier, inside the axes as in the published figure.
# -----------------------------------------------------------#
ax2.text(0.01, 0.98, f"patient ID: {id}", transform=ax2.transAxes,
         ha="left", va="top", fontsize=11, color="black")

# -----------------------------------------------------------#
# Secondary axis in mmol/L. Rescale only: the data is drawn once
# on ax2. Placed here so it inherits the final y limits.
# -----------------------------------------------------------#
ax2b = ax2.twinx()
ax2b.set_ylim([v * MGDL_TO_MMOL for v in ax2.get_ylim()])
ax2b.set_ylabel("BG relative change\n(mmol/L)")
ax2b.grid(False)

# -----------------------------------------------------------#
# Save figure. Only the worked example used in the article is
# written; the panel is built for every participant because the
# CSV above is, but the other panels are not part of the record.
# -----------------------------------------------------------#
if id == globals.idG:
    out = os.path.join(path3, 'Figure6.png')
    plt.savefig(out, dpi=300, bbox_inches='tight')
    print("Saved:", os.path.abspath(out))

plt.close(fig)
