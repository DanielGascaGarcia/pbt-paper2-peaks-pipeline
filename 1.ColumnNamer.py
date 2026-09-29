"""
1.ColumnNamer.py
Step 1 of the pipeline: add column names to the CSV files written by
0.Parser.py.

Created: 1 November 2022
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    For each data type, reads <tag><id>-ws-training.csv (no header), gives
    its columns names that match the field layout written by the parser, and
    saves the result as <tag><id>-ws-training_wCN.csv ("with column names").

Inputs
    globals.id, globals.path1, globals.path2
    <path1>/<id>-ws-training.xml               (only used to list the element tags)
    <path2>/<tag><id>-ws-training.csv          (0.Parser.py)

Outputs
    <path2>/<tag><id>-ws-training_wCN.csv      one per data type
    Input of 2.Disaggregator.py.

IMPORTANT - positional assumption (same as 2.Disaggregator.py)
    The names are chosen by the POSITION of the element under the XML root
    (x == 0, 1, 2, ...), not by its tag. The labels next to each branch
    describe the OhioT1DM order:
        0 glucose_level, 1 finger_stick, 2 basal, 3 temp_basal, 4 bolus,
        5 meal, 6 sleep, 7 work, 8 stressors, 9 hypo_event, 10 illness,
        11 exercise, 12 basis_heart_rate, 13 basis_gsr,
        14 basis_skin_temperature, 15 basis_air_temperature, 16 basis_steps,
        17 basis_sleep
    An XML with the same tags in another order, or with an element missing,
    gets wrong column names without any error.

Notes
    - Each branch is wrapped in try/except: if a file is missing or cannot be
      read (for example rows with different numbers of fields), the _wCN file
      is not written and only 'Not valid' is printed.
    - Some names here differ from the headers that 2.Disaggregator.py writes
      for the per-day files (e.g. 'GRSValue' here, 'GSRValue' there). This
      does not matter downstream: the Disaggregator skips this header and
      writes its own.
    - Same as in the Disaggregator: bolus has 'TimeStamp1' twice (the second
      should be 'TimeStamp2'), and air temperature is called 'BSkinValue'.
"""

# Importing libraries

import xml.etree.ElementTree as ET
import datetime
import calendar
import os
import csv
import pandas as pd
import globals

# --- Configurable global variables (set in globals.py) ---

id = globals.id;
fileToRead=str(id)+"-ws-training";
path1=globals.path1;
path2=globals.path2;

# The XML is read only to get the list of element tags.
ohioTree = ET.parse(str(path1)+str(fileToRead)+'.xml');
ohioRoot = ohioTree.getroot();

elemList = [];

for child in ohioRoot:
    print(child.tag, child.attrib);
    elemList.append(child.tag);

#Duplicities are removed
elemList = list(set(elemList));

# Printing the results
print(len(elemList));


# One branch per data type, chosen by position (see header). Every branch
# reads the parsed CSV, renames columns 0..n and saves the _wCN file.
for x in range(len(elemList)):
    print (x);
     # Blood Glucose
    if  x==0:
        try: 
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key',3:'Weekday',4:'Time',5:'TimeVariable',6:'TimeStamp',7:'Value',8:'BGValue'}, inplace=True);
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv 
        except:
            print('Not valid');
    # Finger stick
    elif x==1:
        try: 
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key',3:'Weekday',4:'Time',5:'TimeVariable',6:'TimeStamp',7:'Value',8:'FingerValue'}, inplace=True);
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
    # Basal 
    elif x==2:
        try:
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key',3:'Weekday',4:'Time',5:'TimeVariable',6:'TimeStamp',7:'Value',8:'BasalValue'}, inplace=True);
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
    # Temp_basal 
    elif x==3:
        try:
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key1',3:'Weekday1',4:'Time1',5:'TimeVariable1',6:'TimeStamp1', 7:'key2',8:'Weekday2',9:'Time2',10:'TimeVariable2',11:'TimeStamp2',12:'Type',13:'Value',14:'TempBasalValue'}, inplace=True);
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
    # Bolus 
    elif x==4:
        try:
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key1',3:'Weekday1',4:'Time1',5:'TimeVariable1',6:'TimeStamp1', 7:'Group2', 8:'key2',9:'Weekday2',10:'Time2',11:'TimeVariable2',12:'TimeStamp1',13:'Type',14:'Dose',15:'DoseType',16:'BolusValue',17:'CarbInput',18:'CarbInputValue'}, inplace=True);
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
    # Meal
    elif x==5:
        try:
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key',3:'Weekday',4:'Time',5:'TimeVariable',6:'TimeStamp',7:'Type',8:'TypeFood',9:'Carbs',10:'CarbsValue'}, inplace=True);
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
    # Sleep
    elif x==6:
        try:
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key1',3:'Weekday1',4:'Time1',5:'TimeVariable1',6:'TimeStamp1',7:'Group2',8:'key2',9:'Weekday2',10:'Time2',11:'TimeVariable2',12:'TimeStamp2',13:'Quality',14:'QualityValue'}, inplace=True);
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
    # Work 
    elif x==7:
        try:
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key1',3:'Weekday1',4:'Time1',5:'TimeVariable1',6:'TimeStamp1',7:'Group2',8:'key2',9:'Weekday2',10:'Time2',11:'TimeVariable2',12:'TimeStamp2',13:'Intensity',14:'IntensityValue'}, inplace=True); 
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
 
    # Stressors 
    elif x==8:
        try:
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key1',3:'Weekday1',4:'Time1',5:'TimeVariable1',6:'TimeStamp1',7:'Type',8:'typeValue',9:'Description',10:'DescriptionValue'}, inplace=True);
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
 
    # Hypo_event 
    elif x==9:
        try:
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key',3:'Weekday',4:'Time',5:'TimeVariable',6:'TimeStamp'}, inplace=True);
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
    
    # Illness 
    elif x==10:
        try:
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key1',3:'Weekday1',4:'Time1',5:'TimeVariable1',6:'TimeStamp1',7:'Type',8:'typeValue',9:'Description',10:'DescriptionValue'}, inplace=True);
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
    
    #  Exercise
    elif x==11:
        try:
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key1',3:'Weekday1',4:'Time1',5:'TimeVariable1',6:'TimeStamp1',7:'Intensity',8:'IntensityValue',9:'Type',10:'TypeValue',11:'Duration',12:'DurationValue',13:'Competitive',14:'CompetitiveValue'}, inplace=True);
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
    # Basis_heart_rate 
    elif x==12:
        try:
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key',3:'Weekday',4:'Time',5:'TimeVariable',6:'TimeStamp',7:'Value',8:'BHValue'}, inplace=True);
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
    # Basis_gsr
    elif x==13:
        try:
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key',3:'Weekday',4:'Time',5:'TimeVariable',6:'TimeStamp',7:'Value',8:'GRSValue'}, inplace=True);
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
    # Basis_skin_temperature 
    elif x==14:
        try:
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key',3:'Weekday',4:'Time',5:'TimeVariable',6:'TimeStamp',7:'Value',8:'BSTValue'}, inplace=True);
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
    # Basis_air_temperature 
    elif x==15:
        try:
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key',3:'Weekday',4:'Time',5:'TimeVariable',6:'TimeStamp',7:'Value',8:'BSkinValue'}, inplace=True);
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
 
    # Basis_steps 
    elif x==16:
        try:
            print(ohioRoot[x].tag);
            df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
            df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key',3:'Weekday',4:'Time',5:'TimeVariable',6:'TimeStamp',7:'Value',8:'BStepsValue'}, inplace=True);
            df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
    # Basis_sleep 
    elif x==17:
        try:    
           print(ohioRoot[x].tag);
           df = pd.read_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv",  header=None);
           df.rename(columns={0: 'Variable', 1: 'Group', 2: 'Key1',3:'Weekday1',4:'Time1',5:'TimeVariable1',6:'TimeStamp1', 7:'Group2',8:'key2',9:'Weekday2',10:'Time2',11:'TimeVariable2',12:'TimeStamp2',13:'Quality',14:'QualityValue',15:'Type',16:'TypeValue'}, inplace=True);       
           df.to_csv(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+"_wCN"+".csv", index=False); # save to new csv file
        except:
            print('Not valid');
   