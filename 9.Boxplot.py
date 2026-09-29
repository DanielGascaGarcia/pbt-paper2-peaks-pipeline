"""
9.Boxplot.py
Step 9 (meal-based branch of paper 2): collect the hourly relative changes of
all days into one table.

Created: 10 May 2023
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    Reads the 24 lastValues files from 8.RelativeChange.py and puts them side
    by side (one column per hour, one row per day) in
    Boxplot<id>0-24total.csv, which the comparison stage of paper 2 reads.
    The box plot is still drawn but, unlike paper 1, it is not saved: the
    figure in the article comes from the peak-based branch.

Inputs
    globals.id, globals.path2, globals.path3, globals.MGDL_TO_MMOL,
    globals.FIGURE_TITLES
    <path2>/BGHourRelativeChange<id>0To1.csv          (only to count the days)
    <path2>/BGHourRelativeChange<id><i>To<i+1>lastValues.csv   for i = 0 ... 23

Outputs
    <path2>/Boxplot<id>0-24total.csv
        Columns [0-1], [1-2], ..., [23-24]; one row per day; mg/dL.

Notes
    - Number of rows = number of day columns: the 0To1 file has Key + one
      column per day, so "-1" is the correct offset.
    - The meal-based lastValues files write empty days as "" (read back as
      NaN, row kept), so row j is day j here.
"""


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
# --- Configurable global variables (set in globals.py) ---
id=globals.id;
path2=globals.path2;
path3=globals.path3;
os.makedirs(path3, exist_ok=True);
fileToRead="BGHourRelativeChange"+str(id);
fileToSave="Boxplot"+str(id);

# -----------------------------------------------------------#
# Unit conversion. Source values are in mg/dL.
# Factor lives in globals.py so every script shares one value.
# -----------------------------------------------------------#
MGDL_TO_MMOL = globals.MGDL_TO_MMOL;

# -----------------------------------------------------------#
# Figure titles. Journals put the title in the caption, not in
# the image, so this is off for the submitted figures.
# -----------------------------------------------------------#
def figTitle(text):
    if globals.FIGURE_TITLES:
        plt.title(text);

# -----------------------------------------------------------#
# Obtain the last values
# -----------------------------------------------------------#
# One row per day: Key + one column per day in this file -> "-1".
# Table for the (unsaved) plot, hours in reverse order.
total = pd.DataFrame(index=range(len(pd.read_csv(str(path2)+str(fileToRead)+str(0)+str("To")+str(1)+".csv").columns)-1));
for i in reversed(range(24)):
    data = pd.read_csv(str(path2)+str(fileToRead)+str(i)+str("To")+str(i+1)+"lastValues"+".csv");
    data.rename(columns = {'Last_values':str(i)+str("-")+str(i+1)}, inplace = True);
    total[str(i)+"-"+str(i+1)]=1*data[str(i)+str("-")+str(i+1)];
# -----------------------------------------------------------#
# Saving in the correct order
# -----------------------------------------------------------#
# Same table in normal hour order, with labels [i-i+1]; this one is saved.
total1 = pd.DataFrame(index=range(len(pd.read_csv(str(path2)+str(fileToRead)+str(0)+str("To")+str(1)+".csv").columns)-1));
for i in range(24):
    data = pd.read_csv(str(path2)+str(fileToRead)+str(i)+str("To")+str(i+1)+"lastValues"+".csv");
    data.rename(columns = {'Last_values':"["+str(i)+str("-")+str(i+1)+"]"}, inplace = True);
    print(str(i)+str("-")+str(i+1));
    total1["["+str(i)+"-"+str(i+1)+"]"]=data["["+str(i)+str("-")+str(i+1)+"]"];

total1.to_csv(str(path2)+str(fileToSave)+str(0)+str("-")+str(24)+"total"+".csv",index=False);


# -----------------------------------------------------------#
# Plot the dataframe
# -----------------------------------------------------------#
plt.figure(figsize=(12, 9));
plt.grid();
pd.DataFrame.boxplot(total, vert = False);
# -----------------------------------------------------------#
# Display the plot
# -----------------------------------------------------------#
figTitle("Blood Glucose Relative Change Behaviour, ID: "+str(id));
plt.xlabel("Blood glucose relative change (mg/dL)");
plt.ylabel("Hours");
plt.axvspan(-2/MGDL_TO_MMOL, 2/MGDL_TO_MMOL, color="blue", alpha=0.2)

# -----------------------------------------------------------#
# Secondary axis in mmol/L. The boxplot is horizontal, so the
# value axis is X: use twiny(). Rescale only, data drawn once.
# -----------------------------------------------------------#
ax = plt.gca();
ax2 = ax.twiny();
ax2.set_xlim([v * MGDL_TO_MMOL for v in ax.get_xlim()]);
ax2.set_xlabel("Blood glucose relative change (mmol/L)");
ax2.grid(False);

# -----------------------------------------------------------#
# No figure is written from this branch. The meal-based box plot
# exists to produce Boxplot<id>0-24total.csv, which the comparison
# stage reads; the figure that goes into the article comes from the
# peak branch. Set FIGURE_TITLES and re-enable the block below only
# if the panel is needed for local review.
# -----------------------------------------------------------#
# if id == globals.idG:
#     out = path3 + 'Figure4.png';
#     plt.savefig(out, dpi=300, bbox_inches='tight');
#     print("Saved:", os.path.abspath(out));

plt.close();
