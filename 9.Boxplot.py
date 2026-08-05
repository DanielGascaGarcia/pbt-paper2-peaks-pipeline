#Description: Generating pivot with relative changes.
#Created 10th May 2023
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
total = pd.DataFrame(index=range(len(pd.read_csv(str(path2)+str(fileToRead)+str(0)+str("To")+str(1)+".csv").columns)-1));
for i in reversed(range(24)):
    data = pd.read_csv(str(path2)+str(fileToRead)+str(i)+str("To")+str(i+1)+"lastValues"+".csv");
    data.rename(columns = {'Last_values':str(i)+str("-")+str(i+1)}, inplace = True);
    total[str(i)+"-"+str(i+1)]=1*data[str(i)+str("-")+str(i+1)];
# -----------------------------------------------------------#
# Saving in the correct order
# -----------------------------------------------------------#
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
