#Code: 3.PivotGeneratorBG.py
#Description: Creating pivot table for merge.
#Created 29th March 2023
#Author: mbaxdg6

import datetime 
import pandas as pd



dt = datetime.datetime(2010, 12, 1);
end = datetime.datetime(2010, 12, 1, 23, 59, 59);
step = datetime.timedelta(minutes=1);
path2='C:/OhioDataset/ExploratoryAnalysisData/OhioT1DM/2018/parsedTexts/';
secArray=[];
# -----------------------------------------------------------#
open(str(path2)+"PivotBG"+".csv", 'w').close();
while dt < end:
        secArray.append(dt.strftime('%H:%M:%S'));
        dt += step;
print(len(secArray));
# -----------------------------------------------------------#
for j in secArray:
        file = open(str(path2)+"PivotBG"+".csv", 'a');
        file.write(str(j));
        print(str(j));
        file.write('\n');
        file.close();
# -----------------------------------------------------------#
df = pd.read_csv(str(path2)+"PivotBG"+".csv",  header=None);
df.rename(columns={0: 'Key'}, inplace=True);
df.to_csv(str(path2)+"PivotBG"+"_wCN"+".csv", index=False); # save to new csv 