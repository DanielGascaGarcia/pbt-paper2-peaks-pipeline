#Code: 9.BoxplotPeak.py
#Description: Generating pivot with relative changes on peaks.
#Created 14th november 2023
#Author: mbaxdg6


import datetime 
import pandas as pd
import os
from datetime import datetime,timedelta
import datetime 
from matplotlib import pyplot as plt
import numpy as np
import csv
import seaborn as sns
import matplotlib
matplotlib.rcParams.update({'font.size': 18})
import globals

# -----------------------------------------------------------#
#              Configurable variables 
# -----------------------------------------------------------#
id = globals.id;
path2 = globals.path2;
fileToRead="BGHourRelativeChangePeak"+str(id);
fileToSave="BoxplotPeak"+str(id);

# -----------------------------------------------------------#
#                 Obtain the last values
# -----------------------------------------------------------#
total = pd.DataFrame(index=range(len(pd.read_csv(str(path2)+str(fileToRead)+str(0)+str("To")+str(1)+".csv").columns)-2));
for i in reversed(range(24)):
    data = pd.read_csv(str(path2)+str(fileToRead)+str(i)+str("To")+str(i+1)+"lastValues"+".csv");
    data.rename(columns = {'Last_values':str(i)+str("-")+str(i+1)}, inplace = True);
    total[str(i)+"-"+str(i+1)]=1*data[str(i)+str("-")+str(i+1)];
# -----------------------------------------------------------#
#                   Saving in the correct order
# -----------------------------------------------------------#
total1 = pd.DataFrame(index=range(len(pd.read_csv(str(path2)+str(fileToRead)+str(0)+str("To")+str(1)+".csv").columns)-2));
for i in range(24):
    data = pd.read_csv(str(path2)+str(fileToRead)+str(i)+str("To")+str(i+1)+"lastValues"+".csv");
    data.rename(columns = {'Last_values':"["+str(i)+str("-")+str(i+1)+"]"}, inplace = True);
    print(str(i)+str("-")+str(i+1));
    total1["["+str(i)+"-"+str(i+1)+"]"]=data["["+str(i)+str("-")+str(i+1)+"]"];
total1.to_csv(str(path2)+str(fileToSave)+str(0)+str("-")+str(24)+"total"+".csv",index=False);
# -----------------------------------------------------------#
# Create the plot with figure and axis for better control
# -----------------------------------------------------------#
fig, ax = plt.subplots(figsize=(10, 6))
# -----------------------------------------------------------#
# Plot the boxplot with customization
# -----------------------------------------------------------#
boxplot = pd.DataFrame.boxplot(total, vert=False, patch_artist=True, ax=ax, grid=False,
                               boxprops=dict(facecolor='lightblue', color='black'),
                               whiskerprops=dict(color='black', linewidth=1.5),
                               capprops=dict(color='black', linewidth=1.5),
                               medianprops=dict(color='red', linewidth=2))

ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

ax.set_xlabel("Blood Glucose Relative Change  (mg/dL)", fontsize=14)
ax.set_ylabel("Hours", fontsize=14)
ax.set_title("Blood Glucose Relative Change Behavior, ID: " + str(id), fontsize=16)


highlight_start, highlight_end = -2 * 18.0182, 2 * 18.0182
ax.axvspan(highlight_start, highlight_end, color="blue", alpha=0.2, label='No Significant Change')


def mg_dL_to_mmol(x):
    return x * 0.0555

secax = ax.secondary_xaxis('top', functions=(mg_dL_to_mmol, lambda x: x / 0.0555))
secax.set_xlabel("Blood Glucose Relative Change  (mmol/L)", fontsize=14)
secax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}'))

ax.tick_params(axis='both', which='major', labelsize=12)
secax.tick_params(axis='x', labelsize=12)
ax.legend(loc='upper right', frameon=False)


plt.tight_layout()
plt.show()

