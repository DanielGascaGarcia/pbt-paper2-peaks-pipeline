"""
6.MergePeaks.py
Step 6 (peak-based branch): record which readings were removed and join the
cleaned daily CGM files onto a minute-by-minute grid.

Created: 14 November 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    1. For every working copy (_wCNF), adds a column ValueCh holding the
       original value (BGValue2) of every reading that is now empty in
       BGValue, i.e. every removed reading, including those removed after
       midnight by 5.MergePeaksNextDay.py. Kept readings get an empty cell.
       The file is overwritten.
    2. Joins BGValue of every day, one column per day, onto the 1,440-minute
       grid from 3.PivotGeneratorBG.py, exactly as 5.MergeBGClean.py does in
       the meal-based branch.

Inputs
    globals.id, globals.path2
    <path2>/glucose_level<id>-ws-training_wCNF <Weekday>-<YYYY-MM-DD> .csv
    <path2>/PivotBG_wCN.csv

Outputs
    The _wCNF files with the new ValueCh column (read by G.Graph3DPeaksRemoved.py)
    <path2>/BGwNMLeftJoinedPeak<id>.csv
        Columns: (unnamed index), Key (HH:MM:00, 1,440 rows), BGValue0,
        BGValue1, ... one per _wCNF file. Saved WITH the index, so there are
        two non-data columns ("Unnamed: 0" and Key); this is why later steps
        subtract 2 from the column count of this file.

Notes
    - Only the days that have a _wCNF file are joined. Which days get one is
      decided in 4.PeaksDetection.py.
    - Times are matched to the minute (cut to "HH:MM", ":00" added back), so
      both "HH:MM" and "HH:MM:SS" times in the _wCNF files work here.
    - Day columns follow the os.listdir order, not necessarily the calendar.
    - If fewer than 2 files are found, output1 is never created and the line
      that adds ":00" fails with a NameError.
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

# Parameters
filesBG=[];

id = globals.id;
path2 = globals.path2;
fileToRead=str(id)+"-ws-training";
fileToSave="BGwNMLeftJoinedPeak"+str(id)+".csv";
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

# Working copies of the peak branch (note "_wCNF " with the space).
for file in os.listdir(path2):
    if file.startswith(listVariables[0]+str(fileToRead)+str('_wCNF ')):
        print(file); 
        filesBG.append(file);

# print(filesBG);

# Part 1: ValueCh = original value of every removed reading (BGValue empty,
# BGValue2 present); empty for readings that were kept.
for i in range(len(filesBG)):
    data = pd.read_csv(str(path2)+filesBG[i]);
    t=len(data["Time"]); #Find important numbers
    Value=pd.notnull(data["BGValue"]) 
    Value1=pd.notnull(data["BGValue2"]) 
    result=[];
    for k in range(len(Value)):
           if (not Value[k] and Value1[k])==True:
               result.append(data.loc[k, 'BGValue2']);
           else:
                result.append('');
    data["ValueCh"]=result;
    data.to_csv(str(path2)+filesBG[i], index=False); # save to new csv 

    
           


# Part 2: join the remaining readings onto the minute grid, one column per day.
if len(filesBG)>=2:
    # reading two csv files
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
    output1 = pd.merge(data1,data2,suffixes=('',''),on='Key',how='left');
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
