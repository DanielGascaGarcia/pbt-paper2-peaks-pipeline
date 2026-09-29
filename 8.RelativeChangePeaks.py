"""
8.RelativeChangePeaks.py
Step 8 (peak-based branch): hourly relative change of glucose, per day.

Created: 14 November 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    Same calculation as 8.RelativeChange.py in the meal-based branch:
    Part 1: in every hourly file and for every day, subtracts the first valid
            glucose value of that hour from all values of that hour.
    Part 2: keeps, for every day and hour, the LAST valid value of that
            relative series = last valid minus first valid value in the hour.

Inputs
    globals.id, globals.path2
    <path2>/BGHourPeak<id><i>To<i+1>.csv   for i = 0 ... 23   (7.SplitHoursPeaks.py)
    Columns: Unnamed: 0, Key, BGValue0 ... (not interpolated at hour level)

Outputs
    <path2>/BGHourRelativeChangePeak<id><i>To<i+1>.csv
        Columns: Key, RChBGValue0, RChBGValue1, ... (one per day), mg/dL
    <path2>/BGHourRelativeChangePeak<id><i>To<i+1>lastValues.csv
        One column, Last_values, one row per day. Days with no data in that
        hour get a single space " ".

Notes
    - Column counts: the hourly files have two non-data columns (Unnamed: 0
      and Key), hence "-2" in Part 1; the relative-change files have one
      (Key), hence "-1" in Part 2. Both are correct.
    - DIFFERENCE from the meal-based branch: an empty day is written as " "
      (a space) instead of "". pd.read_csv skips a line that holds only a
      space, so when the lastValues file is read back the rows after an empty
      day move up one position and row j is no longer day j. The values and
      their number per hour are unchanged, only their positions. The reader
      (9.BoxplotPeak.py) has to use skip_blank_lines=False and convert the
      column with pd.to_numeric to keep the rows aligned with the days.
"""


import datetime 
import pandas as pd
import os
from datetime import datetime,timedelta
import datetime 
from matplotlib import pyplot as plt
import numpy as np
import csv
pd.options.mode.chained_assignment = None  # default='warn'
import globals

# --- Configurable global variables (set in globals.py) ---
id = globals.id;
path2 = globals.path2;
fileToRead="BGHourPeak"+str(id);
fileToSave="BGHourRelativeChangePeak"+str(id);
# -----------------------------------------------------------#
#             Substract the staring point
# -----------------------------------------------------------#

dmean = pd.DataFrame();
# Part 1: subtract the first valid value of the hour, day by day.
for i in range(24):
    data = pd.read_csv(str(path2)+str(fileToRead)+str(i)+str("To")+str(i+1)+".csv"); 
    # print(len(data.columns));
    dt = pd.DataFrame();
    dt=data[['Key']];
    # Hourly files: Unnamed: 0 + Key + one column per day -> "-2".
    for j in range(len(data.columns)-2):
    #    dt1=data['BGValue'+str(j)].diff().to_frame(name='DBGValue'+str(j));
        # serie = data['BGValue'+str(j)].to_frame(name='RChBGValue'+str(j)).div(18.0182).squeeze();
        serie = data['BGValue'+str(j)].to_frame(name='RChBGValue'+str(j)).squeeze();
        try:
            first_val=serie.loc[serie.first_valid_index()];
            dt1=data['BGValue'+str(j)].to_frame(name='RChBGValue'+str(j))-first_val;
            # dt1=data['BGValue'+str(j)].to_frame(name='RChBGValue'+str(j)).div(18.0182)-first_val;
            # print(data['BGValue'+str(j)].to_frame(name='DBGValue'+str(j)).div(18.0182)-first_val);
        except:
            dt1=data['BGValue'+str(j)].to_frame(name='RChBGValue'+str(j));
            # dt1=data['BGValue'+str(j)].to_frame(name='RChBGValue'+str(j)).div(18.0182);
            # print("Variable missing");
        dt['RChBGValue'+str(j)] = dt1['RChBGValue'+str(j)].copy();
    dt.to_csv(str(path2)+str(fileToSave)+str(i)+str("To")+str(i+1)+".csv",index=False);


# -----------------------------------------------------------#
#             Obtaining the last point.
# -----------------------------------------------------------#

# Part 2: last valid value of each day = relative change over the hour.
for i in range(24):
    data = pd.read_csv(str(path2)+str(fileToSave)+str(i)+str("To")+str(i+1)+".csv"); 
    dt=[];
    # Relative-change files: Key + one column per day -> "-1".
    for j in range(len(data.columns)-1):
        try:
            serie = data['RChBGValue'+str(j)].to_frame(name='RChBGLValue'+str(j)).squeeze();
            last_val=serie.loc[serie.last_valid_index()];
            print(last_val);
            dt1=last_val;
        except:
            # print("No key");
            # Written as a space; see the header note on reading it back.
            dt1=" ";
        dt.append(dt1); 
    dt=pd.DataFrame(dt, columns=['Last_values'])  
    dt.to_csv(str(path2)+str(fileToSave)+str(i)+str("To")+str(i+1)+"lastValues"+".csv",index=False);

    print(dt); 




