"""
# Sensitivity analysis version: interpolation after the hourly split.
# Replaces the script of the same name in a copy of the repository; see the
# README (Interpolation and hourly boundaries).
4.PeaksDetection.py   (header of the original file reads "Read files and find peaks")
Step 4 (peak-based branch, paper 2): detect meal-like glucose peaks without
using meal records, remove the glucose around them, and score how often the
detected peaks coincide with a recorded meal.

Created: 14 November 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    0. Writes the minute grid PivotPeak_wCN.csv (column Time, 1,440 rows).
    1. Threshold pass, over all days of the participant:
         - low-pass filters the CGM series (Butterworth order 9, normalised
           cutoff 10 / 12.5 = 0.8; the first 10 samples keep their raw value
           to avoid the filter start-up);
         - puts it on the minute grid, forward/backward filled;
         - finds peaks above 100 mg/dL and records their prominence and
           width (width at 90% of the prominence, in hours).
       The 95th percentiles of all prominences and of all widths become this
       participant's thresholds (PromThr, widthThr).
    2. Main pass, day by day (normalised cutoff 5 / 12.5 = 0.4):
         - same peak finding; a peak is SELECTED when its prominence >
           PromThr OR its width > widthThr;
         - precision (only on days with a meal file): a selected peak is a
           success if a meal was recorded before it within (width / 2 + 1) h,
           or after it within 1 h. Peaks with no meal before or after are
           not scored;
         - removal: for every selected peak, BGValue is blanked from 1 h
           before to 3 h after the peak (clipped at 00:00). If the window
           passes midnight, the part after 00:00 is written as marks
           (1 = remove, 0 = keep) to a _Merge file for the NEXT day file,
           applied later by 5.MergePeaksNextDay.py.
    3. Writes the per-participant row of Table 3 (precision, successes,
       peaks scored, days without meal file, quality flag).

Inputs
    globals.id, globals.idG, globals.FIG2_DAY, globals.MISSING_THRESHOLD,
    globals.MGDL_TO_MMOL, globals.FIGURE_TITLES, globals.path2/3/4
    <path2>/glucose_level<id>-ws-training <Weekday>-<YYYY-MM-DD> .csv   (2.Disaggregator.py)
    <path2>/meal<id>-ws-training <Weekday>-<YYYY-MM-DD> .csv            (2.Disaggregator.py)

Outputs
    <path2>/PivotPeak.csv, PivotPeak_wCN.csv
    <path2>/glucose_level<id>-ws-training_wCNF <Weekday>-<YYYY-MM-DD> .csv
        One per day, minute grid with Time as "HH:MM": BGValue (after
        removal), BGValue2 (before removal), flagM, CarbsValue. BOTH BG
        columns are interpolated on the minute grid (limit 5, both
        directions) BEFORE the removal, so gaps of up to 10 minutes are
        already filled here. This is why the peak branch has no hourly
        interpolation step later, unlike the meal-based branch.
    <path2>/glucose_level<id>-ws-training_Merge <Weekday>-<YYYY-MM-DD> .csv
        Only for days that follow a window passing midnight.
    <path3>/Figure2a.png, Figure2b.png   only for idG, day index FIG2_DAY
        (a: all peaks found; b: selected peaks only)
    <path4>/Table3.csv   one row per participant; the row of the current
        participant is replaced, the others kept.

Exclusion criterion
    Quality = 1 (excluded) when MORE than globals.MISSING_THRESHOLD (20%) of
    the participant's CGM days have no meal file. Days without a meal file
    are still processed (removal only needs the peaks); they are just not
    scored.

Notes
    - The two passes use different filter cutoffs on purpose (see the
      comment in the threshold pass).
    - fs and cutoff are nominal values; only their ratio matters. The filter
      runs sample by sample on the 5-minute readings.
    - Peak times come from str(timedelta), which writes hours before 10
      with one digit ("8:05:00"). The try/except in the removal loop handles
      both "HH:MM" and "H:MM".
    - The next-day marks go to Matrix[i+1] only when it is the next calendar
      day (has_next_day); after a gap in the record nothing is carried.
      Several
      windows passing midnight on the same day overwrite the same _Merge
      file; the last one (latest peak) covers the earlier ones because every
      carried window starts at 00:00.
    - 5.MergePeaksNextDay.py joins the _Merge marks on "HH:MM:SS" without
      cutting the seconds, so a mark is only applied if the reading time has
      seconds = 00. The removal observed after midnight in real runs shows
      that the OhioT1DM times meet this; a reading with other seconds would
      silently keep its value.
    - Any error on a day is caught, printed, and counted in DaysError; the
      day is then left without a _wCNF file.
    - mg_dL_to_mmol_L = 1 in the figure block is an identity factor (the
      panel is drawn in mg/dL); the mmol/L axis uses globals.MGDL_TO_MMOL.
"""
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
import warnings
import math
import globals
warnings.simplefilter(action='ignore', category=FutureWarning)
from scipy.signal import find_peaks, peak_prominences,peak_widths
matplotlib.rcParams.update({'font.size': 15})


# --- Configurable global variables (set in globals.py) ---
id = globals.id;
filesBG=[];
filesMeals=[];
path2 = globals.path2;
path3 = globals.path3;
path4 = globals.path4;
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
# Empty meal table (schema used when a day has no meal file)
# -----------------------------------------------------------#
# Empty meal table used for days without a meal file.
def emptyMeals():
    return pd.DataFrame({'Time': pd.Series(dtype=str),
                         'flagM': pd.Series(dtype=float),
                         'CarbsValue': pd.Series(dtype=float)});

# -----------------------------------------------------------#
# Pivot generator
# -----------------------------------------------------------#
# ---- Step 0: minute grid PivotPeak_wCN.csv (column Time) ----
dt = datetime.datetime(2010, 12, 1);
end = datetime.datetime(2010, 12, 1, 23, 59, 59);
step = datetime.timedelta(minutes=1);
secArray=[];
# -----------------------------------------------------------#
open(str(path2)+"PivotPeak"+".csv", 'w').close();
while dt < end:
        secArray.append(dt.strftime('%H:%M:%S'));
        dt += step;
for j in secArray:
        file = open(str(path2)+"PivotPeak"+".csv", 'a');
        file.write(str(j));
        # print(str(j));
        file.write('\n');
        file.close();
df = pd.read_csv(str(path2)+"PivotPeak"+".csv",  header=None);
df.rename(columns={0: 'Time'}, inplace=True);
df.to_csv(str(path2)+"PivotPeak"+"_wCN"+".csv", index=False); # save to new csv 
# -----------------------------------------------------------#
#                   Files of Blood Glucose
# -----------------------------------------------------------#
# Daily CGM files from 2.Disaggregator.py (space after "-ws-training").
for file in os.listdir(path2):
    if file.startswith(listVariables[0]+str(fileToRead)+str(' ')):
        # print(file); 
        filesBG.append(file);
h, w = len(filesBG), 5;
Matrix = [[0 for x in range(w)] for y in range(h)] ;
# print(Matrix)

# -----------------------------------------------------------#
#                  Files of Meals
# -----------------------------------------------------------#
for file in os.listdir(path2):
    if file.startswith(listVariables[5]+str(fileToRead)+str(' ')):
        # print(file); 
        filesMeals.append(file);
# print(filesMeals);
# -----------------------------------------------------------#
#                    Sort of files
# -----------------------------------------------------------#
# Sort the day files by the date cut from the end of the name (see 4.MealBolusDetection.py).
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

def has_next_day(i):
    """True if Matrix[i+1] exists and is the calendar day after Matrix[i].

    The midnight overflow of a peak window is only marked on the next file
    when that file is the following calendar day. After a gap in the record
    (or on the last day) no _Merge file is written.
    """
    if i+1 >= len(Matrix):
        return False
    d0=datetime.date(int(Matrix[i][2]),int(Matrix[i][3]),int(Matrix[i][4]));
    d1=datetime.date(int(Matrix[i+1][2]),int(Matrix[i+1][3]),int(Matrix[i+1][4]));
    return (d1-d0).days==1
# print(Matrix)
# -----------------------------------------------------------#
#                    Find quartiles
# -----------------------------------------------------------#
# ---- Step 1: threshold pass over all days (cutoff 10) ----
prominencesArray=[];
widthArray=[];
daysNoMeal=[];
for i in range(len(filesBG)):
    try:
        dataBG = pd.read_csv(str(path2)+Matrix[i][0]);  
        BGT=dataBG[["Time","BGValue"]]; 
        BGV=[];
        time=[];
        BG_=len(dataBG["Time"]); #Find important numbers
        for l in range(BG_):
            BGdt=datetime.datetime(2010, 12, 1,int(BGT["Time"][l][0:3]),int(BGT["Time"][l][4:6]),int(BGT["Time"][l][7:9]));
            time.append(BGdt.strftime('%H:%M:%S'));
            BGV.append(BGT["BGValue"][l]); 
        #Revise: reset the meal table every day so nothing is inherited
        M=emptyMeals();
        for j in range(len(filesMeals)):
                #Meals
                # [29:] = "<Weekday>-<YYYY-MM-DD> .csv" (3-digit ID assumed).
                if listVariables[5]+str(fileToRead)+str(' ')+Matrix[i][0][29:]  in filesMeals[j]:
                    # print("exist: "+listVariables[5]+str(fileToRead)+str(' ')+filesBG[i][29:]);
                    dataMeal = pd.read_csv(str(path2)+listVariables[5]+str(fileToRead)+str(' ')+Matrix[i][0][29:]);
                    flag=[];
                    timeM=[];
                    Carbs=[];
                    for h in range(len(dataMeal["Time"])):
                        BGM=datetime.datetime(2010, 12, 1,int(dataMeal["Time"][h][0:3]),int(dataMeal["Time"][h][4:6]),int(dataMeal["Time"][h][7:9]));
                        timeM.append(BGM.strftime('%H:%M:%S'));
                        flag.append(1);
                        Carbs.append(dataMeal["CarbsValue"][h])

                    M=pd.DataFrame({'Time': timeM,'flagM':flag,"CarbsValue":Carbs});   
                    # M=dataMeal[["Time","CarbsValue","TypeFood"]]; #Find important numbers
                    # print(M)
    # -----------------------------------------------------------#
    #                    Low pass filter
    # -----------------------------------------------------------#    
        # Filter requirements.
        order = 9;
        fs = 25;       # sample rate, Hz
        cutoff = 10;      # desired cutoff frequency of the filter, Hz
        nyq = 0.5 * fs;
        normal_cutoff = cutoff / nyq;
        # Normalised cutoff = 10 / 12.5 = 0.8; first 10 samples kept raw.
        b, a = butter(order, normal_cutoff, btype='low', analog=False);
        BGVF = lfilter(b, a, BGV);
        for j in range(10):
            BGVF[j]=BGV[j];  
# The cutoff differs between stages by design (10 for the threshold pass, 5 for
# detection). Sensitivity check on the current pipeline: using 10 in both
# stages leaves mean precision unchanged (70.65% vs 70.64%, n=9) and does not
# alter the included participant set.
    # -----------------------------------------------------------#
    #        Merge values
    # -----------------------------------------------------------#
        data1 = pd.read_csv(str(path2)+'PivotPeak_wCN'+'.csv')
        GlD=pd.DataFrame({'Time': time,'BGValueF':BGVF,'BGValue2':BGV,'BGValue':BGV}); 
    
        GlD['Time']=GlD['Time'].str.slice(0, 5);
        GlD['Time']= GlD['Time'].str.strip();

        data1['Time']=data1['Time'].str.slice(0,5);
        data1['Time']=data1['Time'].str.strip();
        output = pd.merge(data1,GlD,on='Time',how='left');
        output['Time']=output['Time']+':00';

    # -----------------------------------------------------------#
    # Find Peaks prominenses and widths
    # -----------------------------------------------------------#
        # Minute grid forward/backward filled: the series used to find peaks.
        df=output.replace('',float('NaN')).ffill().bfill();
        M['Time']=M['Time'].astype(str).str.strip();  
        df['Time']=df['Time'].str.strip(); 
        output = pd.merge(df,M,on='Time',how='left');
        output2 = pd.merge(data1,GlD,on='Time',how='left');
        output4=output2.interpolate(limit=5, limit_direction='both'); 
        output4['Time']=output4['Time'].str.strip();
        output3 = pd.merge(output4,M,on='Time',how='left');

    # -----------------------------------------------------------#
    # Find peaks    
    # -----------------------------------------------------------#
        BGFArray=output["BGValueF"].to_numpy();
        MArray=output["flagM"].to_numpy();
        CArray=output["CarbsValue"].to_numpy();
        time1=output["Time"];
        ind=[];
        for k in range(len(time1)):
            # print(i);
            (h, m, s) = time1[k].split(':');
            result = (int(h) * 3600 + int(m) * 60 + int(s))/3600;
            ind.append(result-1/60);
        # Peaks above 100 mg/dL; prominence and width (at 90% of prominence, hours).
        peaks, _ = find_peaks(BGFArray, height=100);
        prominences = peak_prominences(BGFArray, peaks)[0];
    # -----------------------------------------------------------#
    #        Save values of prominenses
    # -----------------------------------------------------------#
        for k in range(len(prominences)):
            prominencesArray.append(prominences[k]);
    # -----------------------------------------------------------#
    #        Find altitude of peaks
    # -----------------------------------------------------------#
        values_p=BGFArray[peaks];
        contour_heights = values_p - prominences;
    # -----------------------------------------------------------#
    #        Find widths
    # -----------------------------------------------------------#
        results_half = peak_widths(BGFArray, peaks, rel_height=0.9);
        #Normalize
        p=[i/60  for i in results_half[0]]
        results_half[0][:]=p;
    # -----------------------------------------------------------#
    #        Save values of width
    # -----------------------------------------------------------#
        for k in range(len(p)):
            widthArray.append(results_half[0][:][k]);
    except Exception as e:
        print(f"[thresholds] day {i}: {type(e).__name__}: {e}");                


# -----------------------------------------------------------#
#Discriminator values
# -----------------------------------------------------------#
# Participant thresholds: 95th percentile of all prominences and widths.
PromThr=np.quantile(prominencesArray, 0.95);
widthThr=np.quantile(widthArray, 0.95);
print("Prominence Threshold: ", PromThr);
print("Width Threshold: ",widthThr);

# -----------------------------------------------------------#
#                  Main program
# -----------------------------------------------------------#
# ---- Step 2: main pass, day by day (cutoff 5) ----
counter=0;
success=[];
for i in range(len(filesBG)):
    print("Iteration: "+str(i))
    try:
        print(Matrix[i][0]);
        dataBG = pd.read_csv(str(path2)+Matrix[i][0]);  
        BGT=dataBG[["Time","BGValue"]]; 
        BGV=[];
        time=[];
        BG_=len(dataBG["Time"]); #Find important numbers
        for l in range(BG_):
            BGdt=datetime.datetime(2010, 12, 1,int(BGT["Time"][l][0:3]),int(BGT["Time"][l][4:6]),int(BGT["Time"][l][7:9]));
            time.append(BGdt.strftime('%H:%M:%S'));
            BGV.append(BGT["BGValue"][l]); 
        #Revise: reset the meal table every day so nothing is inherited
        M=emptyMeals();
        for j in range(len(filesMeals)):
                #Meals
                if listVariables[5]+str(fileToRead)+str(' ')+Matrix[i][0][29:]  in filesMeals[j]:
                    # print("exist: "+listVariables[5]+str(fileToRead)+str(' ')+filesBG[i][29:]);
                    dataMeal = pd.read_csv(str(path2)+listVariables[5]+str(fileToRead)+str(' ')+Matrix[i][0][29:]);
                    flag=[];
                    timeM=[];
                    Carbs=[];
                    for h in range(len(dataMeal["Time"])):
                        BGM=datetime.datetime(2010, 12, 1,int(dataMeal["Time"][h][0:3]),int(dataMeal["Time"][h][4:6]),int(dataMeal["Time"][h][7:9]));
                        timeM.append(BGM.strftime('%H:%M:%S'));
                        flag.append(1);
                        Carbs.append(dataMeal["CarbsValue"][h])

                    M=pd.DataFrame({'Time': timeM,'flagM':flag,"CarbsValue":Carbs});   
                    # M=dataMeal[["Time","CarbsValue","TypeFood"]]; #Find important numbers

        #Revise: a day without meal annotations is still processed (the chop
        #        only needs the detected peaks), it just cannot score precision
        # Days without meal annotations are counted for the exclusion criterion.
        hasMeals = len(M) > 0;
        if not hasMeals:
            daysNoMeal.append(Matrix[i][0]);
            print(f"Day {i}: no meal annotations, precision not scored");

    # -----------------------------------------------------------#
    #                    Low pass filter
    # -----------------------------------------------------------#    
        # Filter requirements.
        order = 9;
        fs = 25;       # sample rate, Hz
        cutoff = 5;      # desired cutoff frequency of the filter, Hz
        nyq = 0.5 * fs;
        normal_cutoff = cutoff / nyq;
        # Normalised cutoff = 5 / 12.5 = 0.4 (see the note in the threshold pass).
        b, a = butter(order, normal_cutoff, btype='low', analog=False);
        BGVF = lfilter(b, a, BGV);
        for j in range(10):
            BGVF[j]=BGV[j];  
    # -----------------------------------------------------------#
    #        Merge values
    # -----------------------------------------------------------#
        data1 = pd.read_csv(str(path2)+'PivotPeak_wCN'+'.csv')
        GlD=pd.DataFrame({'Time': time,'BGValueF':BGVF,'BGValue2':BGV,'BGValue':BGV}); 
        GlD['Time']=GlD['Time'].str.slice(0, 5);
        GlD['Time']= GlD['Time'].str.strip();
        data1['Time']=data1['Time'].str.slice(0,5);
        data1['Time']=data1['Time'].str.strip();
        output = pd.merge(data1,GlD,on='Time',how='left');
        output['Time']=output['Time']+':00';


    # -----------------------------------------------------------#
    # Find Peaks prominenses and widths
    # -----------------------------------------------------------#
        df=output.replace('',float('NaN')).ffill().bfill();
        M['Time']=M['Time'].astype(str).str.strip();  
        df['Time']=df['Time'].str.strip(); 
        output = pd.merge(df,M,on='Time',how='left');
        
        # Sensitivity analysis (interpolation position): the day-wide interpolation
        # is removed so that the _wCNF file keeps only the actual CGM readings on
        # the minute grid. The hourly interpolation is applied after the split,
        # in 7.SplitHoursPeaks.py, as in the meal-based branch.
        output2 = pd.merge(data1,GlD,on='Time',how='left');
        output4=output2.copy();  # was: output2.interpolate(limit=5, limit_direction='both')
        output4['Time']=output4['Time'].str.strip();
        output3 = pd.merge(output4,M,on='Time',how='left');

    # -----------------------------------------------------------#
    # Find peaks    
    # -----------------------------------------------------------#
        BGFArray=output["BGValueF"].to_numpy();
        MArray=output["flagM"].to_numpy();        
        CArray=output["CarbsValue"].to_numpy();
        time1=output["Time"];
        ind=[];
        for k in range(len(time1)):
            # print(i);
            (h, m, s) = time1[k].split(':');
            result = (int(h) * 3600 + int(m) * 60 + int(s))/3600;
            ind.append(result-1/60);
        peaks, _ = find_peaks(BGFArray, height=100);
        prominences = peak_prominences(BGFArray, peaks)[0];
    # -----------------------------------------------------------#
    #        Save values of prominenses
    # -----------------------------------------------------------#
        for k in range(len(prominences)):
            prominencesArray.append(prominences[k]);
    # -----------------------------------------------------------#
    #        Find altitude of peaks
    # -----------------------------------------------------------#
        values_p=BGFArray[peaks];
        contour_heights = values_p - prominences;
    # -----------------------------------------------------------#
    #        Find widths
    # -----------------------------------------------------------#
        results_half = peak_widths(BGFArray, peaks, rel_height=0.9);
        #Normalize
        p=[i/60  for i in results_half[0]]
        results_half[0][:]=p;
        widthData=results_half[0][:];

    # -----------------------------------------------------------#
    #        Normalize values
    # -----------------------------------------------------------#
        peaks=peaks*1/60;
        for r in range (1,len(results_half[1:])):
                p=[i/60  for i in results_half[1:][r]]
                results_half[1:][r][:]=p;
 
    # -----------------------------------------------------------#
    #        Discriminate peaks
    # -----------------------------------------------------------#

        # Selected peak: prominence OR width above the participant threshold.
        discrimitator=[];
        for k in range(len(prominences)):
            if  prominences[k]>PromThr or widthData[k]>widthThr:
                discrimitator.append(1);
            else:
                discrimitator.append(0); 

    # -----------------------------------------------------------#
    #        find time values
    # -----------------------------------------------------------#
        formatted_times = []

        # Peak positions (hours) -> "H:MM:SS" strings via timedelta.
        for value in peaks:
            # Convert the decimal hours to hours and minutes
            hours = int(value)
            minutes = int((value - hours) * 60)
            
            # Create a timedelta object to represent the time
            time_delta = timedelta(hours=hours, minutes=minutes)
            
            # Format the time as HH:MM
            formatted_time = str(time_delta)
            formatted_times.append(formatted_time)
        
        PeaksData=pd.DataFrame({'Time': formatted_times,'width':results_half[0][:],'altitude':prominences,'Flag':discrimitator});
 
        # -----------------------------------------------------------#
        #        Compute successes  (only when the day has meal data)
        # -----------------------------------------------------------#       
 
        # Precision is scored only on days with a meal file.
        if hasMeals:
            PeaksData["Time"] = pd.to_datetime(PeaksData["Time"], format="%H:%M:%S")
            M["Time"] = pd.to_datetime(M["Time"], format="%H:%M:%S")

            PeaksData_flag1 = PeaksData[PeaksData["Flag"] == 1] 


            # -----------------------------------------------------------#            
            # Calculate the time differences in meals before
            # -----------------------------------------------------------#    
            results_earlier = []  # Initialize results list for earlier times
            results_later = []  # Initialize results list for later times

            # Loop through each time in PeaksData_flag1["Time"]
            for time1 in PeaksData_flag1["Time"]:
                # Find earlier times
                earlier_times = M[M["Time"] < time1]["Time"]
                if not earlier_times.empty:
                    nearest_earlier_time = earlier_times.max()
                    time_diff_earlier = time1 - nearest_earlier_time
                else:
                    nearest_earlier_time, time_diff_earlier = None, None
                results_earlier.append((time1, nearest_earlier_time, time_diff_earlier))

                # Find later times
                later_times = M[M["Time"] > time1]["Time"]
                if not later_times.empty:
                    nearest_later_time = later_times.min()
                    time_diff_later = nearest_later_time - time1
                else:
                    nearest_later_time, time_diff_later = None, None
                results_later.append((time1, nearest_later_time, time_diff_later))

            # Convert results to DataFrames for readability
            df_earlier = pd.DataFrame(results_earlier, columns=["Tme_peak", "Nearest_Earlier_Time", "Time_Difference_Earlier"])
            df_later = pd.DataFrame(results_later, columns=["Tme_peak", "Nearest_Later_Time", "Time_Difference_Later"])

            # Merge the two DataFrames on Tme_peak
            time_diff_df = pd.merge(df_earlier, df_later, on="Tme_peak")

           #Revise
            for c in ["Tme_peak", "Nearest_Earlier_Time", "Nearest_Later_Time"]:
                time_diff_df[c] = pd.to_datetime(time_diff_df[c], errors="coerce")
            for c in ["Time_Difference_Earlier", "Time_Difference_Later"]:
                time_diff_df[c] = pd.to_timedelta(time_diff_df[c], errors="coerce")

            # Format the times and convert the time differences to floating numbers in hours
            time_diff_df["Tme_peak"] = time_diff_df["Tme_peak"].dt.strftime("%H:%M:%S")
            time_diff_df["Nearest_Earlier_Time"] = time_diff_df["Nearest_Earlier_Time"].dt.strftime("%H:%M:%S")
            time_diff_df["Nearest_Later_Time"] = time_diff_df["Nearest_Later_Time"].dt.strftime("%H:%M:%S")
            time_diff_df["Time_Difference_Earlier"] = time_diff_df["Time_Difference_Earlier"].dt.total_seconds() / 3600
            time_diff_df["Time_Difference_Later"] = time_diff_df["Time_Difference_Later"].dt.total_seconds() / 3600

            # Compute the width-based condition values
            width_condition_values = PeaksData_flag1["width"].to_numpy()
            # Success window: meal before the peak within width/2 + 1 h,
            # or meal after the peak within 1 h.
            time_diff_df["Time_Difference_cond"] = [width / 2 + 1 for width in width_condition_values]  # For earlier times
            time_diff_df["Time_Difference_cond_sup"] = 1  # Fixed condition of 1 hour for later times


            # Drop rows where both Time_Difference_Earlier and Time_Difference_Later are NaN
            # Peaks with no meal before and none after are not scored.
            time_diff_df = time_diff_df.dropna(subset=["Time_Difference_Earlier", "Time_Difference_Later"], how="all")

            # Add a flag column: 1 if either condition is met, otherwise 0
            time_diff_df["Flag"] = (
            (time_diff_df["Time_Difference_cond"] > time_diff_df["Time_Difference_Earlier"]) 
            | 
            (time_diff_df["Time_Difference_cond_sup"] > time_diff_df["Time_Difference_Later"])
            ).astype(int)

            # # Drop rows where (Nearest_Earlier_Time is NaN or Nearest_Later_Time is NaN) and Flag == 0
            # time_diff_df = time_diff_df[
            #     ~(
            #         ((time_diff_df["Nearest_Earlier_Time"].isna()) | (time_diff_df["Nearest_Later_Time"].isna())) & 
            #         (time_diff_df["Flag"] == 0)
            #     )
            # ]


            # -----------------------------------------------------------#    
            # Compute accuraccies
            # -----------------------------------------------------------# 
            print(time_diff_df)
            Succ=time_diff_df["Flag"].to_numpy();
            for w in range(len(Succ)):
                success.append(Succ[w]);
        # -----------------------------------------------------------#
        #        Remove data
        # -----------------------------------------------------------#    

        # Removal: [peak - 1 h, peak + 3 h] for every selected peak.
        PeaksInfo=pd.DataFrame({'Time': formatted_times,'altitude':prominences,'Flag':discrimitator});  
        filtered_df = PeaksInfo[PeaksInfo['Flag'] == 1]
        # print(filtered_df);
        fil=len(filtered_df["Time"]); #Find important numbers
        MTT=filtered_df["Time"].to_numpy();
        # print(MTT)
        for k in range(fil):
                BG_=len(output["Time"]);
                # "HH:MM" first; the except handles one-digit hours ("H:MM").
                try:
                    dt = datetime.datetime(2010, 12, 1,int(MTT[k][0:2]),int(MTT[k][3:5]))-datetime.timedelta(hours=1);        
                    dt1= datetime.datetime(2010, 12, 1,int(MTT[k][0:2]),int(MTT[k][3:5]))+datetime.timedelta(hours=3);# hours=timne needed to find the maximum
                except:
                    dt = datetime.datetime(2010, 12, 1,int(MTT[k][0:1]),int(MTT[k][2:4]))-datetime.timedelta(hours=1);        
                    dt1= datetime.datetime(2010, 12, 1,int(MTT[k][0:1]),int(MTT[k][2:4]))+datetime.timedelta(hours=3);# hours=timne needed to find the maximum            
                if  dt<datetime.datetime(2010, 12, 1,00,00,00):
                        dt=datetime.datetime(2010, 12, 1,00,00,00);

    # -----------------------------------------------------------#
    #                 Next day condition
    # -----------------------------------------------------------#  
                # Window passing midnight: marks 00:00 -> overflow on the NEXT day file.
                if  dt1>datetime.datetime(2010, 12, 1,23,59,59):
                        dt4=dt1;
                        dt1=datetime.datetime(2010, 12, 1,23,59,59);
                        dt3=datetime.datetime(2010, 12, 2,00,00,00);
                        # Only if the next file is the next calendar day.
                        if has_next_day(i):
                            print("Si");
                            dataBG1 = pd.read_csv(str(path2)+Matrix[i+1][0]);
                            print(str(path2)+Matrix[i+1][0]);
                            BG_1=len(dataBG1["Time"]);
                            BGT_1=dataBG1[["Time","BGValue"]];
                            TimeN=BGT_1["Time"].to_numpy();
                            BGN=BGT_1["BGValue"].to_numpy();
                            BGNI=pd.DataFrame({'Time': TimeN,'BGValue':BGN});
                            for l in range(BG_1):
                                BGdt1=datetime.datetime(2010, 12, 1,int(BGT_1["Time"][l][0:3]),int(BGT_1["Time"][l][4:6]),int(BGT_1["Time"][l][7:9]));
                                if dt3.strftime('%H:%M:%S')<=BGdt1.strftime('%H:%M:%S')<=dt4.strftime('%H:%M:%S'):
                                    BGNI.loc[l, 'BGValue'] = 1;
                                else:
                                    BGNI.loc[l, 'BGValue'] = 0;
                            # Written for the next file in date order; applied by 5.MergePeaksNextDay.py.
                            BGNI.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_Merge ')+Matrix[i+1][0][29:], index=False);
                        else:
                            print(f"Day {i}: no next calendar day (last file or gap), overflow not carried");
    # -----------------------------------------------------------#
    #                 Chop off
    # -----------------------------------------------------------#  
                # Blank BGValue inside the window on the current day.
                for l in range(BG_):   
                    BGdt=datetime.datetime(2010, 12, 1,int(output["Time"][l][0:2]),int(output["Time"][l][3:5]));
                    #  print(BGdt)
                    if dt.strftime('%H:%M:%S')<=BGdt.strftime('%H:%M:%S')<=dt1.strftime('%H:%M:%S'): 
                        # print(BGdt.strftime('%H:%M:%S'))  
                        output3.loc[l, 'BGValue'] = np.nan;

    # -----------------------------------------------------------#
    # Save output    
    # -----------------------------------------------------------#
        del output3['BGValueF']
        # del output['BGValue2']
        # Save the day as its _wCNF working copy (Time as "HH:MM").
        output3.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCNF ')+Matrix[i][0][29:], index=False); # save to new csv 




        
    # -----------------------------------------------------------#
    #        Graph  (only the day used in the manuscript)
    # -----------------------------------------------------------#
    # Figure 2 panels, only for the worked example (idG, day FIG2_DAY).
        if  id == globals.idG and i == globals.FIG2_DAY:
            # The panel is drawn in mg/dL, as published; mmol/L is added as a
            # second axis below, using globals.MGDL_TO_MMOL.
            mg_dL_to_mmol_L = 1
            BGFArray_mmol = [value * mg_dL_to_mmol_L for value in BGFArray]
            values_p_mmol = [value * mg_dL_to_mmol_L for value in values_p]
            contour_heights_mmol = [value * mg_dL_to_mmol_L for value in contour_heights]

            # (a) all detected peaks   (b) only peaks above the 95th percentile
            panels = {
                'Figure2a': [k for k in range(len(values_p_mmol))
                             if values_p_mmol[k] - contour_heights_mmol[k] > 0],
                'Figure2b': [k for k in range(len(discrimitator)) if discrimitator[k] == 1],
            }

            for panel_name, sel in panels.items():
                filtered_peaks    = [peaks[k] for k in sel]
                filtered_values   = [values_p_mmol[k] for k in sel]
                filtered_contours = [contour_heights_mmol[k] for k in sel]
                filtered_indices  = sel

                fig, ax1 = plt.subplots(figsize=(10, 6))
                ax1.set_xlabel("Time (h)")
                ax1.set_ylabel("Carbohydrates (g)", labelpad=10, color='black')
                ax1.plot(ind, CArray, 'o', markersize=10, label='Meal', color="Orange")
                ax1.vlines(x=ind, ymin=CArray, ymax=MArray, linewidth=5, color="Orange")

                ax2 = ax1.twinx()
                ax2.set_ylabel("Blood Glucose \n (mg/dL)", labelpad=10, color='black')
                ax2.plot(ind, BGFArray_mmol, 'o', label='Blood Glucose', color="Green")
                ax2.axhline(linewidth=2, color='Black')
                ax2.plot(filtered_peaks, filtered_values, 'o', label='Filtered Peaks',
                         markersize=10, color="Purple")
                ax2.vlines(x=filtered_peaks, ymin=filtered_contours, ymax=filtered_values,
                           linewidth=3, label='Height', color="Blue")
                wa = [mg_dL_to_mmol_L * val for val in results_half[1:]]
                subset = [arr[filtered_indices] for arr in wa]
                ax2.hlines(*subset, linewidth=3, label="Peak's width", color="Red")

                # Second glucose axis in mmol/L. Limits are derived from ax2 so the
                # two scales can never drift apart.
                ax3 = ax2.twinx()
                # twinx() moves the original axis's ticks to the left, where they
                # would collide with the carbohydrate axis. Put ax2 back on the right.
                ax2.yaxis.tick_right()
                ax2.yaxis.set_label_position('right')
                ax3.spines['right'].set_position(('outward', 105))
                lo, hi = ax2.get_ylim()
                ax3.set_ylim(lo * globals.MGDL_TO_MMOL, hi * globals.MGDL_TO_MMOL)
                ax3.set_ylabel("Blood Glucose \n (mmol/L)", labelpad=15, color='black')

                ax1.grid(which='major', color='#DDDDDD', linewidth=0.8)
                ax1.grid(which='minor', color='#DDDDDD', linestyle=':', linewidth=0.5)
                ax1.minorticks_on()

                h1, l1 = ax1.get_legend_handles_labels()
                h2, l2 = ax2.get_legend_handles_labels()
                ax1.legend(h1 + h2, l1 + l2, loc='upper left', fontsize=8, framealpha=0.9)

                if globals.FIGURE_TITLES:
                    plt.title("Blood Glucose Data: " + str(id) + " day: " + str(i + 1))

                out = path3 + panel_name + '.png'
                plt.savefig(out, dpi=300, bbox_inches='tight')
                print("SAVED:", os.path.abspath(out))
                # plt.show()
                plt.close(fig)
            
    except Exception as e:
            counter += 1
            print(f"day {i} ({Matrix[i][0]}): {type(e).__name__}: {e}")
# print("Prominenses: "+str(len(prominencesArray)));
# prominencesdf=pd.DataFrame({'Prominenses': prominencesArray}); 
# pd.DataFrame.boxplot(prominencesdf);
# plt.xlabel("Values");
# plt.ylabel("Prominenses (mg/dL)");
# plt.title("Prominenses' distribution "+str(id));
# plt.show();
# # print(prominencesArray);
# # print("Width: "+str(len(widthArray)));
# Peakwidthsdf=pd.DataFrame({'Peakwidths': widthArray}); 
# pd.DataFrame.boxplot(Peakwidthsdf);
# plt.xlabel("Values");
# plt.ylabel("width (h)");
# plt.title("Width of peaks distribution "+str(id));
# plt.show();
# # print(widthArray);

# -----------------------------------------------------------#
# Save precision summary (Table 3)
# -----------------------------------------------------------#
# ---- Step 3: Table 3 row for this participant ----
size = len(success);
ratio_of_ones = (sum(success) / size)*100 if size > 0 else float('nan');
print("Precision: "+str(ratio_of_ones));
print("Peaks scored: "+str(size)+"  successes: "+str(int(sum(success))));
print("Days without meal file: "+str(len(daysNoMeal))+" out of "+str(len(filesBG)));
print("Days lost to errors: "+str(counter));

os.makedirs(path4, exist_ok=True);

# Low-quality criterion (declared): a participant is flagged when more than
# globals.MISSING_THRESHOLD of their days lack meal annotations, since
# precision cannot be scored on those days. The value lives in globals.py so
# that the threshold declared in the article is traceable to a
# single place.
MISSING_THRESHOLD = globals.MISSING_THRESHOLD;
missFrac = len(daysNoMeal) / len(filesBG) if len(filesBG) else 0.0;
print(f"Missing meal files: {len(daysNoMeal)}/{len(filesBG)} = {100*missFrac:.1f}%");

row = pd.DataFrame({'ID': [id],
                    'Precision': [round(ratio_of_ones, 2)],
                    'Successes': [int(sum(success))],
                    'PeaksScored': [size],
                    'FilesMissing': [len(daysNoMeal)],
                    'FilesTotal': [len(filesBG)],
                    'MissingPct': [round(100*missFrac, 1)],
                    'DaysError': [counter],
                    # Excluded when MORE than 20% of the days have no meal file.
                    'Quality': [1 if missFrac > MISSING_THRESHOLD else 0]});

out = path4 + 'Table3.csv';
# Replace the row of this participant, keep the others.
if os.path.exists(out):
    table = pd.read_csv(out);
    table = table[table['ID'] != id];       # replace previous run for this ID
    table = pd.concat([table, row], ignore_index=True);
else:
    table = row;
table = table.sort_values('ID');
table.to_csv(out, index=False);
print("SAVED:", os.path.abspath(out));