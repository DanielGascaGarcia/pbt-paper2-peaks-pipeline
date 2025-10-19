# Description: Plot hourly relative BG change WITHOUT basal info (colors preserved).
# Created: 19 Oct 2025 (refactor to remove basal dependency)
# Author: mbaxdg6 (refactor by assistant)

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
file_rel = f"BGHourRelativeChangePeak{id}0To24medians_wCN.csv"
file_out = f"ComparisonJoinedPeakNoActivity{id}.csv"   # mantenemos el nombre para compatibilidad
Sampling_time_hours = 0.1  # ~6 minutos

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
# Si deseas conservar el mismo CSV de salida, lo escribimos con las columnas disponibles
data[['Key', 'MedRelChange', 'Flag', 'TimeHours']].to_csv(os.path.join(path2, file_out), index=False)

# -----------------------------
# Muestreo (cada ~Sampling_time_hours)
# -----------------------------
data = data.sort_values('TimeHours').reset_index(drop=True)
step = max(1, int(round(Sampling_time_hours * 60)))  # 0.1 h ≈ 6 minutos
data_plot = data.iloc[::step, :].copy()

# -----------------------------
# Colores por confiabilidad (exactamente como en el original)
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
fig, ax2 = plt.subplots(nrows=1, sharex=True)
plt.suptitle(f"Blood Glucose Dynamic without Meal Announcement, ID: {id}")

# Curva principal (negra punteada) + línea base
ax2.plot(data_plot['TimeHours'], data_plot['MedRelChange'], 'o--', color="Black")
ax2.axhline(linewidth=2, color='Black')
ax2.set_xlabel("Time (h)")
ax2.set_ylabel("BG Rel. Change \n (mg/dL) (mmol/L)")
ax2.grid(which='major', color='#DDDDDD', linewidth=0.8)
ax2.grid(which='minor', color='#DDDDDD', linestyle=':', linewidth=0.5)

# Puntos por fiabilidad (mismo texto de leyenda que tu script original: "reliabilty")
legend_added = {'Low': False, 'Medium': False, 'High': False}

for i, row in data_plot.iterrows():
    flag = int(row['Flag'])
    color = row['Color']
    x = row['TimeHours']
    y = row['MedRelChange']

    if flag == 1:
        lbl = 'Low reliabilty of BG'
        if not legend_added['Low']:
            ax2.plot(x, y, 'o', color=color, label=lbl)
            legend_added['Low'] = True
        else:
            ax2.plot(x, y, 'o', color=color)
    elif flag == 2:
        lbl = 'Medium reliabilty of BG'
        if not legend_added['Medium']:
            ax2.plot(x, y, 'o', color=color, label=lbl)
            legend_added['Medium'] = True
        else:
            ax2.plot(x, y, 'o', color=color)
    else:
        lbl = 'High reliabilty of BG'
        if not legend_added['High']:
            ax2.plot(x, y, 'o', color=color, label=lbl)
            legend_added['High'] = True
        else:
            ax2.plot(x, y, 'o', color=color)

ax2.legend(loc='upper right')
plt.show()
