"""
# >>> SENSITIVITY TEST VERSION - do not use for reported results <<<
7.SplitHoursPeaks.py
Step 7 (peak-based branch): split the minute-by-minute CGM table into 24
files, one per hour of the day.

Created: 14 November 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    Same as 6.SplitHours.py in the meal-based branch: for each hour i (0-23),
    copies the rows of BGwNMLeftJoinedPeak<id>.csv whose Key is between
    i:00:00 and i:59:59 (60 rows) into a separate file with the same header.

Inputs
    globals.id, globals.path2
    <path2>/BGwNMLeftJoinedPeak<id>.csv   (6.MergePeaks.py)

Outputs
    <path2>/BGHourPeak<id><i>To<i+1>.csv   for i = 0 ... 23
    Columns: Unnamed: 0, Key, BGValue0, BGValue1, ... (two non-data columns)

Notes
    - Unlike the meal-based branch, there is no hourly interpolation step
      after this one: 8.RelativeChangePeaks.py reads these files directly.
      The only interpolation in this branch is the one applied to the
      carried-over marks in 5.MergePeaksNextDay.py.
    - The hour is taken from row[1] (Key); row[0] is the unnamed index.
"""


import datetime 
import pandas as pd
import os
from datetime import datetime,timedelta
import datetime 
from matplotlib import pyplot as plt
import numpy as np
import csv

import globals
import warnings
# Key is text; pandas 2.2.2 only warns when interpolating it (see 7.InterpolationBGHourly.py).
warnings.simplefilter(action='ignore', category=FutureWarning)

# --- Configurable global variables (set in globals.py) ---
id = globals.id;
path2 = globals.path2;

fileToRead="BGwNMLeftJoinedPeak"+str(id)+".csv";
fileToSave="BGHourPeak"+str(id);


# Loop over all day round
for i in range(24):
    # csv.reader streams the rows; pandas is only used to get the header.
    with open(str(path2)+str(fileToRead)) as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
                data = pd.read_csv(str(path2)+str(fileToRead)); 
                data_top = data.columns;
                print(data_top); 
                # Hour window: i:00:00 to i:59:59 (the date is arbitrary).
                dt1 = datetime.datetime(2010, 12, 1,i,0,0);
                dt2 = datetime.datetime(2010, 12, 1,i,59,59);
                with open(str(path2)+str(fileToSave)+str(i)+str("To")+str(i+1)+".csv", 'w', newline='') as fout:
                            csv_output = csv.writer(fout);
                            csv_output.writerow(data_top);  #header
                            for row in reader:
                                # row[1] is Key ("HH:MM:SS"); row[0] is the unnamed index.
                                split=datetime.datetime(2010, 12, 1,int(row[1][0:2]),int(row[1][3:5]),int(row[1][6:8])); 
                                if dt1.strftime('%H:%M:%S')<=split.strftime('%H:%M:%S')<=dt2.strftime('%H:%M:%S'):
                                    # print (row[1]);
                                    csv_output.writerow(row);

    # SENSITIVITY TEST (interpolation position): interpolate inside the hour,
    # exactly as 7.InterpolationBGHourly.py does in the meal-based branch, so
    # that both branches start and end each hour on actual readings.
    out_h = str(path2)+str(fileToSave)+str(i)+str("To")+str(i+1)+".csv"
    hour = pd.read_csv(out_h)
    hour = hour.interpolate(limit=5, limit_direction='both')
    hour.to_csv(out_h, index=False)

