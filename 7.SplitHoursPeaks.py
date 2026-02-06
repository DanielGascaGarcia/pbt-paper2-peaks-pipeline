#Code: 7.SplitHoursPeaks.py
#Description: Split values in different files.
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

import globals

# -----------------------------------------------------------#
#              Configurable variables 
# -----------------------------------------------------------#
id = globals.id;
path2 = globals.path2;

fileToRead="BGwNMLeftJoinedPeak"+str(id)+".csv";
fileToSave="BGHourPeak"+str(id);


# Loop over all day round
for i in range(24):
    with open(str(path2)+str(fileToRead)) as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
                data = pd.read_csv(str(path2)+str(fileToRead)); 
                data_top = data.columns;
                print(data_top); 
                dt1 = datetime.datetime(2010, 12, 1,i,0,0);
                dt2 = datetime.datetime(2010, 12, 1,i,59,59);
                with open(str(path2)+str(fileToSave)+str(i)+str("To")+str(i+1)+".csv", 'w', newline='') as fout:
                            csv_output = csv.writer(fout);
                            csv_output.writerow(data_top);  #header
                            for row in reader:
                                split=datetime.datetime(2010, 12, 1,int(row[1][0:2]),int(row[1][3:5]),int(row[1][6:8])); 
                                if dt1.strftime('%H:%M:%S')<=split.strftime('%H:%M:%S')<=dt2.strftime('%H:%M:%S'):
                                    # print (row[1]);
                                    csv_output.writerow(row);

