#Code: globals.py
#Description: Central configuration for the experiment 2 pipeline.
#             Every script imports this module, so all paths, IDs and
#             constants live here and nowhere else. Do not hardcode any
#             of these values inside individual scripts.
#Author: mbaxdg6

import os
import matplotlib

# Non-interactive backend. Set here, at import time, so no script opens a
# window and blocks the orchestrator. Comment out to see figures while
# working locally.
matplotlib.use("Agg")

# -----------------------------------------------------------#
# Demo mode
# -----------------------------------------------------------#
# The OhioT1DM dataset cannot be redistributed, so the repository ships a
# generator of synthetic files in the same schema instead. With DEMO = True
# the orchestrator regenerates those files and runs the pipeline on them,
# which lets anyone verify that the code executes end to end without access
# to the real data.
#
# Demo mode reads and writes a SEPARATE directory (sample_data/). It never
# touches raw/, so leaving this set to True by accident cannot overwrite
# data obtained under the Data Use Agreement.
#
# Results produced in demo mode are meaningless. Do not compare them with
# anything reported in the article or in the correction notice.
DEMO = True

# -----------------------------------------------------------#
# Paths
# -----------------------------------------------------------#
# Resolved relative to this file, so the repository runs as cloned and a
# script can also be run on its own from any working directory. The previous
# version carried absolute Windows paths, which is why the deposited code did
# not run elsewhere.
#
#   path1  raw        input data as downloaded from OhioT1DM
#                     (sample_data/ when DEMO is True)
#   path2  processed  intermediate CSVs passed between pipeline steps
#   path3  figures    final figures
#   path4  tables     final tables
#
# NOTE: several steps collect their inputs by listing whatever per-day files
# are present in path2, rather than regenerating a known list. A leftover
# file from an earlier run is therefore picked up as if it belonged to the
# current one. The orchestrator clears path2 before every run for this
# reason; clear it by hand if you run steps individually.
HERE = os.path.dirname(os.path.abspath(__file__))
_out = 'demo_output' if DEMO else '.'

path1 = os.path.join(HERE, 'sample_data' if DEMO else 'raw') + '/'
path2 = os.path.join(HERE, _out, 'processed') + '/'
path3 = os.path.join(HERE, _out, 'results', 'figures') + '/'
path4 = os.path.join(HERE, _out, 'results', 'tables') + '/'

for _p in (path2, path3, path4):
    os.makedirs(_p, exist_ok=True)

# -----------------------------------------------------------#
# Participant selection
# -----------------------------------------------------------#
# Current participant. Read from the PATIENT_ID environment variable so the
# orchestrator can loop over participants without editing this file (it sets
# PATIENT_ID per subprocess). The default only applies when a script is run
# on its own from the editor.
# NOTE: the name shadows Python's built-in id(). A script that forgets to
# assign it will therefore NOT raise NameError -- it silently picks up the
# built-in function instead. Rename to patient_id if this ever bites.
id = int(os.environ.get("PATIENT_ID", 588))

# All twelve OhioT1DM participants. This experiment uses the full cohort;
# the exclusion criterion is applied later, from the meal-annotation counts,
# not by leaving participants out of the run.
ids = [559, 563, 570, 575, 588, 591,
       540, 544, 552, 567, 584, 596]

# Participant shown as the worked example. Scripts that produce a
# single-subject illustrative figure check `id == idG` before saving, so the
# figure is only written once per full run.
idG = 588

# Days per participant generated in demo mode. The real dataset provides
# about 45 days per participant; a short synthetic run is enough to verify
# that every step executes, but the figures it produces are sparse and the
# last day is always incomplete, because the midnight-overflow trimming
# needs the following day to close.
DEMO_DAYS = 5

# Seed for the synthetic generator, so a demo run is reproducible. The
# generator derives a per-participant seed from this value and carries the
# same number as its own default, so it produces identical files whether it
# is launched by the orchestrator or on its own from the command line.
DEMO_SEED = 20260801

# -----------------------------------------------------------#
# Exclusion criterion
# -----------------------------------------------------------#
# A participant is flagged as low quality when MORE than this fraction of
# their days lack meal annotations, since precision cannot be scored on
# those days. `4.PeaksDetection.py` writes the flag into the Quality column
# of the summary table; the analysis scripts read it from there.
#
# The threshold reproduces the rule applied in the original analysis. It was
# not stated explicitly in the published article and is declared here so
# that the reported participant set can be traced to a single value.
MISSING_THRESHOLD = 0.20

# Day used for the worked example (Figure 2), as a zero-based index into the
# participant's sorted day files. The manuscript uses day 35 of idG, i.e.
# index 34. A demo run only has DEMO_DAYS days, so a lower index is needed
# there or the figure is never produced.
FIG2_DAY = 3 if DEMO else 34

# -----------------------------------------------------------#
# Unit conversion
# -----------------------------------------------------------#
# All blood glucose values in the pipeline are stored in mg/dL. This is the
# single factor used to add mmol/L to tables and secondary axes. Kept here
# so the axes, the tolerance bands and the tables can never drift apart.
# 18 is the conventional rounding of the exact factor (18.0182); at the
# precision reported in the manuscripts the two are indistinguishable.
MGDL_TO_MMOL = 1/18

# -----------------------------------------------------------#
# Figure formatting
# -----------------------------------------------------------#
# Journals put the figure title in the caption, not inside the image.
# Keep this False for the figures that go into the manuscript; set it to
# True when reviewing plots locally and you want them self-labelled.
FIGURE_TITLES = False
