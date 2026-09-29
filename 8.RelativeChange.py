"""
8.RelativeChange.py
Step 8 (meal-based branch): hourly relative change of glucose, per day.

Created: 19 April 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    Part 1: in every hourly file and for every day, subtracts the first valid
            glucose value of that hour from all values of that hour, so each
            day starts the hour at 0 mg/dL.
    Part 2: keeps, for every day and hour, the LAST valid value of that
            relative series. This is the hourly relative change used in the
            box plots (the relative change algorithm of the papers): last valid value minus first
            valid value inside the hour.

Inputs
    globals.id, globals.path2
    <path2>/BGHourInterpolated<id><i>To<i+1>.csv   for i = 0 ... 23
    (7.InterpolationBGHourly.py; columns Unnamed: 0, Key, BGValue0 ...)

Outputs
    <path2>/BGHourRelativeChange<id><i>To<i+1>.csv
        Columns: Key, RChBGValue0, RChBGValue1, ... (one per day), in mg/dL.
    <path2>/BGHourRelativeChange<id><i>To<i+1>lastValues.csv
        One column, Last_values, one row per day (same order as the day
        columns). Days with no data in that hour get an empty cell.

Notes
    - The change is measured between the first and last VALID values of the
      hour, not always between minute 0 and minute 59. If part of the hour
      was removed around a meal, the change covers only the part that is
      left, so different days can span different lengths of time.
    - Column counts: the interpolated files have two non-data columns
      (Unnamed: 0 and Key), hence "-2" in Part 1; the relative-change files
      have one (Key), hence "-1" in Part 2.
    - Empty cells in lastValues are written as "" and pandas writes a lone
      empty string as a quoted "" line. When 9.Boxplot.py reads the file
      back, that line becomes NaN and is NOT skipped, so row j still belongs
      to day j.
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
id=globals.id;
path2=globals.path2;
fileToRead="BGHourInterpolated"+str(id);
fileToSave="BGHourRelativeChange"+str(id);
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
    # Interpolated files: Unnamed: 0 + Key + one column per day -> "-2".
    for j in range(len(data.columns)-2):
    #    dt1=data['BGValue'+str(j)].diff().to_frame(name='DBGValue'+str(j));
        # serie = data['BGValue'+str(j)].to_frame(name='RChBGValue'+str(j)).div(18.0182).squeeze();
        serie = data['BGValue'+str(j)].to_frame(name='RChBGValue'+str(j)).squeeze();
        # A day with no data in this hour has no first valid index; the
        # except keeps the column as it is (all empty).
        try:
            first_val=serie.loc[serie.first_valid_index()];
            dt1=data['BGValue'+str(j)].to_frame(name='RChBGValue'+str(j))-first_val;
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
    # print(data)
    dt=[];
    # The comment above is from the original code. This file has one
    # non-data column (Key), so "-1" gives exactly one value per day.
    #2 for Ohio Dataset, 1 for Simglucose
    for j in range(len(data.columns)-1):
        # print(j)
        try:
            serie = data['RChBGValue'+str(j)].to_frame(name='RChBGLValue'+str(j)).squeeze();
            last_val=serie.loc[serie.last_valid_index()];
            # print(last_val);
            dt1=last_val;
        except:
            # print("No key");
            dt1="";
        dt.append(dt1); 
    dt=pd.DataFrame(dt, columns=['Last_values'])  
    dt.to_csv(str(path2)+str(fileToSave)+str(i)+str("To")+str(i+1)+"lastValues"+".csv",index=False);
    print(dt); 




