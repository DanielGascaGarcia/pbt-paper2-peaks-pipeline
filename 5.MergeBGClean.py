"""
5.MergeBGClean.py
Step 5 (meal-based branch): join the cleaned daily CGM files of one participant
onto a common minute-by-minute grid.

Created: 11 April 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    Takes every daily working copy written by 4.MealBolusDetection.py
    (glucose_level<id>-ws-training_wCN <day>.csv), keeps its Time and BGValue
    columns and left-joins them, one day per column, onto the 1,440-minute
    grid from 3.PivotGeneratorBG.py. Readings removed around meals are
    already NaN in BGValue, so they stay empty here.

Inputs
    globals.id, globals.path2
    <path2>/PivotBG_wCN.csv   (3.PivotGeneratorBG.py)
    <path2>/glucose_level<id>-ws-training_wCN <Weekday>-<YYYY-MM-DD> .csv
    (4.MealBolusDetection.py)

Output
    <path2>/BGwNMLeftJoined<id>.csv
    Columns: (unnamed index), Key (HH:MM:00, 1,440 rows), BGValue0,
    BGValue1, ... one column per day file. Saved WITH the pandas index, so
    the file has two non-data columns ("Unnamed: 0" and "Key") when re-read;
    this is why later steps subtract 2 from the column count of this file.
    CGM readings come every 5 min, so most minutes of each day are empty.

Notes
    - Times are matched to the minute: both sides are cut to "HH:MM" before
      the join and ":00" is added back at the end. A reading at 12:03:27
      lands on 12:03:00.
    - Every day that has a CGM file is included, also days without a meal
      file. Those days had no post-meal window removed in step 4.
    - Day columns are numbered in the order returned by os.listdir, which is
      not guaranteed to be chronological.
    - If fewer than 2 day files are found, output1 is never created and the
      line that adds ":00" fails with a NameError.
"""


import datetime 
import pandas as pd
import os
from datetime import datetime,timedelta
import datetime 
from matplotlib import pyplot as plt
import numpy as np
import globals

# --- Configurable global variables (set in globals.py) ---
id = globals.id;

# Parameters
filesBG=[];
path2=globals.path2;
fileToRead=str(id)+"-ws-training";
fileToSave="BGwNMLeftJoined"+str(id)+".csv";
listVariables=['glucose_level',
'finger_stick',
'basal',
'temp_basal',
'bolus',
'meal',
'sleep',
'work',
'stressors',
'hypo_event',
'illness',
'exercise',
'basis_heart_rate',
'basis_gsr',
'basis_skin_temperature',
'basis_air_temperature',
'basis_steps',
'basis_sleep'];

# Collect the working copies from step 4 (note the "_wCN " in the name).
for file in os.listdir(path2):
    if file.startswith(listVariables[0]+str(fileToRead)+str('_wCN ')):
        # print(file); 
        filesBG.append(file);

# print(filesBG);

if len(filesBG)>=2:
    # reading two csv files
    # data1: the 1,440-minute grid; data2: first day, value column -> BGValue0.
    data1 = pd.read_csv(str(path2)+'PivotBG_wCN'+'.csv')
    data2 = pd.read_csv(str(path2)+filesBG[0],usecols = ['Time','BGValue']);
    data2.rename(columns = {'BGValue':'BGValue'+str(0)}, inplace = True);
    data2.rename(columns = {'Time':'Key'}, inplace = True);
    # Cut both keys to "HH:MM" so readings are matched to the minute.
    data1['Key']=data1['Key'].str.slice(0, 5);
    data1['Key']=data1['Key'].str.strip();
    print(data1);
    data2['Key']=data2['Key'].str.slice(0, 5);
    data2['Key']=data2['Key'].str.strip();
    print(data2);
    # using merge function by setting how='left'
    # Left join: keeps all 1,440 minutes; minutes with no reading stay NaN.
    output1 = pd.merge(data1,data2,suffixes=('',''),on='Key',how='left');
    # Remaining days, one column each: BGValue1, BGValue2, ...
    for j in range(len(filesBG)-1):
            data3 = pd.read_csv(str(path2)+filesBG[j+1],usecols = ['Time','BGValue']);
            data3.rename(columns = {'BGValue':'BGValue'+str(j+1)}, inplace = True);
            data3.rename(columns = {'Time':'Key'}, inplace = True);
            data3['Key']=data3['Key'].str.slice(0, 5);
            data3['Key']=data3['Key'].str.strip();
            # print(data3);
            output1 = pd.merge(output1,data3,suffixes=('',''),on='Key',how='left');
# Restore the "HH:MM:SS" format of the key.
output1['Key']=output1['Key']+':00';
# Saving the result
output1.to_csv(str(path2)+str(fileToSave));
