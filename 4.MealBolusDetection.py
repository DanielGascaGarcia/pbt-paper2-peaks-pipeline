"""
4.MealBolusDetection.py
Step 4 (meal-based branch): remove the post-meal glucose window from each day
of CGM data.

Created: 29 March 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    1. Makes a working copy of every daily CGM file, with extra columns to
       record which readings are removed.
    2. For every self-reported meal, looks for the peak of the (low-pass
       filtered) glucose in the 3 h after the meal and classifies the meal as
       high / medium / low glycaemic by the time to that peak.
    3. Removes the CGM readings from the meal time to meal time + 4 h. If that
       window passes midnight, the part after 00:00 is removed from the next
       day's file.
    4. Saves the result of each day that has a meal file as a _ToGraph file,
       which is the input of the next step of this branch.

Inputs
    globals.id, globals.path2
    <path2>/glucose_level<id>-ws-training <Weekday>-<YYYY-MM-DD> .csv
    <path2>/meal<id>-ws-training <Weekday>-<YYYY-MM-DD> .csv
    <path2>/bolus<id>-ws-training <Weekday>-<YYYY-MM-DD> .csv   (listed only)
    (per-day files written by 2.Disaggregator.py)

Outputs
    <path2>/glucose_level<id>-ws-training_wCN <Weekday>-<YYYY-MM-DD> .csv
        working copy, columns: Time, BGValue, Flag, ValueCh, BGValue2
    <path2>/glucose_level<id>-ws-training_ToGraph<Weekday>-<YYYY-MM-DD> .csv
        same without BGValue2; only for days that have a meal file

Removed readings
    Flag = 100, the original value is copied to ValueCh and BGValue is set to
    NaN. Readings that are kept have Flag = 0 and ValueCh = 0.

Assumptions worth knowing
    - File names: the day files end in "<YYYY-MM-DD> .csv" (with a space
      before .csv, inherited from the parsed text). The date used for sorting
      is cut from the last 15 characters of the name, and the prefix
      "glucose_level<id>-ws-training " is removed with a fixed [29:], which
      assumes a 3-digit participant ID.
    - The overflow past midnight is removed from the next CGM file only when
      that file is the next calendar day (has_next_day). After a gap in the
      record, or on the last day, today's window is capped at 23:59:59 and
      nothing is removed elsewhere. Earlier versions used the next file in
      date order whatever its date, and on the last day tried to open a file
      that does not exist.
    - The whole main program is inside one try/except. Any error stops the
      processing of all remaining days and only prints "file not found".
"""


import datetime 
import pandas as pd
import os
from datetime import datetime,timedelta
import datetime 
from matplotlib import pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter, freqz
import operator
import globals

# --- Configurable global variable ---
# --- Configurable global variables (set in globals.py) ---
id = globals.id;
filesBG=[];
filesBolus=[];
filesMeals=[];
path2=globals.path2;
fileToRead=str(id)+"-ws-training";
# Data type names used to build file names. Used here:
#   [0] glucose_level, [4] bolus, [5] meal.
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
# Collect the daily CGM files of this participant. Note the space after
# "-ws-training": it excludes the _wCN / _ToGraph files this script writes.
for file in os.listdir(path2):
    if file.startswith(listVariables[0]+str(fileToRead)+str(' ')):
        # print(file); 
        filesBG.append(file);
# Matrix: one row per CGM day file -> [file name, date text, year, month, day]
h, w = len(filesBG), 5;
Matrix = [[0 for x in range(w)] for y in range(h)] ;
# -----------------------------------------------------------#
#                    Sort of files
# -----------------------------------------------------------#
for i in range(len(filesBG)):
    Matrix[i][0]=filesBG[i];
    # Date text = last 15 characters of the name, e.g. "2021-12-07 .csv".
    # This relies on the space before ".csv" (see header).
    Matrix[i][1]=filesBG[i][len(Matrix[i][0]):len(Matrix[i][0])-16:-1]; 
    Matrix[i][1]=Matrix[i][1][::-1].strip();
    # print(Matrix[i][1]);
    Matrix[i][2]=(Matrix[i][1][0:4]);#Year
    # print(Matrix[i][2]);
    Matrix[i][3]=(Matrix[i][1][5:7]);#Month
    # print(Matrix[i][2]);
    Matrix[i][4]=(Matrix[i][1][8:10]);#Day
    # print(Matrix[i][3]);
# Sort the days chronologically. From here on Matrix[i] is the i-th day and
# Matrix[i+1] is treated as the following day.
Matrix = sorted(Matrix, key = operator.itemgetter(2,3,4));

def has_next_day(i):
    """True if Matrix[i+1] exists and is the calendar day after Matrix[i].

    The midnight overflow of a meal window is only removed from the next file
    when that file is the following calendar day. After a gap in the record
    (or on the last day) nothing is removed from any other day.
    """
    if i+1 >= len(Matrix):
        return False
    d0=datetime.date(int(Matrix[i][2]),int(Matrix[i][3]),int(Matrix[i][4]));
    d1=datetime.date(int(Matrix[i+1][2]),int(Matrix[i+1][3]),int(Matrix[i+1][4]));
    return (d1-d0).days==1
# -----------------------------------------------------------#
#                  Files of Boluses
# -----------------------------------------------------------#
# Collect the daily bolus files (listed only; see the end of the script).
for file in os.listdir(path2):
    if file.startswith(listVariables[4]+str(fileToRead)+str(' ')):
        # print(file); 
        filesBolus.append(file);
# print(filesBolus);
# -----------------------------------------------------------#
#                  Files of Meals
# -----------------------------------------------------------#
# Collect the daily meal files.
for file in os.listdir(path2):
    if file.startswith(listVariables[5]+str(fileToRead)+str(' ')):
        # print(file); 
        filesMeals.append(file);
# print(filesMeals);


# -----------------------------------------------------------#
#                  Main program
# -----------------------------------------------------------#
try:
# -----------------------------------------------------------#
#                    Create files to input
# -----------------------------------------------------------#
# Part 1: working copy of each day with the columns needed to mark removals.
# Matrix[i][0][29:] is the file name without "glucose_level<id>-ws-training "
# (29 characters for a 3-digit ID), i.e. "<Weekday>-<YYYY-MM-DD> .csv".
    for i in range(len(filesBG)):
            print(Matrix[i][0])
            dataBG = pd.read_csv(str(path2)+Matrix[i][0]);
            BG_1=len(dataBG["Time"]); #Find important numbers
            open(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:], 'w').close();
            BGT_=dataBG[["Time","BGValue"]];
            for l in range(BG_1):
                    # Time is read as " HH:MM:SS" (leading space), hence the
                    # slices [0:3], [4:6], [7:9]. The date 2010-12-01 is arbitrary.
                    BGdt=datetime.datetime(2010, 12, 1,int(BGT_["Time"][l][0:3]),int(BGT_["Time"][l][4:6]),int(BGT_["Time"][l][7:9]));
                    file = open(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:], 'a');
                    # Row: Time, BGValue, Flag=0, ValueCh=0, BGValue2 (copy of BGValue)
                    file.write(str(BGdt.strftime('%H:%M:%S')+str(",")+str(dataBG["BGValue"][l])+str(",")+str(0)+str(",")+str(0)+str(",")+str(dataBG["BGValue"][l])));
                    file.write('\n');
                    file.close();
            # Re-read the file and add the header.
            df = pd.read_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:],  header=None);
            df.rename(columns={0: 'Time', 1: 'BGValue', 2: 'Flag', 3: 'ValueCh',4: 'BGValue2'}, inplace=True);
            df.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:], index=False); # save to new csv 
# -----------------------------------------------------------#
#                   Find files to use
# -----------------------------------------------------------#
# Part 2: for every day that has a meal file, remove the post-meal windows.
    for i in range(len(filesBG)):

        print(Matrix[i][0]);   

        for j in range(len(filesMeals)):
            #Meals
            if listVariables[5]+str(fileToRead)+str(' ')+Matrix[i][0][29:]  in filesMeals[j]:
                # print("exist: "+listVariables[5]+str(fileToRead)+str(' ')+filesBG[i][29:]);
                dataBG = pd.read_csv(str(path2)+Matrix[i][0]);
                dataMeal = pd.read_csv(str(path2)+listVariables[5]+str(fileToRead)+str(' ')+Matrix[i][0][29:]);

                print(listVariables[5]+str(fileToRead)+str(' ')+Matrix[i][0][29:]);
               
                M=len(dataMeal["Time"]); #Find important numbers
                MTT=dataMeal["Time"];
                MC=dataMeal["CarbsValue"];
                MK=dataMeal["TypeFood"];
                # print(type(dataBG["Time"]));

# -----------------------------------------------------------#
#       Find maximum values and define Glycemic index
# -----------------------------------------------------------#
                # One iteration per meal of the day.
                for k in range(M):
                    # print(M);
                    # MK[k] in {' Breakfast ',' Lunch ',' Dinner '}
                    # Filter by meal type disabled (1==1): every meal is processed.
                    # The commented line above shows the original filter.
                    if 1==1: #Check for the kind of food

                                print(MK[k]);

                                # dt = meal time; dt1 = meal + 3 h = end of the window
                                # used to look for the glucose peak. Capped at 23:59:59,
                                # so the peak search never goes past midnight.
                                dt = datetime.datetime(2010, 12, 1,int(MTT[k][0:3]),int(MTT[k][4:6]),int(MTT[k][7:9]));
                                dt1= datetime.datetime(2010, 12, 1,int(MTT[k][0:3]),int(MTT[k][4:6]),int(MTT[k][7:9]))+datetime.timedelta(hours=3);# hours=timne needed to find the maximum
                                BG_=len(dataBG["Time"]); #Find important numbers
                                if  dt1>datetime.datetime(2010, 12, 1,23,59,59):
                                        # print("dt1 modified");
                                        # print(dt1);
                                        dt1=datetime.datetime(2010, 12, 1,23,59,59);
                                        # print(dt1);
                                BGT=dataBG[["Time","BGValue"]];
                                BGV=[];
                                time=[];
                                # Keep the CGM readings between the meal and meal + 3 h.
                                for l in range(BG_):
                                    BGdt=datetime.datetime(2010, 12, 1,int(BGT["Time"][l][0:3]),int(BGT["Time"][l][4:6]),int(BGT["Time"][l][7:9]));
                                    if dt.strftime('%H:%M:%S') <= BGdt.strftime('%H:%M:%S')<= dt1.strftime('%H:%M:%S'): 
                                        # print(dt.strftime('%H:%M:%S'),BGT["BGValue"][l],BGdt.strftime('%H:%M:%S'),dt1.strftime('%H:%M:%S'));
                                        time.append(BGdt.strftime('%H:%M:%S'));
                                        BGV.append(BGT["BGValue"][l]);
                                # Butterworth low-pass filter (order 6) to smooth the series
                                # before locating the maximum. fs and cutoff are nominal values
                                # (CGM is sampled every 5 min, not at 25 Hz); only their ratio
                                # matters: normalised cutoff = 5 / 12.5 = 0.4.
                                #Low pass filter        
                                # Filter requirements.
                                order = 6;
                                fs = 25.0;       # sample rate, Hz
                                cutoff = 5;      # desired cutoff frequency of the filter, Hz
                                nyq = 0.5 * fs;
                                normal_cutoff = cutoff / nyq;
                                b, a = butter(order, normal_cutoff, btype='low', analog=False);
                                BGVF = lfilter(b, a, BGV);
                                GlD=pd.DataFrame({'Time': time, 'BGValue':BGV,'BGValueF':BGVF}); 
                                # Meals with no CGM readings in the window are skipped.
                                if len(GlD)>0: #Missing Blood Glucose values 
                                    # TypeFood = hours from the FIRST CGM reading in the window
                                    # (not the exact meal time) to the filtered peak.
                                    t2 = datetime.datetime(2010, 12, 1,int(GlD["Time"][GlD["BGValueF"].argmax()][0:2]),int(GlD["Time"][GlD["BGValueF"].argmax()][3:5]),int(GlD["Time"][GlD["BGValueF"].argmax()][6:8]));
                                    t1 = datetime.datetime(2010, 12, 1,int(GlD["Time"][0][0:2]),int(GlD["Time"][0][3:5]),int(GlD["Time"][0][6:8]));
                                    TypeFood=(t2-t1).total_seconds()/3600;
                                    print((t2-t1).total_seconds()/3600);#Value needed to check the glycemic index
# -----------------------------------------------------------#
#                 High Glycemic Food
# -----------------------------------------------------------#  
                                    # Classification by time to peak: <1.5 h high, 1.5-2.5 h
                                    # medium, >=2.5 h low glycaemic. NOTE: all three classes
                                    # remove the same window (meal to meal + 4 h); the class is
                                    # only printed.
                                    if  0<=TypeFood<1.5:
                                        print("High Glycemic Food");
                                        # Removal window: dtH1 = meal time, dtH2 = meal + 4 h.
                                        dtH1 = datetime.datetime(2010, 12, 1,int(MTT[k][0:3]),int(MTT[k][4:6]),int(MTT[k][7:9]));
                                        dtH2= datetime.datetime(2010, 12, 1,int(MTT[k][0:3]),int(MTT[k][4:6]),int(MTT[k][7:9]))+datetime.timedelta(hours=4);# hours=timne needed to find the maximum 
# -----------------------------------------------------------#
#                 Next day condition
# -----------------------------------------------------------#                                    
                                        # If meal + 4 h passes midnight, remove 00:00 -> overflow time
                                        # in the next day file (Matrix[i+1]), then cap today at 23:59:59.
                                        if  dtH2>datetime.datetime(2010, 12, 1,23,59,59):
                                            dtH3=datetime.datetime(2010, 12, 1,00,00,00);
                                            dtH4=dtH2;
                                            print("dtH2 modified");
                                            # print(dtH3.strftime('%H:%M:%S'));

                                            # Only if the next file is the next calendar day.
                                            if has_next_day(i):
                                                dataBG1 = pd.read_csv(str(path2)+Matrix[i+1][0]);
                                                BG_=len(dataBG1["Time"]);
                                                BGT_=dataBG1[["Time","BGValue"]];
                                            else:
                                                BG_=0;
                                            for l in range(BG_):
                                                    BGdt=datetime.datetime(2010, 12, 1,int(BGT_["Time"][l][0:3]),int(BGT_["Time"][l][4:6]),int(BGT_["Time"][l][7:9]));
                                                    if dtH3.strftime('%H:%M:%S')<=BGdt.strftime('%H:%M:%S')<=dtH4.strftime('%H:%M:%S'): 
                                                        # reading the csv file
                                                        df = pd.read_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i+1][0][29:]);
                                                        
                                                        # updating the column value/data
                                                        # Mark as removed: Flag=100, keep the original
                                                        # value in ValueCh, blank BGValue.
                                                        df.loc[l, 'Flag'] = 100;
                                                        df.loc[l, 'ValueCh']=df.loc[l, 'BGValue2'];   
                                                        df.loc[l, 'BGValue'] = np.nan;
                                                        
                                                        # writing into the file
                                                        df.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i+1][0][29:], index=False);
                                            # Today's window now ends at 23:59:59.
                                            dtH2=datetime.datetime(2010, 12, 1,23,59,59);
                                        BG_2=len(dataBG["Time"]); #Find important numbers
# -----------------------------------------------------------#
#                 Chop off
# -----------------------------------------------------------#  
                                        # Remove the window on the current day. The file is read and
                                        # written once per removed reading.
                                        for l in range(BG_2):
                                                BGdt=datetime.datetime(2010, 12, 1,int(BGT["Time"][l][0:3]),int(BGT["Time"][l][4:6]),int(BGT["Time"][l][7:9]));
                                                if dtH1.strftime('%H:%M:%S')<=BGdt.strftime('%H:%M:%S')<=dtH2.strftime('%H:%M:%S'): 
                                                    # reading the csv file
                                                    df = pd.read_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:]);
                                                    
                                                    # updating the column value/data
                                                    df.loc[l, 'Flag'] = 100;
                                                    df.loc[l, 'ValueCh']=df.loc[l, 'BGValue2'];   
                                                    df.loc[l, 'BGValue'] = np.nan;

                                                    # writing into the file
                                                    df.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:], index=False);
# -----------------------------------------------------------#
#                 Medium Glycemic Food
# -----------------------------------------------------------#                                                
                                    # Same removal as the high glycaemic case.
                                    elif 1.5<=TypeFood<2.5:
                                        print("Medium Glycemic Food");
                                        dtH1 = datetime.datetime(2010, 12, 1,int(MTT[k][0:3]),int(MTT[k][4:6]),int(MTT[k][7:9]));
                                        dtH2= datetime.datetime(2010, 12, 1,int(MTT[k][0:3]),int(MTT[k][4:6]),int(MTT[k][7:9]))+datetime.timedelta(hours=4);# hours=timne needed to find the maximum 
# -----------------------------------------------------------#
#                 Next day condition
# -----------------------------------------------------------#                                    
                                        if  dtH2>datetime.datetime(2010, 12, 1,23,59,59):
                                            dtH3=datetime.datetime(2010, 12, 1,00,00,00);
                                            dtH4=dtH2;
                                            print("dtH2 modified");
                                            # print(dtH3.strftime('%H:%M:%S'));

                                            # Only if the next file is the next calendar day.
                                            if has_next_day(i):
                                                dataBG1 = pd.read_csv(str(path2)+Matrix[i+1][0]);
                                                BG_=len(dataBG1["Time"]);
                                                BGT_=dataBG1[["Time","BGValue"]];
                                            else:
                                                BG_=0;
                                            for l in range(BG_):
                                                    BGdt=datetime.datetime(2010, 12, 1,int(BGT_["Time"][l][0:3]),int(BGT_["Time"][l][4:6]),int(BGT_["Time"][l][7:9]));
                                                    if dtH3.strftime('%H:%M:%S')<=BGdt.strftime('%H:%M:%S')<=dtH4.strftime('%H:%M:%S'): 
                                                        # reading the csv file
                                                        df = pd.read_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i+1][0][29:]);
                                                        
                                                        # updating the column value/data
                                                        df.loc[l, 'Flag'] = 100;
                                                        df.loc[l, 'ValueCh']=df.loc[l, 'BGValue2'];   
                                                        df.loc[l, 'BGValue'] = np.nan;
                                                        
                                                        # writing into the file
                                                        df.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i+1][0][29:], index=False);
                                            dtH2=datetime.datetime(2010, 12, 1,23,59,59);
                                        BG_2=len(dataBG["Time"]); #Find important numbers
# -----------------------------------------------------------#
#                 Chop off
# -----------------------------------------------------------#                                    
                                        for l in range(BG_2):
                                                BGdt=datetime.datetime(2010, 12, 1,int(BGT["Time"][l][0:3]),int(BGT["Time"][l][4:6]),int(BGT["Time"][l][7:9]));
                                                if dtH1.strftime('%H:%M:%S')<=BGdt.strftime('%H:%M:%S')<=dtH2.strftime('%H:%M:%S'): 
                                                    # reading the csv file
                                                    df = pd.read_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:]);
                                                    
                                                    # updating the column value/data
                                                    df.loc[l, 'Flag'] = 100;
                                                    df.loc[l, 'ValueCh']=df.loc[l, 'BGValue2'];   
                                                    df.loc[l, 'BGValue'] = np.nan;
                                                    
                                                    # writing into the file
                                                    df.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:], index=False);
# -----------------------------------------------------------#
#                 Low Glycemic Glycemic Food
# -----------------------------------------------------------# 
                                    # Same removal as the high glycaemic case.
                                    elif 2.5<=TypeFood:
                                        print("Low Glycemic Food");
                                        dtH1 = datetime.datetime(2010, 12, 1,int(MTT[k][0:3]),int(MTT[k][4:6]),int(MTT[k][7:9]));
                                        dtH2= datetime.datetime(2010, 12, 1,int(MTT[k][0:3]),int(MTT[k][4:6]),int(MTT[k][7:9]))+datetime.timedelta(hours=4);# hours=timne needed to find the maximum 
# -----------------------------------------------------------#
#                 Next day condition
# -----------------------------------------------------------#                                    
                                        if  dtH2>datetime.datetime(2010, 12, 1,23,59,59):
                                            dtH3=datetime.datetime(2010, 12, 1,00,00,00);
                                            dtH4=dtH2;
                                            print("dtH2 modified");
                                            # print(dtH3.strftime('%H:%M:%S'));

                                            # Only if the next file is the next calendar day.
                                            if has_next_day(i):
                                                dataBG1 = pd.read_csv(str(path2)+Matrix[i+1][0]);
                                                BG_=len(dataBG1["Time"]);
                                                BGT_=dataBG1[["Time","BGValue"]];
                                            else:
                                                BG_=0;
                                            for l in range(BG_):
                                                    BGdt=datetime.datetime(2010, 12, 1,int(BGT_["Time"][l][0:3]),int(BGT_["Time"][l][4:6]),int(BGT_["Time"][l][7:9]));
                                                    if dtH3.strftime('%H:%M:%S')<=BGdt.strftime('%H:%M:%S')<=dtH4.strftime('%H:%M:%S'): 
                                                        # reading the csv file
                                                        df = pd.read_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i+1][0][29:]);
                                                        
                                                        # updating the column value/data
                                                        df.loc[l, 'Flag'] = 100;
                                                        df.loc[l, 'ValueCh']=df.loc[l, 'BGValue2'];   
                                                        df.loc[l, 'BGValue'] = np.nan;
                                                        
                                                        # writing into the file
                                                        df.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i+1][0][29:], index=False);
                                            dtH2=datetime.datetime(2010, 12, 1,23,59,59);
                                        BG_2=len(dataBG["Time"]); #Find important numbers
# -----------------------------------------------------------#
#                 Chop off
# -----------------------------------------------------------# 
                                        BG_2=len(dataBG["Time"]); #Find important numbers
                                        for l in range(BG_2):
                                                BGdt=datetime.datetime(2010, 12, 1,int(BGT["Time"][l][0:3]),int(BGT["Time"][l][4:6]),int(BGT["Time"][l][7:9]));
                                                if dtH1.strftime('%H:%M:%S')<=BGdt.strftime('%H:%M:%S')<=dtH2.strftime('%H:%M:%S'): 
                                                    # reading the csv file
                                                    df = pd.read_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:]);
                                                    
                                                    # updating the column value/data
                                                    df.loc[l, 'Flag'] = 100;
                                                    df.loc[l, 'ValueCh']=df.loc[l, 'BGValue2'];   
                                                    df.loc[l, 'BGValue'] = np.nan;   

                                                    # writing into the file
                                                    df.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:], index=False);

                                    else:
                                        print("Meal not found");
                                    # GlD.plot('Time',  'BGValue', kind='scatter');
                                    # GlD.plot('Time',  'BGValueF', kind='scatter');
                                    # plt.show();
                                # After each meal, save the day without BGValue2 as the
                                # _ToGraph file (overwritten by each later meal of the day).
                                df = pd.read_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:]);
                                del df['BGValue2']
                                df.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_ToGraph')+Matrix[i][0][29:], index=False);
                    else:
                        print("This event is one"+MK[k]);   
        # Bolus files are matched to the day but not used: placeholder with no effect.
        for j in range(len(filesBolus)):
            #Bolus
            if listVariables[4]+str(fileToRead)+str(' ')+Matrix[i][0][29:]  in filesBolus[j]:
                print("");
                #  print("exist: "+listVariables[4]+str(fileToRead)+str(' ')+filesBG[i][29:]);
except:
    print("file not found");

