#Code: 10.Non-inferiorityTest.py
#Description: Non-inferiority test between the meal-based and peak-based
#             branches, plus the descriptive comparison of the two
#             distributions (Figure 5).
#Created 14th november 2023
#Author: mbaxdg6
#
# NOTE ON STATUS
# --------------
# The non-inferiority framing reported in the published article has been
# superseded. It is retained here so that the analysis behind the published
# Table 2 remains reproducible, and because the corrected pipeline no longer
# yields the published values. The replacement analysis is an agreement
# analysis at participant level; see the correction notice.
#
# Figure 5 is unaffected: it is a descriptive comparison of the two
# distributions, not part of the test.


import datetime 
import pandas as pd
import os
from datetime import datetime,timedelta
import datetime 
from matplotlib import pyplot as plt
import numpy as np
import numpy
import csv
import seaborn as sns
import matplotlib
matplotlib.rcParams.update({'font.size': 18})
from scipy.stats import ttest_ind_from_stats
import numpy as np
import globals

# --- Configurable global variable ---
id = globals.id;
path2 = globals.path2;
path3 = globals.path3;
path4 = globals.path4;
os.makedirs(path3, exist_ok=True);
os.makedirs(path4, exist_ok=True);
fileToRead1="Boxplot"+str(id);
fileToRead2="BoxplotPeak"+str(id);
fileToSave="ComparisonPeakNoPeak"+str(id);

# -----------------------------------------------------------#
# Unit conversion. Source values are in mg/dL.
# Factor lives in globals.py so every script shares one value.
# -----------------------------------------------------------#
MGDL_TO_MMOL = globals.MGDL_TO_MMOL;

# Non-inferiority margin used by the published analysis, as a fraction of
# the reference group mean.
MARGIN = 0.2;



# -----------------------------------------------------------#
#             Non-inferiority test function
# -----------------------------------------------------------#

def non_inferiority_ttest(mean1, stddev1, n1, mean2, stddev2, n2, relative_difference, equal_variance, increase_good):
    '''
    Perform a one-sided t-test with a non-inferiority threshold for two independent samples.
    mean1/2: group mean
    stddev1/2: standard deviation of each group
    n1/2: number of observations in each group
    relative_difference: threshold as a percentage of the base group (e.g. 0.1=10% difference)
    equal_variance: if False, uses Welch's t-test.
    increase_good: if True, Ho: mean2 <= mean1 - threshold. Else Ho: mean2 >= mean1 + threshold.
    Returns: 
    '''
    
    delta = relative_difference * mean1

    if increase_good:
        threshold = mean1 - delta
    else:
        threshold = mean1 + delta

    tstat, pval = ttest_ind_from_stats(mean1=threshold, 
                                       std1=stddev1, 
                                       nobs1=n1, 
                                       mean2=mean2, 
                                       std2=stddev2, 
                                       nobs2=n2, 
                                       equal_var=equal_variance)

    if increase_good:
        pvalue = 1 - pval/2.0
    else:
        pvalue = pval/2.0
    
    return tstat, pvalue


# --- df calculator ---
def welch_df(n1, n2, s1, s2):
    v1 = (s1**2) / n1
    v2 = (s2**2) / n2
    num = (v1 + v2)**2
    den = (v1**2)/(n1 - 1) + (v2**2)/(n2 - 1)
    return num / den


# -----------------------------------------------------------#
#             Read files
#
# Total_group1/2 accumulate ABSOLUTE deviations, which is the quantity the
# published method describes. The hourly loop below reports the test on the
# signed values, so it does not follow the declared method: it is printed as
# a diagnostic and deliberately not exported.
# -----------------------------------------------------------#
Total_group1=[];
Total_group2=[];
hourly_rows=[];

data1=pd.read_csv(str(path2)+str(fileToRead1)+str(0)+str("-")+str(24)+"total"+".csv");
data2=pd.read_csv(str(path2)+str(fileToRead2)+str(0)+str("-")+str(24)+"total"+".csv");

for i in range(24):
    group1=data1["["+str(i)+str("-")+str(i+1)+"]"].to_numpy();
    group2=data2["["+str(i)+str("-")+str(i+1)+"]"].to_numpy();
    group1 = group1[~numpy.isnan(group1)]
    group2 = group2[~numpy.isnan(group2)]
    for j in range(len(group1)):
        Total_group1.append(abs(group1[j]));
    for k in range(len(group2)):
        Total_group2.append(abs(group2[k]));

    label = "["+str(i)+"-"+str(i+1)+"]";
    if len(group1)>1 and len(group2)>1: 
        mean_group1 = np.mean(group1)
        mean_group2 = np.mean(group2)
        stddev_group1 = np.std(group1, ddof=1)
        stddev_group2 = np.std(group2, ddof=1)
        tstat_h, pval_h = non_inferiority_ttest(mean1=mean_group1,
                                        stddev1=stddev_group1, 
                                        n1=len(group1), 
                                        mean2=mean_group2, 
                                        stddev2=stddev_group2, 
                                        n2=len(group2), 
                                        relative_difference=MARGIN, 
                                        equal_variance=False, 
                                        increase_good=False)
        df_h = welch_df(len(group1), len(group2), stddev_group1, stddev_group2);
        print('One sided ttest '+label+': t value = {:.4f}, pval = {:.5f}'.format(tstat_h, pval_h));
        hourly_rows.append({'Hour': label, 'n_meal': len(group1), 'n_peak': len(group2),
                            'mean_meal': mean_group1, 'mean_peak': mean_group2,
                            't': tstat_h, 'df_welch': df_h, 'p': pval_h});
    else:
       print('One sided ttest '+label+': t value = N/A, pval = N/A');
       hourly_rows.append({'Hour': label, 'n_meal': len(group1), 'n_peak': len(group2),
                           'mean_meal': np.nan, 'mean_peak': np.nan,
                           't': np.nan, 'df_welch': np.nan, 'p': np.nan});


# -----------------------------------------------------------#
#             Total  ->  the row this participant contributes
#                        to the published Table 2
# -----------------------------------------------------------#
mean_total_group1 = np.mean(Total_group1)
mean_total_group2 = np.mean(Total_group2)
stddev_total_group1 = np.std(Total_group1, ddof=1)
stddev_total_group2 = np.std(Total_group2, ddof=1)
tstat, pval = non_inferiority_ttest(mean1=mean_total_group1,
                                    stddev1=stddev_total_group1, 
                                    n1=len(Total_group1), 
                                    mean2=mean_total_group2, 
                                    stddev2=stddev_total_group2, 
                                    n2=len(Total_group2), 
                                    relative_difference=MARGIN, 
                                    equal_variance=False, 
                                    increase_good=False)

df_welch  = welch_df(len(Total_group1), len(Total_group2),
                     stddev_total_group1, stddev_total_group2)
df_pooled = len(Total_group1) + len(Total_group2) - 2

def p_to_str(p):  # JMIR compact
    return "P<.001" if p < 0.001 else f"P=.{int(round(p*1000)):03d}"

print('One sided ttest Total 1 vs Total 2: t value = {:.5f}, pval = {:.5f}'.format(tstat, pval))
print('One sided ttest Total 1 vs Total 2 (Welch df={}): t value = {:.5f}, pval = {:.5f}'
      .format(int(round(df_welch)), tstat, pval))
print('JMIR (one-sided): t({})={:.3f}, {}'
      .format(int(round(df_welch)), tstat, p_to_str(pval)))
print("Mean, meal branch:", mean_total_group1)
print("Mean, peak branch:", mean_total_group2)

# -----------------------------------------------------------#
# Export. The published Table 2 is one row per participant, taken from the
# Total comparison. Each run replaces its own row in a single file, so the
# whole cohort ends up in one table rather than twelve.
# -----------------------------------------------------------#
row = pd.DataFrame({'ID': [id],
                    'n_meal': [len(Total_group1)],
                    'n_peak': [len(Total_group2)],
                    'mean_meal_mgdL': [mean_total_group1],
                    'mean_peak_mgdL': [mean_total_group2],
                    'sd_meal_mgdL': [stddev_total_group1],
                    'sd_peak_mgdL': [stddev_total_group2],
                    'margin': [MARGIN],
                    't': [tstat],
                    'df_welch': [df_welch],
                    'df_pooled': [df_pooled],
                    'p_onesided': [pval],
                    'meets_criterion': [int(pval < 0.05)]});

out_table = path4 + "Table2_NonInferiority.csv";
if os.path.isfile(out_table):
    table = pd.read_csv(out_table);
    table = table[table['ID'] != id];
    table = pd.concat([table, row], ignore_index=True);
else:
    table = row;
table = table.sort_values('ID').reset_index(drop=True);
table.to_csv(out_table, index=False);
print("Saved:", os.path.abspath(out_table));

# -----------------------------------------------------------#
# Figure 5 — descriptive comparison of the two distributions.
# Unaffected by the status of the test above.
# -----------------------------------------------------------#
data = [Total_group1, Total_group2]

fig, ax = plt.subplots(figsize=(8, 6))
boxplot = ax.boxplot(data, patch_artist=True, showmeans=True)

# Customize box appearance
colors = ['#87CEEB', '#FFCCCB']  # Light blue and light pink colors for each box
for patch, color in zip(boxplot['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_edgecolor('black')

# Customize whiskers, caps, and medians
for whisker in boxplot['whiskers']:
    whisker.set(color='black', linewidth=1.5, linestyle='--')

for cap in boxplot['caps']:
    cap.set(color='black', linewidth=1.5)

for median in boxplot['medians']:
    median.set(color='red', linewidth=2)

# Customize the mean point
for mean in boxplot['means']:
    mean.set(marker='o', markerfacecolor='black', markeredgecolor='black', markersize=7)

# Customize x-axis labels
plt.xticks([1, 2], ['With meal data', 'Without meal data'], fontsize=12)
plt.xlabel('Comparison of approaches with versus without meal data', fontsize=14)
plt.ylabel('BG relative change (mg/dL)', fontsize=14)
if globals.FIGURE_TITLES:
    plt.title(f'Cumulative deviation of blood glucose: {id}', fontsize=16)

# Add grid and adjust its appearance
plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

# Customize y-ticks for both mg/dL and mmol/L
def mg_dL_to_mmol(y):
    return y * MGDL_TO_MMOL

secax = ax.secondary_yaxis('right',
                           functions=(mg_dL_to_mmol, lambda y: y / MGDL_TO_MMOL))
secax.set_ylabel("BG relative change (mmol/L)", fontsize=14)
secax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}'))

# Add minor ticks for y-axis
ax.yaxis.set_minor_locator(plt.MultipleLocator(5))
ax.tick_params(axis='both', which='major', labelsize=12)

plt.tight_layout()

# Only the worked example used in the article is written. The panel is built
# for every participant because the test above runs for all of them, but the
# other panels are not part of the record.
if id == globals.idG:
    out = path3 + 'Figure5.png';
    plt.savefig(out, dpi=300, bbox_inches='tight');
    print("Saved:", os.path.abspath(out));
plt.close(fig);
