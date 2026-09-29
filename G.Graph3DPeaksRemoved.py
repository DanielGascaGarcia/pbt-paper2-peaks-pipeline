"""
G.Graph3DPeaksRemoved.py
Figure 3b: the CGM readings REMOVED by the peak-based exclusion for the
worked-example participant, as a 3D scatter.

Author: mbaxdg6 (Daniel Gasca Garcia)

What it does
    Reads column ValueCh of the peak-branch working copies (_wCNF), which
    6.MergePeaks.py fills with the original value of every removed reading
    (including readings removed after midnight by 5.MergePeaksNextDay.py)
    and leaves empty for kept readings. Only the removed readings are plotted.

Inputs
    globals.idG, globals.path2, globals.path3, globals.MGDL_TO_MMOL,
    globals.FIGURE_TITLES
    <path2>/PivotBG_wCN.csv
    <path2>/glucose_level<id>-ws-training_wCNF <Weekday>-<YYYY-MM-DD> .csv

Outputs
    <path2>/BGwOnlyMLeftJoinedPeak<id>.csv
    <path3>/Figure3b.png

Notes
    - replace(0, '') is kept from the meal-based version, where kept readings
      were 0; here they are already empty, so it has no effect.
    - "Day number" follows the os.listdir order; z range fixed at 0-400 mg/dL.
"""


import pandas as pd
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
import numpy as np
matplotlib.rcParams.update({'font.size': 18});
import globals
# Parameters
# Worked-example participant, whatever PATIENT_ID says.
id=globals.idG;
path2=globals.path2;
path3=globals.path3;
os.makedirs(path3, exist_ok=True);
fileToRead=str(id)+"-ws-training";
fileToSave="BGwOnlyMLeftJoinedPeak"+str(id)+".csv";

# -----------------------------------------------------------#
# Unit conversion. Source values are in mg/dL.
# Factor lives in globals.py so every script shares one value.
# -----------------------------------------------------------#
MGDL_TO_MMOL = globals.MGDL_TO_MMOL;

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


# This panel shows what the PEAK detector removed, so it reads the _wCNF
# files. The trailing character distinguishes them from the meal branch's
# "_wCN " files, which carry a space instead.
filesToGraph=[];
for file in os.listdir(path2):
    if file.startswith(listVariables[0]+str(fileToRead)+"_wCNF"):
        print(file); 
        filesToGraph.append(file);
print(filesToGraph);


# reading two csv files
data1 = pd.read_csv(str(path2)+'PivotBG_wCN'+'.csv')
# ValueCh = original value of a removed reading, empty for a kept one.
data2 = pd.read_csv(str(path2)+filesToGraph[0],usecols = ['Time','ValueCh']);
# Replace Values in Column
data2['ValueCh'] = data2['ValueCh'].replace(0,'');
data2.rename(columns = {'ValueCh':'BGValue'+str(0)}, inplace = True);
data2.rename(columns = {'Time':'Key'}, inplace = True);
data1['Key']=data1['Key'].str.slice(0, 5);
data1['Key']=data1['Key'].str.strip();
# print(data1);
data2['Key']=data2['Key'].str.slice(0, 5);
data2['Key']=data2['Key'].str.strip();
# print(data2);
# using merge function by setting how='left'
output1 = pd.merge(data1,data2,suffixes=('',''),on='Key',how='left');
for j in range(len(filesToGraph)-1):
        print(filesToGraph[j+1])
        data3 = pd.read_csv(str(path2)+filesToGraph[j+1],usecols = ['Time','ValueCh']);
        data3['ValueCh'] = data3['ValueCh'].replace(0,'');
        data3.rename(columns = {'ValueCh':'BGValue'+str(j+1)}, inplace = True);

        data3.rename(columns = {'Time':'Key'}, inplace = True);
        data3['Key']=data3['Key'].str.slice(0, 5);
        data3['Key']=data3['Key'].str.strip();
        # print(data3);
        output1 = pd.merge(output1,data3,suffixes=('',''),on='Key',how='left');
output1['Key']=output1['Key']+':00';
# Saving the result
output1.to_csv(str(path2)+str(fileToSave));
# -----------------------------------------------------------#
#              Graph 
# -----------------------------------------------------------#
# Re-read the joined table and convert Key "HH:MM:SS" to hours for the x axis.
df =  pd.read_csv(str(path2)+str(fileToSave));
Key=df["Key"].to_numpy();

T_Key=[];
# Converting to number
for i in range(len(Key)):
    (h, m, s) = Key[i].split(':');
    result = (int(h) * 3600 + int(m) * 60 + int(s))/3600;
    T_Key.append(result);
df["Time1"]=T_Key;

#Plot
fig = plt.figure(figsize=(13, 11));
threedee = fig.add_subplot(projection='3d');
if globals.FIGURE_TITLES:
    plt.suptitle("Blood glucose levels removed, ID: "+str(id));
columns=[];
for col in df.columns:
    if "BGValue" in col:
        print(col);
        columns.append(col);

# One scatter per day: x = time of day, y = day index, z = BG (mg/dL).
for i in range(len(columns)):
    threedee.scatter(df["Time1"],i,df["BGValue"+str(i)]);

threedee.set_xlabel('Time (h)',labelpad=18);
threedee.set_ylabel('Day number (#)',labelpad=18);
threedee.set_zlabel('Blood glucose levels \n mg/dL (mmol/L)', labelpad=60);
threedee.tick_params(axis='z', pad=20);

zticks_mgdl = [0, 90, 180, 270, 360];
# z axis in mg/dL with the mmol/L value in brackets on each tick.
threedee.set_zlim(0, 400);
threedee.set_zticks(zticks_mgdl);
threedee.set_zticklabels([f"{v} ({v*MGDL_TO_MMOL:.0f})" for v in zticks_mgdl]);

print("ZLIM:", threedee.get_zlim());
print("TICKS:", threedee.get_zticks());

threedee.set_box_aspect(aspect=None, zoom=1.05);

plt.savefig(path3 + 'Figure3b.png', dpi=300);
plt.close(fig);
