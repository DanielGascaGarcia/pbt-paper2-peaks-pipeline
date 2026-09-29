"""
5.MergePeaksNextDay.py   (header of the original file reads "Read files and find peaks")
Step 5 (peak-based branch): carry the part of a removal window that passes
midnight over to the following day.

Created: 14 November 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    4.PeaksDetection.py writes, for a day whose removal window runs past
    midnight, a "_Merge" file holding the readings that must be removed from
    the early hours of the FOLLOWING day. For every such file this script:
      1. puts it on the minute grid (PivotPeak_wCN.csv) and interpolates it
         (limit 5 minutes, both directions), so the marks cover the minutes
         between readings;
      2. finds the working copy (_wCNF) of the same date;
      3. blanks BGValue in that copy wherever the interpolated mark is > 0,
         and saves the copy back under the same name.

Inputs
    globals.id, globals.path2
    <path2>/glucose_level<id>-ws-training_Merge <Weekday>-<YYYY-MM-DD> .csv   (4.PeaksDetection.py)
    <path2>/glucose_level<id>-ws-training_wCNF <Weekday>-<YYYY-MM-DD> .csv    (4.PeaksDetection.py)
    <path2>/PivotPeak_wCN.csv                                                 (minute grid, column Time)

Outputs
    The same _wCNF files, overwritten: BGValue blanked where the carried-over
    window applies, a new column "Delete" (the interpolated mark) and the
    Time values written as "HH:MM:00".

Notes
    - The interpolation widens the carried-over window: gaps of up to 10
      minutes are bridged and up to 5 minutes are added at each edge, so a
      few more minutes are removed than the marks alone would remove.
    - The _Merge file and the _wCNF file are paired by the date part of the
      name. Matrix[i][0][35:] removes "glucose_level<id>-ws-training_Merge "
      (35 characters for a 3-digit ID), and the date used for sorting is cut
      from the last 15 characters of the name, as in 4.MealBolusDetection.py.
    - ":00" is appended to the _wCNF times before the join. The join only
      finds matches if those times are stored as "HH:MM"; if they already had
      seconds, no reading would be removed and no error would appear.
    - Delete > 0 is always true for a glucose value, so any mark removes the
      reading; empty marks (NaN) never do.
    - The warnings filter at the top hides the pandas message about
      interpolating the text column Time (needs pandas < 3, as pinned).
"""
import warnings
import datetime 
import pandas as pd
import os
# import time
from datetime import datetime,timedelta
import datetime 
from matplotlib import pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter, freqz
import operator
from scipy import interpolate
from scipy.interpolate import make_interp_spline
from scipy.interpolate import UnivariateSpline
from scipy.interpolate import interp1d
import matplotlib
from scipy.signal import find_peaks, peak_prominences,peak_widths
matplotlib.rcParams.update({'font.size': 15})
import math
warnings.simplefilter(action='ignore', category=FutureWarning)
import globals

# --- Configurable global variables (set in globals.py) ---
id = globals.id;
path2 = globals.path2;

# Parameters
filesBG=[];
filesToMerge=[];
fileToRead=str(id)+"-ws-training";
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
# -----------------------------------------------------------#
#                   Files of Blood Glucose
# -----------------------------------------------------------#
# Day files with the carried-over marks written by 4.PeaksDetection.py.
for file in os.listdir(path2):
    if file.startswith(listVariables[0]+str(fileToRead)+str('_Merge')):
        filesBG.append(file);
# Matrix: [file name, date text, year, month, day], sorted by date below.
h, w = len(filesBG), 5;
Matrix = [[0 for x in range(w)] for y in range(h)] ;
# -----------------------------------------------------------#
#                    Sort of files
# -----------------------------------------------------------#
for i in range(len(filesBG)):
    Matrix[i][0]=filesBG[i];
    Matrix[i][1]=filesBG[i][len(Matrix[i][0]):len(Matrix[i][0])-16:-1]; 
    Matrix[i][1]=Matrix[i][1][::-1].strip();
    # print(Matrix[i][1]);
    Matrix[i][2]=(Matrix[i][1][0:4]);#Year
    # print(Matrix[i][2]);
    Matrix[i][3]=(Matrix[i][1][5:7]);#Month
    # print(Matrix[i][2]);
    Matrix[i][4]=(Matrix[i][1][8:10]);#Day
    # print(Matrix[i][3]);
Matrix = sorted(Matrix, key = operator.itemgetter(2,3,4));
# -----------------------------------------------------------#
#                  Files to merge
# -----------------------------------------------------------#
# Working copies of the peak branch (note "_wCNF " with the space).
for file in os.listdir(path2):
    if file.startswith(listVariables[0]+str(fileToRead)+str('_wCNF ')):
        print(file); 
        filesToMerge.append(file);
# -----------------------------------------------------------#
#                    Merge files
# -----------------------------------------------------------#


# One pass per _Merge file.
for i in range(len(filesBG)):
    print(Matrix[i][0][35:])
    
    # Read the BG data file and main data file
    dataBG = pd.read_csv(str(path2) + Matrix[i][0])  
    data1 = pd.read_csv(str(path2) + 'PivotPeak_wCN.csv')

    # Strip any whitespace in the 'Time' column
    dataBG['Time'] = dataBG['Time'].str.strip()
    data1['Time'] = data1['Time'].str.strip()

    # Merge BG data with main data on 'Time'
    output = pd.merge(data1, dataBG, on='Time', how='left')

    # Interpolation limit 5, both directions: widens the marks (see header).
    # Interpolate missing values if needed
    output1 = output.interpolate(limit=5, limit_direction='both')

    for j in range(len(filesToMerge)):
        # Check if the file to merge exists in the list
        # Pair with the _wCNF file of the same date ([35:] = "<Weekday>-<date> .csv").
        if listVariables[0] + str(fileToRead) + str('_wCNF ') + Matrix[i][0][35:] in filesToMerge[j]:
            print("Found")

            # Read the file to merge
            FileToMerge = pd.read_csv(str(path2) + listVariables[0] + str(fileToRead) + '_wCNF ' + Matrix[i][0][35:])
            
            # Strip whitespace in 'Time' for consistency
            FileToMerge['Time'] = FileToMerge['Time'].astype(str).str.strip()
            # Assumes the _wCNF times are "HH:MM" (see header).
            FileToMerge['Time'] = FileToMerge['Time']+":00"
            # Rename 'BGValue' in the merged data to 'Delete'
            output1.rename(columns={'BGValue': 'Delete'}, inplace=True)

            # Merge FileToMerge with the interpolated data based on 'Time'
            output2 = pd.merge(FileToMerge, output1, on='Time', how='left')

            # # Replace BGValue where Delete > 0
            # Blank the readings covered by the carried-over window.
            output2.loc[output2['Delete'] > 0, 'BGValue'] = ''
            # print(output2)
            # # Save the updated file
            output2.to_csv(str(path2) + listVariables[0] + str(fileToRead) + '_wCNF ' + Matrix[i][0][35:], index=False)
