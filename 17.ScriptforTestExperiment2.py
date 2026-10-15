"""
17.ScriptforTestExperiment2.py
Orchestrator for the experiment 2 (paper 2) pipeline: the peak-based branch
and the meal-based branch it is compared against.

Created: 5 July 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    1. Demo mode: regenerates the synthetic input. Real mode: checks that the
       twelve OhioT1DM training files are in place.
    2. Clears the intermediate folder (path2). path3 and path4 are not
       cleared; the table written there by a per-participant step replaces
       each participant's row (Table3.csv).
    3. Runs COMMON + MEALS + PEAKS + COMPARE once per participant, passing
       the ID through PATIENT_ID.
    4. Stops before the aggregation if any participant failed or did not
       produce both Boxplot<id> and BoxplotPeak<id> summaries.
    5. Runs the cross-participant scripts with PATIENT_ID = globals.idG.

Usage
    python 17.ScriptforTestExperiment2.py
"""

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
    "10.ComparisonFigure.py",
    "10.PivotGeneratormediansPeak.py",
    "12.MergeRChBasalPeakNoAct.py",
]

PIPELINE = COMMON + MEALS + PEAKS + COMPARE

# Cross-patient scripts, run once after every ID is done.
FINAL_SCRIPTS = [
    "G.CGMCoverage.py",
    "G.PrecisionSummary.py",
    # Agreement between the two branches (read Table3.csv, written during the
    # per-participant pass). Shared reader: pbt_io.py.
    "G.BADescriptives.py",       # descriptive statistics
    "G.BlandAltman.py",          # primary analysis, absolute and signed
    "G.Divergence.py",           # Jensen-Shannon / Kullback-Leibler
    "G.Branches.py",             # both branches, all 12 participants
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
    # steps later as an unrelated error.
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
# entering the analysis would reflect the state of the directory instead of
# the input data. Clearing it makes every run independent of earlier ones.
print(f"Clearing intermediate directory: {globals.path2}")
shutil.rmtree(globals.path2, ignore_errors=True)
for directory in (globals.path2, globals.path3, globals.path4):
    os.makedirs(directory, exist_ok=True)

# ------------------------------------------------------------------ #
# Per-participant pipeline
# ------------------------------------------------------------------ #
failures = []
completed = []

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
        completed.append(patient_id)
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

# ------------------------------------------------------------------ #
# Confirm every participant produced BOTH branch summaries
# ------------------------------------------------------------------ #
# A step can lose a participant without raising: an empty read, a silent
# exception, a filter that matches nothing. The pipeline then completes and
# the aggregation scripts average over whatever is present. It matters more
# here than in the meal-only pipeline, because an analysis that pairs the
# two branches would silently drop any participant missing either one.
#
# Size is checked as well as existence: a step that opens its output file
# and then fails leaves a zero-byte CSV behind, which os.path.isfile alone
# would accept as a successful run.
expected = [(i, f"{prefix}{i}0-24total.csv")
            for i in globals.ids
            for prefix in ("Boxplot", "BoxplotPeak")]
absent = []
for i, f in expected:
    p = os.path.join(globals.path2, f)
    if not os.path.isfile(p):
        absent.append((i, f, "not found"))
    elif os.path.getsize(p) == 0:
        absent.append((i, f, "empty"))
if absent:
    print(f"\n{'=' * 58}")
    print("  OUTPUTS MISSING AFTER PIPELINE")
    print(f"{'=' * 58}")
    print(f"  Expected in: {globals.path2}")
    for i, f, why in absent:
        print(f"    ID {i:<6} {f:<34} {why}")
    print(f"\n  {len(absent)} expected file(s) absent or empty, and every")
    print("  step reported success. Aggregation was not run: it reads all")
    print("  participants at once and would have produced output from an")
    print("  incomplete set.\n")
    sys.exit(1)
print(f"\n  All {len(globals.ids)} participants produced both branch summaries.")

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
print(f"  IDs completed : {len(completed)}")

if failures:
    print(f"\n  {len(failures)} failure(s) in the aggregation stage:")
    for pid, script, code in failures:
        print(f"    {script:<36} exit {code}")
    sys.exit(1)

print("\n  No failures.")
if globals.DEMO:
    print("\n  This was a demo run on synthetic data. The outputs are not")
    print("  comparable with the reported results.")
