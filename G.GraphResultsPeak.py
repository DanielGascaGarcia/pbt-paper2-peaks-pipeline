#Code: G.GraphResultsPeak.py
#Description: Cross-participant results for the peak branch.
#Created 3rd August 2023
#Author: mbaxdg6

import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime,timedelta
import datetime 
matplotlib.rcParams.update({'font.size': 12});
import seaborn as sns
import numpy 
import numpy as np
from scipy import stats as scistats
import os
import globals

path2=globals.path2;
path3=globals.path3;
os.makedirs(path3, exist_ok=True);
path4=globals.path4;
os.makedirs(path4, exist_ok=True);

# -----------------------------------------------------------#
# Unit conversion. Source values are in mg/dL.
# Factor lives in globals.py so every script shares one value.
# -----------------------------------------------------------#
MGDL_TO_MMOL = globals.MGDL_TO_MMOL;

# -----------------------------------------------------------#
# Figure titles. Journals put the title in the caption, not in
# the image, so this is off for the submitted figures.
# -----------------------------------------------------------#
def figTitle(text):
    if globals.FIGURE_TITLES:
        plt.title(text);

Complete=pd.DataFrame();
CompleteBP=pd.DataFrame();


for id in globals.ids:
   fileToRead="ComparisonJoinedPeakNoActivity"+str(id);
   fileToSave="ComparisonSampledPeakNoActivity"+str(id);

   # -----------------------------------------------------------#
   # Conversion to arrays
   # -----------------------------------------------------------#
   data = pd.read_csv(str(path2)+str(fileToRead)+".csv");
   Key=data["Key"].to_numpy();
   MedRelChange=data["MedRelChange"].to_numpy();
   Reliability=data["Flag"].to_numpy();

   T_MedRelChange=[];
   T_Reliability=[];
   Flag_pos=[];
   Flag_R=[];
   ID=[];
   # Sampling
   for i in range(len(Key)):
      (h, m, s) = Key[i].split(':');
      result = (int(h) * 3600 + int(m) * 60 + int(s))/3600;
      if i % int(60) ==True:
         if numpy.isnan(MedRelChange[i])==True:
            T_Reliability.append(np.nan);
         else:
            T_Reliability.append(Reliability[i]);
         T_MedRelChange.append(MedRelChange[i]);
         ID.append(id);

         if MedRelChange[i]>0:
            Flag_pos.append("1. Too little insulin");
         elif MedRelChange[i]<0:
            Flag_pos.append("2. Too much insulin");
         elif MedRelChange[i]==0:
            Flag_pos.append("3. Optimal")
         else:
            Flag_pos.append("4. Missing")

         if  Reliability[i]==3:
             Flag_R.append("high");
         elif  Reliability[i]==2:
             Flag_R.append("Medium");
         elif  Reliability[i]==1:
            Flag_R.append("Low")
         else:
            Flag_R.append(np.nan)


   dt = datetime.datetime(2010, 12, 1);
   end = datetime.datetime(2010, 12, 1, 23, 59, 59);
   step = datetime.timedelta(minutes=1);
   positive_array=[];
   for i in range(len(T_MedRelChange)):
     positive_array.append(abs(T_MedRelChange[i]));
   # -----------------------------------------------------------#
   #                           Sample
   # -----------------------------------------------------------#
   Sample=pd.DataFrame();
   medTime=[];
   j=0;
   while dt < end:
         if j%60==0:
               medTime.append(dt.strftime('%H:%M:%S'));
         j=j+1;
         dt += step;
   Sample['ID']=ID;
   Sample['Time']=medTime;
   Sample['MedRelChange']=[i for i in T_MedRelChange];
   Sample['UMedRelChange']=[i for i in positive_array];
   Sample['Flag']=T_Reliability;
   Sample['Category']=Flag_pos;
   Sample['FlagR']=Flag_R;

   Sample.to_csv(str(path2)+str(fileToSave)+".csv",index=False);

   temp_df1 =  Sample[(Sample['Category'] =='1. Too little insulin') ]
   temp_df2 =  Sample[(Sample['Category'] =='2. Too much insulin') ]

   temp_df=pd.concat([temp_df1, temp_df2], ignore_index=True, axis=0);
   temp_df.to_csv(str(path2)+str(fileToSave)+"Clean.csv",index=False);

   CompleteBP=pd.concat([CompleteBP, temp_df], ignore_index=True, axis=0);
   Complete=pd.concat([Complete, Sample], ignore_index=True, axis=0);

# -----------------------------------------------------------#
# All results
#
# sort_values returns a new frame; assigning it is what makes the
# saved files ordered by participant.
# -----------------------------------------------------------#
CompleteBP = CompleteBP.sort_values(by=['ID']).reset_index(drop=True);
CompleteBP.to_csv(str(path2)+"CompleteBP"+".csv",index=False);
Complete = Complete.sort_values(by=['ID']).reset_index(drop=True);
Complete.to_csv(str(path2)+"Complete"+".csv",index=False);

# -----------------------------------------------------------#
# Statistics (mg/dL and mmol/L)
# -----------------------------------------------------------#
median_umedrelchange = Complete['UMedRelChange'].median();
df_median = pd.DataFrame({
    'MedianUMedRelChange_mgdL':  [median_umedrelchange],
    'MedianUMedRelChange_mmolL': [median_umedrelchange * MGDL_TO_MMOL],
});
df_median.to_csv(f"{path2}MedianUMedRelChange.csv", index=False);

df_sum = Complete.groupby('ID', as_index=False)['UMedRelChange'].sum();
df_sum = df_sum.rename(columns={'UMedRelChange': 'UMedRelChange_mgdL'});
df_sum['UMedRelChange_mmolL'] = df_sum['UMedRelChange_mgdL'] * MGDL_TO_MMOL;
df_sum.to_csv(f"{path2}SumUMedRelChange.csv", index=False);
print(df_sum);

n_ids      = len(df_sum);
mean_value = df_sum['UMedRelChange_mgdL'].mean();
sd_value   = df_sum['UMedRelChange_mgdL'].std();
sem        = sd_value / np.sqrt(n_ids) if n_ids > 1 else np.nan;
tcrit      = scistats.t.ppf(0.975, n_ids - 1) if n_ids > 1 else np.nan;
ci_low     = mean_value - tcrit * sem;
ci_high    = mean_value + tcrit * sem;
peak_row   = df_sum.loc[df_sum['UMedRelChange_mgdL'].idxmax()];
peak_value = peak_row['UMedRelChange_mgdL'];
peak_id    = int(peak_row['ID']);

print(f"Mean = {mean_value:.2f} mg/dL ({mean_value*MGDL_TO_MMOL:.3f} mmol/L), "
      f"SD = {sd_value:.2f} mg/dL ({sd_value*MGDL_TO_MMOL:.3f} mmol/L)");
print(f"95% CI = {ci_low:.2f} to {ci_high:.2f} mg/dL");
print(f"Peak = {peak_value:.2f} mg/dL, participant {peak_id}");

# -----------------------------------------------------------#
# Save summary statistics
# -----------------------------------------------------------#
df_sum.to_csv(path4 + "SumUMedRelChange_byID.csv", index=False);

stats = pd.DataFrame({
    'Statistic':           ['Mean', 'SD', 'CI95 low', 'CI95 high', 'Peak', 'N'],
    'UMedRelChange_mgdL':  [mean_value, sd_value, ci_low, ci_high, peak_value, n_ids],
    'UMedRelChange_mmolL': [mean_value * MGDL_TO_MMOL, sd_value * MGDL_TO_MMOL,
                            ci_low * MGDL_TO_MMOL, ci_high * MGDL_TO_MMOL,
                            peak_value * MGDL_TO_MMOL, np.nan],
    'Note':                ['', '', '', '', f"participant {peak_id}", ''],
});
stats.to_csv(path4 + "SummaryStats_UMedRelChange.csv", index=False);
print("Saved:", os.path.abspath(path4 + "SumUMedRelChange_byID.csv"));
print("Saved:", os.path.abspath(path4 + "SummaryStats_UMedRelChange.csv"));
# -----------------------------------------------------------#
# Locate the extreme outliers of the boxplot
# -----------------------------------------------------------#
max_val = CompleteBP['MedRelChange'].max();
min_val = CompleteBP['MedRelChange'].min();
print("Max:", max_val, " Min:", min_val);

pd.DataFrame({
    'Statistic':          ['Max', 'Min'],
    'MedRelChange_mgdL':  [max_val, min_val],
    'MedRelChange_mmolL': [max_val * MGDL_TO_MMOL, min_val * MGDL_TO_MMOL],
}).to_csv(path4 + "MedRelChange_extremes.csv", index=False);
print("SAVED:", os.path.abspath(path4 + "MedRelChange_extremes.csv"));
# -----------------------------------------------------------#
# Box plot of relative changes by kind of insulin problem  -> Figure 8
# -----------------------------------------------------------#
plt.figure(figsize=(12, 8));
sns.boxplot(y ='MedRelChange',
              x ='ID',data=CompleteBP,  hue = CompleteBP['Category'], width=0.4,
              palette='pastel');

# -----------------------------------------------------------#
# Display the box plots
# -----------------------------------------------------------#
ax8 = plt.gca();
ax8.set_ylabel("Blood glucose relative change (mg/dL)");
plt.xlabel("Patient ID");
plt.grid(which='major', color='#DDDDDD', linewidth=0.8);
plt.grid(which='minor', color='#DDDDDD', linestyle=':', linewidth=0.5);
plt.axhline(linewidth=2, color='Black');
figTitle("Blood glucose relative change distribution in all individuals");
plt.legend(title='Insulin condition', loc='upper right');

# Secondary axis in mmol/L. Rescale only: the data is drawn once on ax8.
ax8b = ax8.twinx();
ax8b.set_ylim([v * MGDL_TO_MMOL for v in ax8.get_ylim()]);
ax8b.set_ylabel("Blood glucose relative change (mmol/L)");
ax8b.grid(False);

plt.savefig(path3 + 'Figure8.png', dpi=300, bbox_inches='tight');
print("Saved:", os.path.abspath(path3 + 'Figure8.png'));
plt.close();
# -----------------------------------------------------------#
# Histogram of relative changes by kind of insulin problem  -> Figure 7
# -----------------------------------------------------------#
df_gb = Complete.groupby(["ID","Category"]).size().unstack(level=1)

# -----------------------------------------------------------#
# Values quoted in the Figure 7 caption
# -----------------------------------------------------------#
counts = Complete['Category'].value_counts();
n_participants = Complete['ID'].nunique();
n_total = len(Complete);                    # 24 h x participants

n_low  = counts.get('1. Too little insulin', 0);
n_high = counts.get('2. Too much insulin', 0);
n_opt  = counts.get('3. Optimal', 0);
n_miss = counts.get('4. Missing', 0);

pct_all    = 100 * (n_low + n_high) / n_total;
pct_scored = 100 * (n_low + n_high) / (n_total - n_miss);
opt_hours_per_day = n_opt / n_participants;

# Participant-level version of the off-target proportion. Each participant
# contributes one value, computed over their own 24 hours, so the interval
# below is a t interval on n-1 degrees of freedom rather than a binomial
# interval over pooled hourly intervals. The pooled percentage is reported
# alongside it as a plain count.
per_id = Complete.groupby('ID')['Category'].apply(
    lambda s: 100 * s.isin(['1. Too little insulin',
                            '2. Too much insulin']).sum() / len(s));
pct_sd = per_id.std();
pct_mean = per_id.mean();
n_pid = len(per_id);
sem_pid = pct_sd / np.sqrt(n_pid) if n_pid > 1 else np.nan;
t_pid = scistats.t.ppf(0.975, n_pid - 1) if n_pid > 1 else np.nan;
# The upper limit is written as computed, not capped. Eleven of the twelve
# participants sit at 100% and the twelfth at 95.8%, so the interval extends
# above the maximum a proportion can take. That is why no interval is reported
# for this quantity in the article; the value is kept here so the deposited
# tables show what was computed rather than a truncated substitute.
ci_pid_low = pct_mean - t_pid * sem_pid;
ci_pid_high = pct_mean + t_pid * sem_pid;

caption = pd.DataFrame({
    'Metric': ['Participants', 'Hours (24 x n)',
               'Too little insulin', 'Too much insulin', 'Optimal', 'Missing',
               'Off-target %, pooled count', 'Off-target %, excl. missing',
               'Off-target %, mean across participants',
               'Off-target % SD between participants',
               'Off-target % CI95 low (t)',
               'Off-target % CI95 high (t, exceeds 100 - not reported)',
               'Optimal hours per participant'],
    'Value': [n_participants, n_total,
              n_low, n_high, n_opt, n_miss,
              round(pct_all, 2), round(pct_scored, 2),
              round(pct_mean, 2),
              round(pct_sd, 2),
              round(ci_pid_low, 2), round(ci_pid_high, 2),
              round(opt_hours_per_day, 3)],
});
caption.to_csv(path4 + "Figure7_key_values.csv", index=False);
print(caption.to_string(index=False));

df_gb.plot(kind = 'bar', figsize=(12, 8), edgecolor='black')
# -----------------------------------------------------------#
# Display the bar chart
# -----------------------------------------------------------#
plt.xlabel("Patient ID");
plt.grid(which='major', color='#DDDDDD', linewidth=1);
plt.yticks([0,2,4,6,8,10,12,14,16,18,20,22,24])
plt.ylabel("Count");
figTitle("Histogram of category levels of blood glucose relative changes");
plt.savefig(path3 + 'Figure7.png', dpi=300, bbox_inches='tight');
print("Saved:", os.path.abspath(path3 + 'Figure7.png'));
plt.close();
df_gb.to_csv(path4 + "Figure7_data.csv");
print("Saved:", os.path.abspath(path4 + "Figure7_data.csv"));