#Description: Merge of peak.
#Created 14th November 2023
#Author: mbaxdg6


import datetime 
import pandas as pd
import os
from datetime import datetime,timedelta
import datetime 
from matplotlib import pyplot as plt
import numpy as np
import globals

# --- Configurable global variable ---

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

for file in os.listdir(path2):
    if file.startswith(listVariables[0]+str(fileToRead)+str('_wCNF ')):
        print(file); 
        filesBG.append(file);

# print(filesBG);

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

    
           


if len(filesBG)>=2:
    # reading two csv files
    data1 = pd.read_csv(str(path2)+'PivotBG_wCN'+'.csv')
    data2 = pd.read_csv(str(path2)+filesBG[0],usecols = ['Time','BGValue']);
    data2.rename(columns = {'BGValue':'BGValue'+str(0)}, inplace = True);
    data2.rename(columns = {'Time':'Key'}, inplace = True);
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
output1['Key']=output1['Key']+':00';
# Saving the result
output1.to_csv(str(path2)+str(fileToSave));
