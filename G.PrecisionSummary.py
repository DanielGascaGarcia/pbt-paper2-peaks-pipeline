#Code: G.PrecisionSummary.py
#Description: Summary of classification precision across participants, read
#             from the per-participant table written by 4.PeaksDetection.py.
#
#             Two levels are reported and labelled as such:
#               - participant level: the mean of the per-participant
#                 precisions, with a t interval on n-1 degrees of freedom.
#                 This is the reported statistic.
#               - pooled: successes over scored peaks across participants,
#                 reported as a count. No interval is attached, because the
#                 peaks are clustered within participants and a binomial
#                 interval would treat them as independent.
#Author: mbaxdg6

import os
import numpy as np
import pandas as pd
from scipy import stats as scistats
import globals

path4 = globals.path4
os.makedirs(path4, exist_ok=True)

src = os.path.join(path4, "Table3.csv")
if not os.path.isfile(src):
    raise FileNotFoundError(
        f"Missing {src}. It is written by 4.PeaksDetection.py, one row per "
        f"participant, so the per-participant pass must run first.")

t = pd.read_csv(src).sort_values("ID").reset_index(drop=True)


def summarise(d, label):
    n = len(d)
    mean = d.Precision.mean()
    sd = d.Precision.std(ddof=1)
    sem = sd / np.sqrt(n) if n > 1 else np.nan
    tcrit = scistats.t.ppf(0.975, n - 1) if n > 1 else np.nan
    succ = int(d.Successes.sum())
    peaks = int(d.PeaksScored.sum())
    lo = d.loc[d.Precision.idxmin()]
    hi = d.loc[d.Precision.idxmax()]
    return {
        'Set': label,
        'N': n,
        'IDs': " ".join(str(int(i)) for i in d.ID),
        'Mean_pct': round(mean, 2),
        'SD_pct': round(sd, 2),
        'CI95_low_pct': round(mean - tcrit * sem, 2),
        'CI95_high_pct': round(mean + tcrit * sem, 2),
        'Pooled_successes': succ,
        'Pooled_peaks': peaks,
        'Pooled_pct': round(100 * succ / peaks, 2) if peaks else np.nan,
        'Min_pct': round(lo.Precision, 2),
        'Min_fraction': f"{int(lo.Successes)}/{int(lo.PeaksScored)}",
        'Min_ID': int(lo.ID),
        'Max_pct': round(hi.Precision, 2),
        'Max_fraction': f"{int(hi.Successes)}/{int(hi.PeaksScored)}",
        'Max_ID': int(hi.ID),
    }


rows = [summarise(t[t.Quality == 0], "included (Quality = 0)"),
        summarise(t, "all participants")]

summary = pd.DataFrame(rows)
out = os.path.join(path4, "PrecisionSummary.csv")
summary.to_csv(out, index=False)

for r in rows:
    print(f"\n{r['Set']}  (n = {r['N']})")
    print(f"  IDs                : {r['IDs']}")
    print(f"  mean               : {r['Mean_pct']:.2f}%  SD {r['SD_pct']:.2f}")
    print(f"  95% CI (t, df={r['N']-1:>2})  : [{r['CI95_low_pct']:.2f}, {r['CI95_high_pct']:.2f}]")
    print(f"  pooled count       : {r['Pooled_successes']}/{r['Pooled_peaks']} "
          f"= {r['Pooled_pct']:.2f}%")
    print(f"  range              : {r['Min_pct']:.2f}% ({r['Min_fraction']}, ID {r['Min_ID']})"
          f"  to  {r['Max_pct']:.2f}% ({r['Max_fraction']}, ID {r['Max_ID']})")

print("\nPer-participant fractions:")
for _, r in t.iterrows():
    mark = "" if r.Quality == 0 else "   (excluded)"
    print(f"  {int(r.ID)}  {r.Precision:5.2f}%  "
          f"{int(r.Successes):>3}/{int(r.PeaksScored):<3}  "
          f"missing {int(r.FilesMissing):>2}/{int(r.FilesTotal):<2} "
          f"= {r.MissingPct:4.1f}%{mark}")

print("\nSaved:", os.path.abspath(out))
