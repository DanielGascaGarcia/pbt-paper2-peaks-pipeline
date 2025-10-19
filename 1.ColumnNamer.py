#Code: 1.ColumnNamer.py
#Description: Adding column names to parsed files.
#Created 1st November 2022
#Author: mbaxdg6

# Importing libreries

import xml.etree.ElementTree as ET
import datetime
import calendar
import os
import csv
import pandas as pd
import globals

# --- Configurable global variable ---
id = globals.id;
fileToRead=str(id)+"-ws-training";
path1=globals.path1;
path2=globals.path2;

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
   