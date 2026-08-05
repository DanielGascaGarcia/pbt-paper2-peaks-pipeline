#Code: 17.ScriptforTestExperiment2.py
#Description: Full pipeline runner for experiment 2 (peak detector)
#             plus the meal-based branch it is compared against.
#Created 5th July 2023
#Author: mbaxdg6

import subprocess
import shutil
import sys
import os
import globals

HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ #
# Phases
#
# COMMON  parsing and the BG pivot. Everything else depends on it.
# MEALS   meal-based branch (experiment 1). Produces Boxplot<id>0-24total.csv
# PEAKS   peak-based branch (experiment 2). Produces BoxplotPeak<id>0-24total.csv
# COMPARE analyses that need BOTH branches, so they must run last —
#         not inside the PEAKS branch.
# ------------------------------------------------------------------ #
COMMON = [
    "0.Parser.py",
    "1.ColumnNamer.py",
    "2.Disaggregator.py",
    "3.PivotGeneratorBG.py",
]

MEALS = [
    "4.MealBolusDetection.py",
    "5.MergeBGClean.py",
    "6.SplitHours.py",
    "7.InterpolationBGHourly.py",
    "8.RelativeChange.py",
    "9.Boxplot.py",
]

PEAKS = [
    "4.PeaksDetection.py",
    "5.MergePeaksNextDay.py",
    "6.MergePeaks.py",
    "7.SplitHoursPeaks.py",
    "8.RelativeChangePeaks.py",
    "9.BoxplotPeak.py",
]

COMPARE = [
    "10.Non-inferiorityTest.py",
    "10.PivotGeneratormediansPeak.py",
    "12.MergeRChBasalPeakNoAct.py",
]

PIPELINE = COMMON + MEALS + PEAKS + COMPARE

# Cross-patient scripts, run once after every ID is done.
FINAL_SCRIPTS = [
    "G.CGMCoverage.py",
    "G.PrecisionSummary.py",
    "G.GraphResultsPeak.py",
    "G.Graph3DCleanBGPeak.py",
    "G.Graph3DPeaksRemoved.py",
    "G.Graph3DComplete.py",
    # These two run last: they read the panel PNGs written by the steps above
    # and by the per-participant pass, and compose the multi-panel figures.
    "G.ComposeFigure2.py",
    "G.ComposeFigure3.py",
]

# ------------------------------------------------------------------ #
# Demo data
# ------------------------------------------------------------------ #
# In demo mode the synthetic input files are regenerated from scratch, so a
# run never mixes files from different generator settings. This only ever
# touches sample_data/; globals.path1 points at raw/ when DEMO is False and
# the block below is skipped entirely.
print(f"Interpreter: {sys.executable}\n")

if globals.DEMO:
    print("========== DEMO MODE: generating synthetic input data ==========\n")
    print("Results produced from these files are meaningless. Do not compare")
    print("them with anything reported in the article.\n")
    shutil.rmtree(globals.path1, ignore_errors=True)
    subprocess.run(
        [sys.executable, "S.GenerateSampleData.py",
         "--out", globals.path1,
         "--days", str(globals.DEMO_DAYS),
         "--seed", str(globals.DEMO_SEED),
         "--ids", *[str(i) for i in globals.ids]],
        check=True, cwd=HERE,
    )
else:
    # -----------------------------------------------------------#
    # Real dataset: fail early and say what is missing
    # -----------------------------------------------------------#
    # Without this check a missing or misplaced dataset surfaces several
    # steps later as an unrelated error. This is what produced the
    # SET_ME-ws-training.xml failure reported against the deposited code.
    missing = [i for i in globals.ids
               if not os.path.isfile(os.path.join(globals.path1,
                                                  f"{i}-ws-training.xml"))]
    if missing:
        print("========== INPUT DATA NOT FOUND ==========\n")
        print(f"Expected in: {globals.path1}")
        for i in missing:
            print(f"  missing: {i}-ws-training.xml")
        print("\nThe OhioT1DM dataset is not redistributable and is not")
        print("included here. Request it from its custodians under their Data")
        print("Use Agreement, then place the training files listed above in")
        print("the directory shown. Only the '-ws-training' files are used;")
        print("the test portion is not.")
        print("\nTo verify that the pipeline executes without the real data,")
        print("set DEMO = True in globals.py. That runs on synthetic files in")
        print("the same schema; its outputs are meaningless.\n")
        sys.exit(1)

# ------------------------------------------------------------------ #
# Clean intermediate directory
# ------------------------------------------------------------------ #
# Not optional, and not only for demo runs. Several steps collect their
# inputs by listing whatever per-day files are present in path2 rather than
# regenerating a known list, and the midnight-overflow step rewrites those
# files in place. A file left behind by an earlier or partial run is
# therefore picked up as if it belonged to this one, and the number of days
# entering the analysis reflects the state of the directory instead of the
# input data. This is the defect behind the divergence between the
# originally published outputs and a clean run.
print(f"Clearing intermediate directory: {globals.path2}")
shutil.rmtree(globals.path2, ignore_errors=True)
for directory in (globals.path2, globals.path3, globals.path4):
    os.makedirs(directory, exist_ok=True)

# ------------------------------------------------------------------ #
# Per-participant pipeline
# ------------------------------------------------------------------ #
failures = []

for patient_id in globals.ids:
    print(f"\n{'=' * 58}")
    print(f"  Pipeline for ID {patient_id}")
    print(f"{'=' * 58}\n")

    env = os.environ.copy()
    env["PATIENT_ID"] = str(patient_id)

    for script in PIPELINE:
        print(f"  -> {script}")
        try:
            subprocess.run([sys.executable, script],
                           check=True, env=env, cwd=HERE)
        except subprocess.CalledProcessError as e:
            print(f"     FAILED (exit {e.returncode}) — skipping rest of ID {patient_id}")
            failures.append((patient_id, script, e.returncode))
            break
    else:
        print(f"\n  ID {patient_id}: complete")

# ------------------------------------------------------------------ #
# Aggregation
# ------------------------------------------------------------------ #
# The aggregation scripts read every participant at once, so running them
# after a partial pipeline would silently produce figures and tables based
# on an incomplete set. Stop instead.
if failures:
    print(f"\n{'=' * 58}")
    print("  RUN FAILED — aggregation not attempted")
    print(f"{'=' * 58}")
    for pid, script, code in failures:
        print(f"    ID {pid:<6} {script:<36} exit {code}")
    print("\n  The aggregation scripts read all participants at once and")
    print("  would have produced output from an incomplete set.")
    print("  Fix the errors above and re-run.\n")
    sys.exit(1)

env_final = os.environ.copy()
env_final["PATIENT_ID"] = str(globals.idG)

for script in FINAL_SCRIPTS:
    print(f"\n{'=' * 58}")
    print(f"  {script} (all IDs)")
    print(f"{'=' * 58}\n")
    try:
        subprocess.run([sys.executable, script],
                       check=True, env=env_final, cwd=HERE)
    except subprocess.CalledProcessError as e:
        print(f"     FAILED (exit {e.returncode})")
        failures.append(("ALL", script, e.returncode))

# ------------------------------------------------------------------ #
# Summary — so a failure buried 200 lines up is not missed
# ------------------------------------------------------------------ #
print(f"\n{'=' * 58}")
print("  SUMMARY")
print(f"{'=' * 58}")
print(f"  IDs attempted : {len(globals.ids)}")
print(f"  IDs completed : {len(globals.ids)}")

if failures:
    print(f"\n  {len(failures)} failure(s) in the aggregation stage:")
    for pid, script, code in failures:
        print(f"    {script:<36} exit {code}")
    sys.exit(1)

print("\n  No failures.")
if globals.DEMO:
    print("\n  This was a demo run on synthetic data. The outputs are not")
    print("  comparable with the reported results.")
