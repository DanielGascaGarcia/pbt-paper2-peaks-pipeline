#Description: Computation of relative changes.
#Created 14th November 2023
#Author: mbaxdg6


import datetime 
import pandas as pd
import os
from datetime import datetime,timedelta
import datetime 
from matplotlib import pyplot as plt
import numpy as np
import csv
pd.options.mode.chained_assignment = None  # default='warn'
import globals

# --- Configurable global variable ---
id = globals.id;
path2 = globals.path2;
fileToRead="BGHourPeak"+str(id);
fileToSave="BGHourRelativeChangePeak"+str(id);
# -----------------------------------------------------------#
#             Substract the staring point
# -----------------------------------------------------------#

dmean = pd.DataFrame();
for i in range(24):
    data = pd.read_csv(str(path2)+str(fileToRead)+str(i)+str("To")+str(i+1)+".csv"); 
    # print(len(data.columns));
    dt = pd.DataFrame();
    dt=data[['Key']];
    for j in range(len(data.columns)-2):
    #    dt1=data['BGValue'+str(j)].diff().to_frame(name='DBGValue'+str(j));
        # serie = data['BGValue'+str(j)].to_frame(name='RChBGValue'+str(j)).div(18.0182).squeeze();
        serie = data['BGValue'+str(j)].to_frame(name='RChBGValue'+str(j)).squeeze();
        try:
            first_val=serie.loc[serie.first_valid_index()];
            dt1=data['BGValue'+str(j)].to_frame(name='RChBGValue'+str(j))-first_val;
            # dt1=data['BGValue'+str(j)].to_frame(name='RChBGValue'+str(j)).div(18.0182)-first_val;
            # print(data['BGValue'+str(j)].to_frame(name='DBGValue'+str(j)).div(18.0182)-first_val);
        except:
            dt1=data['BGValue'+str(j)].to_frame(name='RChBGValue'+str(j));
            # dt1=data['BGValue'+str(j)].to_frame(name='RChBGValue'+str(j)).div(18.0182);
            # print("Variable missing");
        dt['RChBGValue'+str(j)] = dt1['RChBGValue'+str(j)].copy();
    dt.to_csv(str(path2)+str(fileToSave)+str(i)+str("To")+str(i+1)+".csv",index=False);


# -----------------------------------------------------------#
#             Obtaining the last point.
# -----------------------------------------------------------#

for i in range(24):
    data = pd.read_csv(str(path2)+str(fileToSave)+str(i)+str("To")+str(i+1)+".csv"); 
    dt=[];
    for j in range(len(data.columns)-2):
        try:
            serie = data['RChBGValue'+str(j)].to_frame(name='RChBGLValue'+str(j)).squeeze();
            last_val=serie.loc[serie.last_valid_index()];
            print(last_val);
            dt1=last_val;
        except:
            # print("No key");
            dt1=" ";
        dt.append(dt1); 
    dt=pd.DataFrame(dt, columns=['Last_values'])  
    dt.to_csv(str(path2)+str(fileToSave)+str(i)+str("To")+str(i+1)+"lastValues"+".csv",index=False);

    print(dt); 




