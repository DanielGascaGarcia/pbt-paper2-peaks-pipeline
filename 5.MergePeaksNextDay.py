#Code: 5.MergePeaksNextDay.py
#Description: Read files and find peaks.
#Created 14th November 2023
#Author: mbaxdg6
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

# --- Configurable global variable ---
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
for file in os.listdir(path2):
    if file.startswith(listVariables[0]+str(fileToRead)+str('_Merge')):
        filesBG.append(file);
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
for file in os.listdir(path2):
    if file.startswith(listVariables[0]+str(fileToRead)+str('_wCNF ')):
        print(file); 
        filesToMerge.append(file);
# -----------------------------------------------------------#
#                    Merge files
# -----------------------------------------------------------#


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

    # Interpolate missing values if needed
    output1 = output.interpolate(limit=5, limit_direction='both')

    for j in range(len(filesToMerge)):
        # Check if the file to merge exists in the list
        if listVariables[0] + str(fileToRead) + str('_wCNF ') + Matrix[i][0][35:] in filesToMerge[j]:
            print("Found")

            # Read the file to merge
            FileToMerge = pd.read_csv(str(path2) + listVariables[0] + str(fileToRead) + '_wCNF ' + Matrix[i][0][35:])
            
            # Strip whitespace in 'Time' for consistency
            FileToMerge['Time'] = FileToMerge['Time'].astype(str).str.strip()
            FileToMerge['Time'] = FileToMerge['Time']+":00"
            # Rename 'BGValue' in the merged data to 'Delete'
            output1.rename(columns={'BGValue': 'Delete'}, inplace=True)

            # Merge FileToMerge with the interpolated data based on 'Time'
            output2 = pd.merge(FileToMerge, output1, on='Time', how='left')

            # # Replace BGValue where Delete > 0
            output2.loc[output2['Delete'] > 0, 'BGValue'] = ''
            # print(output2)
            # # Save the updated file
            output2.to_csv(str(path2) + listVariables[0] + str(fileToRead) + '_wCNF ' + Matrix[i][0][35:], index=False)
