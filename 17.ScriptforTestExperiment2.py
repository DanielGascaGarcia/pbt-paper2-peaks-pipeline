# Code: 17.ScriptforTestExperiment2.py
# Description: Orchestrator for Paper 2 (Peaks) with optional Paper 1 dependency.
# Created: 19 Oct 2025
# Author: mbaxdg6 (with assistant refactor)

import os
import subprocess
import globals

print(f"[Paper 2] Current id: {globals.id}")
print(f"[Paper 2] globals.path2: {globals.path2}")

# --- Preflight: check Paper 1 dependency (only for the non-inferiority step) ---
p_boxplot_p1 = os.path.join(globals.path2, f"Boxplot{globals.id}0-24total.csv")
HAS_P1_BOXPLOT = os.path.isfile(p_boxplot_p1)

if not HAS_P1_BOXPLOT:
    print(
        "[Paper 2] WARN: Missing Paper 1 artifact:\n"
        f" - {p_boxplot_p1}\n"
        "Non-inferiority test (10.Non-inferiorityTest.py) will be skipped.\n"
        "To enable it, run Paper 1 (same id) or download from Zenodo: "
        "https://doi.org/10.5281/zenodo.17392921\n"
        f"Current globals.path2: {globals.path2}\n"
    )

# --- Execution list (Paper 2) ---
scripts = [
    "globals.py",
    "0.Parser.py",
    "1.ColumnNamer.py",
    "2.Disaggregator.py",
    "3.PivotGeneratorBG.py",
    "4.PeaksDetection.py",
    "5.MergePeaksNextDay.py",
    "6.MergePeaks.py",
    "7.SplitHoursPeaks.py",
    "8.RelativeChangePeaks.py",
    "9.BoxplotPeak.py",
    "10.Non-inferiorityTest.py",       # <- only if HAS_P1_BOXPLOT
    "10.PivotGeneratormediansPeak.py",
    "12.MergeRChBasalPeakNoAct.py",    # <- modified (no basal, keeps colors)
]

# Remove non-inferiority if requirement missing
if not HAS_P1_BOXPLOT and "10.Non-inferiorityTest.py" in scripts:
    scripts.remove("10.Non-inferiorityTest.py")

# --- Run sequentially ---
for script in scripts:
    try:
        print(f"[Paper 2] Running: {script} ...")
        subprocess.run(["python", script], check=True)
        print(f"[Paper 2] {script} completed.\n")
    except subprocess.CalledProcessError as e:
        print(f"[Paper 2] ERROR while running {script}: {e}")
        break
