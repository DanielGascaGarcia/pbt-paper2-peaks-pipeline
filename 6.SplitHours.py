"""
6.SplitHours.py
Step 6 (meal-based branch): split the minute-by-minute CGM table into 24 files,
one per hour of the day.

Created: 19 April 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    For each hour i (0-23), copies the rows of BGwNMLeftJoined<id>.csv whose
    Key is between i:00:00 and i:59:59 (60 rows) into a separate file, with
    the same header.

Inputs
    globals.id, globals.path2
    <path2>/BGwNMLeftJoined<id>.csv   (5.MergeBGClean.py)

Outputs
    <path2>/BGHour<id><i>To<i+1>.csv   for i = 0 ... 23
    e.g. BGHour5400To1.csv, BGHour54023To24.csv
    Columns: Unnamed: 0, Key, BGValue0, BGValue1, ... (one per day)
    The first two columns are not data; later steps rely on this.

Notes
    - The input file is re-read once per hour (24 times); this only costs time.
    - The hour is taken from the second CSV column (row[1] = Key), because the
      first column is the unnamed index written by 5.MergeBGClean.py.
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
# --- Configurable global variables (set in globals.py) ---
id=globals.id;

path2=globals.path2;
fileToRead="BGwNMLeftJoined"+str(id)+".csv";
fileToSave="BGHour"+str(id);


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

