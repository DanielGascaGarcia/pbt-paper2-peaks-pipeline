#Code: G.Graph3DCleanBGPeak.py
#Description: Graph the Blood Glucose readings that remain after the peak
#             detector has removed meal-related excursions (Figure 3, panel c).
#Created 3rd August 2023
#Author: mbaxdg6

import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
import numpy as np
matplotlib.rcParams.update({'font.size': 18});
import globals
import os
# Parameters
id=globals.idG;
path2=globals.path2;
path3=globals.path3;
os.makedirs(path3, exist_ok=True);
fileToGraph="BGwNMLeftJoinedPeak"+str(id)+".csv";

# -----------------------------------------------------------#
# Unit conversion. Source values are in mg/dL.
# Factor lives in globals.py so every script shares one value.
#
# NOTE: the values are plotted in mg/dL, as in panels a and b. An earlier
# version divided them by 18 before plotting, which put this panel on a
# different scale from the other two and made the three not comparable.
# -----------------------------------------------------------#
MGDL_TO_MMOL = globals.MGDL_TO_MMOL;

df =  pd.read_csv(str(path2)+str(fileToGraph));
Key=df["Key"].to_numpy();

T_Key=[];
# Converting to number
for i in range(len(Key)):
    (h, m, s) = Key[i].split(':');
    result = (int(h) * 3600 + int(m) * 60 + int(s))/3600;
    T_Key.append(result);
df["Time1"]=T_Key;
# -----------------------------------------------------------#
#                            Graph 
# -----------------------------------------------------------#

fig = plt.figure(figsize=(13, 11));
threedee = fig.add_subplot(projection='3d');
if globals.FIGURE_TITLES:
    plt.suptitle("Blood glucose levels after removing peaks, ID: "+str(id));
columns=[];
for col in df.columns:
    if "BGValue" in col:
        print(col);
        columns.append(col);

for i in range(len(columns)):
    threedee.scatter(df["Time1"],i,df["BGValue"+str(i)]);

threedee.set_xlabel('Time (h)', labelpad=18);
threedee.set_ylabel('Day number (#)', labelpad=18);
threedee.set_zlabel('Blood glucose levels \n mg/dL (mmol/L)', labelpad=60);
threedee.tick_params(axis='z', pad=20);

zticks_mgdl = [0, 90, 180, 270, 360];
threedee.set_zlim(0, 400);
threedee.set_zticks(zticks_mgdl);
threedee.set_zticklabels([f"{v} ({v*MGDL_TO_MMOL:.0f})" for v in zticks_mgdl]);

print("ZLIM:", threedee.get_zlim());
print("TICKS:", threedee.get_zticks());

threedee.set_box_aspect(aspect=None, zoom=1.05);
plt.savefig(path3 + 'Figure3c.png', dpi=300);
plt.close(fig);
