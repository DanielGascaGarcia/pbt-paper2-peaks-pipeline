"""
10.PivotGeneratormediansPeak.py   (header of the original file reads "Computation of relative changes")
Step 10 (peak-based branch): hourly median relative change and reliability
flag, spread over a minute-by-minute day.

Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    Same as 10.PivotGeneratormedians.py in the meal-based branch, on the
    peak-based table:
    1. Median relative change of each hour over the days with data
       (MedRelChange).
    2. Reliability flag of each hour from the number of days with data, using
       the 50th and 70th percentiles of the 24 counts:
       1 = below P50 (low), 2 = from P50 up to P70 (medium), 3 = at or above
       P70 (high).
    3. Both values written for every minute of the day (each hour repeated
       60 times).

Inputs
    globals.id, globals.path2
    <path2>/BoxplotPeak<id>0-24total.csv   (9.BoxplotPeak.py)

Outputs
    <path2>/BGHourRelativeChangePeak<id>0To24medians.csv      (no header, intermediate)
    <path2>/BGHourRelativeChangePeak<id>0To24medians_wCN.csv
        Columns: Key (HH:MM:SS, 1,440 rows), MedRelChange (mg/dL), Flag

Notes
    - The medians and the counts per hour do not depend on the order of the
      rows, so they are not affected by the row shift described in
      8.RelativeChangePeaks.py.
    - Medians are read from the median lines of a matplotlib box plot; same
      value as the column median over non-empty cells.
    - values[i] reads the counts by position from a Series with text labels;
      pandas 2.2.2 accepts this with a FutureWarning (hidden by the filter),
      newer pandas would fail.
"""

import warnings
import datetime 
import pandas as pd
import os
from datetime import datetime,timedelta
import datetime 
from matplotlib import pyplot as plt
import numpy as np
import csv
import seaborn as sns
warnings.simplefilter(action='ignore', category=FutureWarning)
import globals

# --- Configurable global variables (set in globals.py) ---
id = globals.id;
path2 = globals.path2;
fileToRead="BoxplotPeak"+str(id);
fileToSave="BGHourRelativeChangePeak"+str(id);
# -----------------------------------------------------------#
dt = datetime.datetime(2010, 12, 1);
end = datetime.datetime(2010, 12, 1, 23, 59, 59);
step = datetime.timedelta(minutes=1);
secArray=[];
medians_a=[];
Flag_a=[];
# -----------------------------------------------------------#
# Open file and obtain medians
# -----------------------------------------------------------#
# Table of hourly relative changes: one column per hour, one row per day.
total=pd.read_csv(str(path2)+str(fileToRead)+str(0)+str("-")+str(24)+"total"+".csv");
# Draw a box plot only to read its median lines: medians[i][0] = median of hour i.
_, bp = pd.DataFrame.boxplot(total, return_type='both');
medians = [median.get_ydata() for median in bp["medians"]];
# -----------------------------------------------------------#
# Obtain statistics of the number of lectures per hour
# -----------------------------------------------------------#
values=pd.DataFrame();       
# Number of days with data in each hour (non-empty cells per column).
values=total.count(axis='rows');
# Reliability thresholds: 50th and 70th percentiles of the 24 counts.
low_b=np.percentile(values, 50);
upper_b=np.percentile(values, 70);
Flag=[]

# Flag per hour: 1 = low, 2 = medium, 3 = high reliability.
for i in range(len(values)):
 if values[i]<low_b:
    Flag.append(1);
 elif values[i]>=upper_b:
    Flag.append(3);
 else:
    Flag.append(2);
print(Flag);

# -----------------------------------------------------------#
# Obtain the pivot and variables needed to graph
# -----------------------------------------------------------#
open(str(path2)+str(fileToSave)+str("0To24")+"medians"+".csv", 'w').close();
i=0;
j=1;
# Spread the 24 hourly values over 1,440 minutes.
while dt < end:
        secArray.append(dt.strftime('%H:%M:%S'));
        medians_a.append(medians[i][0]);
        Flag_a.append(Flag[i]);
        # print(i);
        dt += step;
        if j%60==0:
              i=i+1;
        j=j+1;
# -----------------------------------------------------------#
# Write Key, median and flag (no header), then add the header below.
for j in range(len(secArray)):
        file = open(str(path2)+str(fileToSave)+str("0To24")+"medians"+".csv", 'a');
        file.write(str(secArray[j])+","+str(medians_a[j])+","+str(Flag_a[j]));
        file.write('\n');
        file.close();
# -----------------------------------------------------------#
df = pd.read_csv(str(path2)+str(fileToSave)+str("0To24")+"medians"+".csv",  header=None);
df.rename(columns={0: 'Key',1:'MedRelChange',2:'Flag'}, inplace=True);
df.to_csv(str(path2)+str(fileToSave)+str("0To24")+"medians"+"_wCN"+".csv", index=False); # save to new csv 
