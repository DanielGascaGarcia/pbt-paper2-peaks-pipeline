# PBT — Paper 2 Peaks Pipeline

Pipeline to detect and characterise **post-meal glucose peaks** from CGM, compute **hourly relative change** around those peaks, and summarise their distribution. Includes a simple runner that executes all steps in order.

---

## Manuscript context

This repository implements the **PBT — Paper 2 Peaks Pipeline**, a meal-agnostic approach to assess basal rate (BR) adequacy using CGM data. It detects and removes meal-related glucose excursions via peak detection, computes **hourly relative BG change**, and summarises 24-h behaviour to flag hours indicative of **excess** or **insufficient** basal insulin. The pipeline complements scenarios where closed-loop systems revert to manual mode or are unavailable, and supports periodic BR review in clinical settings.

---

## ✨ Features

- Parsing and harmonisation of Ohio-style XML (CGM ± meals)
- Daily **peak detection** on low-pass filtered BG with **prominence/width** discrimination (95th-percentile thresholds)
- “Next-day” handling to avoid window truncation across midnight
- Hourly stacks + baseline-subtracted **relative change**
- Reliability flags (per-hour counts)
- Exports for **24-h boxplots**, medians, and last-value series
- Optional **non-inferiority** vs meal-based exclusion (Paper 1)

---

## 📥 Inputs

- `ID-ws-training.xml` — Ohio-style CGM (and meals if available)
- `globals.py` — set `id`, paths (`path`, optional `path2`), base date, timezone, thresholds
- (Generated) `PivotBG_wCN.csv`, `PivotPeak_wCN.csv` — built by earlier steps

---

## 📤 Key outputs

- `glucose_level<ID>-ws-training_wCNF <YYYY-MM-DD>.csv` — BG with peak windows removed in [t−1 h, t+3 h]
- `glucose_level<ID>-ws-training_Merge <YYYY-MM-DD>.csv` — mask for windows crossing midnight
- `BGwNMLeftJoinedPeak<ID>.csv` — left-joined table of filtered days
- `BGHourPeak<ID><h>To<h+1>.csv` — hourly stacks by day
- `BGHourRelativeChangePeak<ID><h>To<h+1>.csv` — per-day **relative change** per hour (baseline-subtracted)
- `BGHourRelativeChangePeak<ID><h>To<h+1>lastValues.csv` — last point per day/hour
- `BoxplotPeak<ID>0-24total.csv` — 24-h summary used for boxplots
- `BGHourRelativeChangePeak<ID>0To24medians_wCN.csv` — 24-h medians + reliability flag (counts-based)
- `ComparisonJoinedPeakNoActivity<ID>.csv` — **median relative change only** (no basal columns)
- Figure from `9.BoxplotPeak.py`

---

## ▶️ Execution order

Run the orchestrator `17.ScriptforTestExperiment2.py`. It calls the scripts in this sequence:

1. `globals.py`  
2. `0.Parser.py`  
3. `1.ColumnNamer.py`  
4. `2.Disaggregator.py`  
5. `3.PivotGeneratorBG.py`  
6. `4.PeaksDetection.py`  
7. `5.MergePeaksNextDay.py`  
8. `6.MergePeaks.py`  
9. `7.SplitHoursPeaks.py`  
10. `8.RelativeChangePeaks.py`  
11. `9.BoxplotPeak.py`  
12. `10.Non-inferiorityTest.py` *(auto-skipped if Paper 1 file is missing)*  
13. `10.PivotGeneratormediansPeak.py`  
14. `12.MergeRChBasalPeakNoAct.py` *(no basal dependency; same colours)*

---

## 🚀 Quick start

```bash
# Edit globals.py (ID, paths, optional path2)
python 17.ScriptforTestExperiment2.py
```

---

## ⚙️ Requirements

- **Python ≥ 3.10**
- Packages: `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn` (see `requirements.txt`)

---

## 🔗 Upstream dependency (Paper 1)

This pipeline optionally uses a **Paper 1** artifact (same `id`) **only for the non-inferiority step**:

- `Boxplot{id}0-24total.csv` — 24-h distribution used by `10.Non-inferiorityTest.py`.

Obtain it by either:

- Running **Paper 1** with the same `id`, or  
- Downloading the versioned release: Zenodo https://doi.org/10.5281/zenodo.17392920 (Repo: https://github.com/DanielGascaGarcia/pbt-paper1-pipeline)

> If this file is not present in `globals.path2`, the runner will **skip** `10.Non-inferiorityTest.py` and continue.

---

## 🧪 Method in brief

1) Parse and harmonise CGM/insulin data  
2) Low-pass filter + peak detection  
3) Exclude windows around prominent peaks (−1 h to +3 h)  
4) Build 24-h composites + **relative BG change** by hour  
5) Add **reliability flag** (counts)  
6) Export per-hour distributions + 24-h boxplot summary  
7) (Optional) Non-inferiority vs meal-based exclusion + precision check

---

## 🤝 Contributing

Issues and PRs are welcome. Please keep function docs and I/O contracts consistent.

---

## 📚 Citation 

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17393514.svg)](https://doi.org/10.5281/zenodo.17393514)

- **Manuscript:** *Towards a Personalised Basal Tuner: Detecting Basal Rate Inaccuracies in Type 1 Diabetes Mellitus Without Meal Data* (PBT — Paper 2). **JMIR Diabetes** (accepted; in production, 2025).
- **Software (this repository):** Gasca García, D. **PBT — Paper 2 Peaks Pipeline (v1.0.0).** Zenodo/GitHub. DOI: https://doi.org/10.5281/zenodo.17393514



**BibTeX**
```bibtex
@software{gasca_garcia_pbt_paper2_peaks_2025_v1_1_2,
  author    = {Gasca Garcia, Daniel},
  title     = {PBT — Paper 2 Peaks Pipeline},
  version   = {v1.0.0},
  year      = {2025},
  doi       = {10.5281/zenodo.17393515},
  url       = {https://doi.org/10.5281/zenodo.17393514},
  publisher = {Zenodo}
}

