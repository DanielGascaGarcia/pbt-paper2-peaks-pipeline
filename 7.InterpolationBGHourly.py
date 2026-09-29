"""
7.InterpolationBGHourly.py
Step 7 (meal-based branch): fill short gaps in the hourly CGM files by linear
interpolation.

Created: 19 April 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    CGM readings come every 5 min, so the minute grid has 4 empty minutes
    between readings. For each hourly file and each day column, this script
    fills those gaps by linear interpolation, working inside the hour only
    (it never uses readings from the previous or next hour).

Inputs
    globals.id, globals.path2
    <path2>/BGHour<id><i>To<i+1>.csv   for i = 0 ... 23   (6.SplitHours.py)

Outputs
    <path2>/BGHourInterpolated<id><i>To<i+1>.csv   for i = 0 ... 23
    Same columns as the input: Unnamed: 0, Key, BGValue0, BGValue1, ...
    (two non-data columns, which is why step 8 subtracts 2 from the column
    count of these files).

How interpolate(limit=5, limit_direction='both') behaves (pandas 2.2.2)
    - A gap of up to 10 consecutive empty minutes is filled completely
      (5 minutes from each side).
    - In a longer gap, 5 minutes are filled at each edge and the middle stays
      empty. This also applies to the post-meal windows removed in step 4:
      their edges shrink by up to 5 minutes on each side, and those minutes
      get values interpolated towards the reading on the other side.
    - Empty minutes at the start or end of the hour (up to 5) get the value
      of the nearest reading.
    - An hour with no reading at all for a day stays empty.

Note on the warnings filter
    The Key column is text. With pandas 2.2.2, interpolating a DataFrame that
    contains a text column only raises a FutureWarning, which the filter below
    hides. Newer pandas versions raise an error instead ("Cannot interpolate
    with str dtype"), so this script needs pandas < 3 as pinned in
    requirements.txt.
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
import globals
id=globals.id;


# --- Configurable global variables (set in globals.py) ---
path2=globals.path2;
fileToRead="BGHour"+str(id);
fileToSave="BGHourInterpolated"+str(id);
# Hides the pandas warning about interpolating the text column Key (see header).
warnings.simplefilter(action='ignore', category=FutureWarning)

for i in range(24):
    data = pd.read_csv(str(path2)+str(fileToRead)+str(i)+str("To")+str(i+1)+".csv"); 
    # Linear interpolation down each column, inside this hour only.
    dI=data.interpolate(limit=5, limit_direction='both');
    # dI["MeanBGValue"]=dI.mean(axis='columns',numeric_only=True);
    # dI["MedianBGValue"]=dI.median(axis='columns',numeric_only=True);
    # dI["STDBGValue"]=dI.std(axis='columns',numeric_only=True);
    # print(dI.columns);
    dI.to_csv(str(path2)+str(fileToSave)+str(i)+str("To")+str(i+1)+".csv",index=False);