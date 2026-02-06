#Description: Computation of relative changes.
#Created 19th April 2023
#Author: mbaxdg6

import warnings
import datetime 
import pandas as pd
import os
from datetime import datetime,timedelta
import datetime 
from matplotlib import pyplot as plt
import numpy as np
import csv
import seaborn as sns
warnings.simplefilter(action='ignore', category=FutureWarning)
import globals

# --- Configurable global variable ---
id = globals.id;
path2 = globals.path2;
fileToRead="BoxplotPeak"+str(id);
fileToSave="BGHourRelativeChangePeak"+str(id);
# -----------------------------------------------------------#
dt = datetime.datetime(2010, 12, 1);
end = datetime.datetime(2010, 12, 1, 23, 59, 59);
step = datetime.timedelta(minutes=1);
secArray=[];
medians_a=[];
Flag_a=[];
# -----------------------------------------------------------#
# Open file and obtain medians
# -----------------------------------------------------------#
total=pd.read_csv(str(path2)+str(fileToRead)+str(0)+str("-")+str(24)+"total"+".csv");
_, bp = pd.DataFrame.boxplot(total, return_type='both');
medians = [median.get_ydata() for median in bp["medians"]];
# -----------------------------------------------------------#
# Obtain statistics of the number of lectures per hour
# -----------------------------------------------------------#
values=pd.DataFrame();       
values=total.count(axis='rows');
low_b=np.percentile(values, 50);
upper_b=np.percentile(values, 70);
Flag=[]

for i in range(len(values)):
 if values[i]<low_b:
    Flag.append(1);
 elif values[i]>=upper_b:
    Flag.append(3);
 else:
    Flag.append(2);
print(Flag);

# -----------------------------------------------------------#
# Obtain the pivot and variables needed to graph
# -----------------------------------------------------------#
open(str(path2)+str(fileToSave)+str("0To24")+"medians"+".csv", 'w').close();
i=0;
j=1;
while dt < end:
        secArray.append(dt.strftime('%H:%M:%S'));
        medians_a.append(medians[i][0]);
        Flag_a.append(Flag[i]);
        # print(i);
        dt += step;
        if j%60==0:
              i=i+1;
        j=j+1;
# -----------------------------------------------------------#
for j in range(len(secArray)):
        file = open(str(path2)+str(fileToSave)+str("0To24")+"medians"+".csv", 'a');
        file.write(str(secArray[j])+","+str(medians_a[j])+","+str(Flag_a[j]));
        file.write('\n');
        file.close();
# -----------------------------------------------------------#
df = pd.read_csv(str(path2)+str(fileToSave)+str("0To24")+"medians"+".csv",  header=None);
df.rename(columns={0: 'Key',1:'MedRelChange',2:'Flag'}, inplace=True);
df.to_csv(str(path2)+str(fileToSave)+str("0To24")+"medians"+"_wCN"+".csv", index=False); # save to new csv 
