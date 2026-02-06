#Code: 10.Non-inferiorityTest.py
#Description: Run of non-interiority test.
#Created 14th november 2023
#Author: mbaxdg6


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

# -----------------------------------------------------------#
#              Configurable variables 
# -----------------------------------------------------------#
id = globals.id;
path2 = globals.path2;
fileToRead1="Boxplot"+str(id);
fileToRead2="BoxplotPeak"+str(id);
fileToSave="ComparisonPeakNoPeak"+str(id);


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




# -----------------------------------------------------------#
#             Read files
# -----------------------------------------------------------#
Total_group1=[];
Total_group2=[];


for i in range(24):
    data1=pd.read_csv(str(path2)+str(fileToRead1)+str(0)+str("-")+str(24)+"total"+".csv");
    data2=pd.read_csv(str(path2)+str(fileToRead2)+str(0)+str("-")+str(24)+"total"+".csv");
    group1=data1["["+str(i)+str("-")+str(i+1)+"]"].to_numpy();
    group2=data2["["+str(i)+str("-")+str(i+1)+"]"].to_numpy();
    group1 = group1[~numpy.isnan(group1)]
    group2 = group2[~numpy.isnan(group2)]
    for j in range(len(group1)):
        Total_group1.append(abs(group1[j]));
    for k in range(len(group2)):
        Total_group2.append(abs(group2[k]));

    if len(group1)>1 and len(group2)>1: 
        mean_group1 = np.mean(group1)
        mean_group2 = np.mean(group2)
        stddev_group1 = np.std(group1, ddof=1)
        stddev_group2 = np.std(group2, ddof=1)
        relative_difference_threshold = 0.2
        tstat, pval = non_inferiority_ttest(mean1=mean_group1,
                                        stddev1=stddev_group1, 
                                        n1=len(group1), 
                                        mean2=mean_group2, 
                                        stddev2=stddev_group2, 
                                        n2=len(group2), 
                                        relative_difference=relative_difference_threshold, 
                                        equal_variance=False, 
                                        increase_good=False)
        print('One sided ttest ['+str(i)+str("-")+str(i+1)+']: t value = {:.4f}, pval = {:.5f}'.format(tstat, pval));
    else:
       print('One sided ttest ['+str(i)+str("-")+str(i+1)+']: t value = N/A, pval = N/A'); 


# -----------------------------------------------------------#
#             Total
# -----------------------------------------------------------#
# print(Total_group1)
# print("\n")
# print(Total_group2)
# print("\n")

mean_total_group1 = np.mean(Total_group1)
mean_total_group2 = np.mean(Total_group2)
stddev_total_group1 = np.std(Total_group1, ddof=1)
stddev_total_group2 = np.std(Total_group2, ddof=1)
relative_difference_threshold = 0.2
tstat, pval = non_inferiority_ttest(mean1=mean_total_group1,
                                    stddev1=stddev_total_group1, 
                                    n1=len(Total_group1), 
                                    mean2=mean_total_group2, 
                                    stddev2=stddev_total_group2, 
                                    n2=len(Total_group2), 
                                    relative_difference=relative_difference_threshold, 
                                    equal_variance=False, 
                                    increase_good=False)
print('One sided ttest Total 1 vs Total 2: t value = {:.5f}, pval = {:.5f}'.format(tstat, pval));

# Example data for testing (replace with your data)
print(mean_total_group1)
print(mean_total_group2)
data = [Total_group1, Total_group2]
# -----------------------------------------------------------#
#                        df calculators 
# -----------------------------------------------------------#
#        This code is for jmir requieremnts of df
# -----------------------------------------------------------#

def welch_df(n1, n2, s1, s2):
    v1 = (s1**2) / n1
    v2 = (s2**2) / n2
    num = (v1 + v2)**2
    den = (v1**2)/(n1 - 1) + (v2**2)/(n2 - 1)
    return num / den

df_welch  = welch_df(len(Total_group1), len(Total_group2),
                     stddev_total_group1, stddev_total_group2)
df_pooled = len(Total_group1) + len(Total_group2) - 2  # if you need it


print('One sided ttest Total 1 vs Total 2: t value = {:.5f}, pval = {:.5f}'.format(tstat, pval))
print('One sided ttest Total 1 vs Total 2 (Welch df={}): t value = {:.5f}, pval = {:.5f}'
      .format(int(round(df_welch)), tstat, pval))

def p_to_str(p): 
    return "P<.001" if p < 0.001 else f"P=.{int(round(p*1000)):03d}"

print('JMIR (one-sided): t({})={:.3f}, {}'
      .format(int(round(df_welch)), tstat, p_to_str(pval)))
# -----------------------------------------------------------#
#                    Create boxplot
# -----------------------------------------------------------#
fig, ax = plt.subplots(figsize=(8, 6))  
boxplot = ax.boxplot(data, patch_artist=True, showmeans=True)


colors = ['#87CEEB', '#FFCCCB']  
for patch, color in zip(boxplot['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_edgecolor('black')


for whisker in boxplot['whiskers']:
    whisker.set(color='black', linewidth=1.5, linestyle='--')

for cap in boxplot['caps']:
    cap.set(color='black', linewidth=1.5)

for median in boxplot['medians']:
    median.set(color='red', linewidth=2)


for mean in boxplot['means']:
    mean.set(marker='o', markerfacecolor='black', markeredgecolor='black', markersize=7)


plt.xticks([1, 2], ['With  Meal Data', 'Without  Meal Data'], fontsize=12)
plt.xlabel('Comparison of Approaches with vs Without Meal Data', fontsize=14)

plt.ylabel('BG Relative Change (mg/dL)', fontsize=14)
plt.title(f'Cumulative Deviation of Blood Glucose: {id}', fontsize=16)


plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)


def mg_dL_to_mmol(y):
    return y * 0.0555

secax = ax.secondary_yaxis('right', functions=(mg_dL_to_mmol, lambda y: y / 0.0555))
secax.set_ylabel("BG Relative Change (mmol/L)", fontsize=14)
secax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}'))

ax.yaxis.set_minor_locator(plt.MultipleLocator(5))
ax.tick_params(axis='both', which='major', labelsize=12)


plt.tight_layout()
plt.show()


