#Code: 4.MealBolusDetection.py
#Description: Read files of BG, meal and Bolus.
#Created 29th March 2023
#Author: mbaxdg6


import datetime 
import pandas as pd
import os
from datetime import datetime,timedelta
import datetime 
from matplotlib import pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter, freqz
import operator
import globals

# --- Configurable global variable ---
id = globals.id;
filesBG=[];
filesBolus=[];
filesMeals=[];
path2=globals.path2;
fileToRead=str(id)+"-ws-training";
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


# -----------------------------------------------------------#
#                   Files of Blood Glucose
# -----------------------------------------------------------#
for file in os.listdir(path2):
    if file.startswith(listVariables[0]+str(fileToRead)+str(' ')):
        # print(file); 
        filesBG.append(file);
h, w = len(filesBG), 5;
Matrix = [[0 for x in range(w)] for y in range(h)] ;
# -----------------------------------------------------------#
#                    Sort of files
# -----------------------------------------------------------#
for i in range(len(filesBG)):
    Matrix[i][0]=filesBG[i];
    Matrix[i][1]=filesBG[i][len(Matrix[i][0]):len(Matrix[i][0])-16:-1]; 
    Matrix[i][1]=Matrix[i][1][::-1].strip();
    # print(Matrix[i][1]);
    Matrix[i][2]=(Matrix[i][1][0:4]);#Year
    # print(Matrix[i][2]);
    Matrix[i][3]=(Matrix[i][1][5:7]);#Month
    # print(Matrix[i][2]);
    Matrix[i][4]=(Matrix[i][1][8:10]);#Day
    # print(Matrix[i][3]);
Matrix = sorted(Matrix, key = operator.itemgetter(2,3,4));
# -----------------------------------------------------------#
#                  Files of Boluses
# -----------------------------------------------------------#
for file in os.listdir(path2):
    if file.startswith(listVariables[4]+str(fileToRead)+str(' ')):
        # print(file); 
        filesBolus.append(file);
# print(filesBolus);
# -----------------------------------------------------------#
#                  Files of Meals
# -----------------------------------------------------------#
for file in os.listdir(path2):
    if file.startswith(listVariables[5]+str(fileToRead)+str(' ')):
        # print(file); 
        filesMeals.append(file);
# print(filesMeals);


# -----------------------------------------------------------#
#                  Main program
# -----------------------------------------------------------#
try:
# -----------------------------------------------------------#
#                    Create files to input
# -----------------------------------------------------------#
    for i in range(len(filesBG)):
            print(Matrix[i][0])
            dataBG = pd.read_csv(str(path2)+Matrix[i][0]);
            BG_1=len(dataBG["Time"]); #Find important numbers
            open(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:], 'w').close();
            BGT_=dataBG[["Time","BGValue"]];
            for l in range(BG_1):
                    BGdt=datetime.datetime(2010, 12, 1,int(BGT_["Time"][l][0:3]),int(BGT_["Time"][l][4:6]),int(BGT_["Time"][l][7:9]));
                    file = open(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:], 'a');
                    file.write(str(BGdt.strftime('%H:%M:%S')+str(",")+str(dataBG["BGValue"][l])+str(",")+str(0)+str(",")+str(0)+str(",")+str(dataBG["BGValue"][l])));
                    file.write('\n');
                    file.close();
            df = pd.read_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:],  header=None);
            df.rename(columns={0: 'Time', 1: 'BGValue', 2: 'Flag', 3: 'ValueCh',4: 'BGValue2'}, inplace=True);
            df.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:], index=False); # save to new csv 
# -----------------------------------------------------------#
#                   Find files to use
# -----------------------------------------------------------#
    for i in range(len(filesBG)):

        print(Matrix[i][0]);   

        for j in range(len(filesMeals)):
            #Meals
            if listVariables[5]+str(fileToRead)+str(' ')+Matrix[i][0][29:]  in filesMeals[j]:
                # print("exist: "+listVariables[5]+str(fileToRead)+str(' ')+filesBG[i][29:]);
                dataBG = pd.read_csv(str(path2)+Matrix[i][0]);
                dataMeal = pd.read_csv(str(path2)+listVariables[5]+str(fileToRead)+str(' ')+Matrix[i][0][29:]);

                print(listVariables[5]+str(fileToRead)+str(' ')+Matrix[i][0][29:]);
               
                M=len(dataMeal["Time"]); #Find important numbers
                MTT=dataMeal["Time"];
                MC=dataMeal["CarbsValue"];
                MK=dataMeal["TypeFood"];
                # print(type(dataBG["Time"]));

# -----------------------------------------------------------#
#       Find maximum values and define Glycemic index
# -----------------------------------------------------------#
                for k in range(M):
                    # print(M);
                    # MK[k] in {' Breakfast ',' Lunch ',' Dinner '}
                    if 1==1: #Check for the kind of food

                                print(MK[k]);

                                dt = datetime.datetime(2010, 12, 1,int(MTT[k][0:3]),int(MTT[k][4:6]),int(MTT[k][7:9]));
                                dt1= datetime.datetime(2010, 12, 1,int(MTT[k][0:3]),int(MTT[k][4:6]),int(MTT[k][7:9]))+datetime.timedelta(hours=3);# hours=timne needed to find the maximum
                                BG_=len(dataBG["Time"]); #Find important numbers
                                if  dt1>datetime.datetime(2010, 12, 1,23,59,59):
                                        # print("dt1 modified");
                                        # print(dt1);
                                        dt1=datetime.datetime(2010, 12, 1,23,59,59);
                                        # print(dt1);
                                BGT=dataBG[["Time","BGValue"]];
                                BGV=[];
                                time=[];
                                for l in range(BG_):
                                    BGdt=datetime.datetime(2010, 12, 1,int(BGT["Time"][l][0:3]),int(BGT["Time"][l][4:6]),int(BGT["Time"][l][7:9]));
                                    if dt.strftime('%H:%M:%S') <= BGdt.strftime('%H:%M:%S')<= dt1.strftime('%H:%M:%S'): 
                                        # print(dt.strftime('%H:%M:%S'),BGT["BGValue"][l],BGdt.strftime('%H:%M:%S'),dt1.strftime('%H:%M:%S'));
                                        time.append(BGdt.strftime('%H:%M:%S'));
                                        BGV.append(BGT["BGValue"][l]);
                                #Low pass filter        
                                # Filter requirements.
                                order = 6;
                                fs = 25.0;       # sample rate, Hz
                                cutoff = 5;      # desired cutoff frequency of the filter, Hz
                                nyq = 0.5 * fs;
                                normal_cutoff = cutoff / nyq;
                                b, a = butter(order, normal_cutoff, btype='low', analog=False);
                                BGVF = lfilter(b, a, BGV);
                                GlD=pd.DataFrame({'Time': time, 'BGValue':BGV,'BGValueF':BGVF}); 
                                if len(GlD)>0: #Missing Blood Glucose values 
                                    t2 = datetime.datetime(2010, 12, 1,int(GlD["Time"][GlD["BGValueF"].argmax()][0:2]),int(GlD["Time"][GlD["BGValueF"].argmax()][3:5]),int(GlD["Time"][GlD["BGValueF"].argmax()][6:8]));
                                    t1 = datetime.datetime(2010, 12, 1,int(GlD["Time"][0][0:2]),int(GlD["Time"][0][3:5]),int(GlD["Time"][0][6:8]));
                                    TypeFood=(t2-t1).total_seconds()/3600;
                                    print((t2-t1).total_seconds()/3600);#Value needed to check the glycemic index
# -----------------------------------------------------------#
#                 High Glycemic Food
# -----------------------------------------------------------#  
                                    if  0<=TypeFood<1.5:
                                        print("High Glycemic Food");
                                        dtH1 = datetime.datetime(2010, 12, 1,int(MTT[k][0:3]),int(MTT[k][4:6]),int(MTT[k][7:9]));
                                        dtH2= datetime.datetime(2010, 12, 1,int(MTT[k][0:3]),int(MTT[k][4:6]),int(MTT[k][7:9]))+datetime.timedelta(hours=4);# hours=timne needed to find the maximum 
# -----------------------------------------------------------#
#                 Next day condition
# -----------------------------------------------------------#                                    
                                        if  dtH2>datetime.datetime(2010, 12, 1,23,59,59):
                                            dtH3=datetime.datetime(2010, 12, 1,00,00,00);
                                            dtH4=dtH2;
                                            print("dtH2 modified");
                                            # print(dtH3.strftime('%H:%M:%S'));

                                            dataBG1 = pd.read_csv(str(path2)+Matrix[i+1][0]);
                                            BG_=len(dataBG1["Time"]);
                                            BGT_=dataBG1[["Time","BGValue"]];
                                            for l in range(BG_):
                                                    BGdt=datetime.datetime(2010, 12, 1,int(BGT_["Time"][l][0:3]),int(BGT_["Time"][l][4:6]),int(BGT_["Time"][l][7:9]));
                                                    if dtH3.strftime('%H:%M:%S')<=BGdt.strftime('%H:%M:%S')<=dtH4.strftime('%H:%M:%S'): 
                                                        # reading the csv file
                                                        df = pd.read_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i+1][0][29:]);
                                                        
                                                        # updating the column value/data
                                                        df.loc[l, 'Flag'] = 100;
                                                        df.loc[l, 'ValueCh']=df.loc[l, 'BGValue2'];   
                                                        df.loc[l, 'BGValue'] = np.nan;
                                                        
                                                        # writing into the file
                                                        df.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i+1][0][29:], index=False);
                                            dtH2=datetime.datetime(2010, 12, 1,23,59,59);
                                        BG_2=len(dataBG["Time"]); #Find important numbers
# -----------------------------------------------------------#
#                 Chop off
# -----------------------------------------------------------#  
                                        for l in range(BG_2):
                                                BGdt=datetime.datetime(2010, 12, 1,int(BGT["Time"][l][0:3]),int(BGT["Time"][l][4:6]),int(BGT["Time"][l][7:9]));
                                                if dtH1.strftime('%H:%M:%S')<=BGdt.strftime('%H:%M:%S')<=dtH2.strftime('%H:%M:%S'): 
                                                    # reading the csv file
                                                    df = pd.read_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:]);
                                                    
                                                    # updating the column value/data
                                                    df.loc[l, 'Flag'] = 100;
                                                    df.loc[l, 'ValueCh']=df.loc[l, 'BGValue2'];   
                                                    df.loc[l, 'BGValue'] = np.nan;

                                                    # writing into the file
                                                    df.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:], index=False);
# -----------------------------------------------------------#
#                 Medium Glycemic Food
# -----------------------------------------------------------#                                                
                                    elif 1.5<=TypeFood<2.5:
                                        print("Medium Glycemic Food");
                                        dtH1 = datetime.datetime(2010, 12, 1,int(MTT[k][0:3]),int(MTT[k][4:6]),int(MTT[k][7:9]));
                                        dtH2= datetime.datetime(2010, 12, 1,int(MTT[k][0:3]),int(MTT[k][4:6]),int(MTT[k][7:9]))+datetime.timedelta(hours=4);# hours=timne needed to find the maximum 
# -----------------------------------------------------------#
#                 Next day condition
# -----------------------------------------------------------#                                    
                                        if  dtH2>datetime.datetime(2010, 12, 1,23,59,59):
                                            dtH3=datetime.datetime(2010, 12, 1,00,00,00);
                                            dtH4=dtH2;
                                            print("dtH2 modified");
                                            # print(dtH3.strftime('%H:%M:%S'));

                                            dataBG1 = pd.read_csv(str(path2)+Matrix[i+1][0]);
                                            BG_=len(dataBG1["Time"]);
                                            BGT_=dataBG1[["Time","BGValue"]];
                                            for l in range(BG_):
                                                    BGdt=datetime.datetime(2010, 12, 1,int(BGT_["Time"][l][0:3]),int(BGT_["Time"][l][4:6]),int(BGT_["Time"][l][7:9]));
                                                    if dtH3.strftime('%H:%M:%S')<=BGdt.strftime('%H:%M:%S')<=dtH4.strftime('%H:%M:%S'): 
                                                        # reading the csv file
                                                        df = pd.read_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i+1][0][29:]);
                                                        
                                                        # updating the column value/data
                                                        df.loc[l, 'Flag'] = 100;
                                                        df.loc[l, 'ValueCh']=df.loc[l, 'BGValue2'];   
                                                        df.loc[l, 'BGValue'] = np.nan;
                                                        
                                                        # writing into the file
                                                        df.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i+1][0][29:], index=False);
                                            dtH2=datetime.datetime(2010, 12, 1,23,59,59);
                                        BG_2=len(dataBG["Time"]); #Find important numbers
# -----------------------------------------------------------#
#                 Chop off
# -----------------------------------------------------------#                                    
                                        for l in range(BG_2):
                                                BGdt=datetime.datetime(2010, 12, 1,int(BGT["Time"][l][0:3]),int(BGT["Time"][l][4:6]),int(BGT["Time"][l][7:9]));
                                                if dtH1.strftime('%H:%M:%S')<=BGdt.strftime('%H:%M:%S')<=dtH2.strftime('%H:%M:%S'): 
                                                    # reading the csv file
                                                    df = pd.read_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:]);
                                                    
                                                    # updating the column value/data
                                                    df.loc[l, 'Flag'] = 100;
                                                    df.loc[l, 'ValueCh']=df.loc[l, 'BGValue2'];   
                                                    df.loc[l, 'BGValue'] = np.nan;
                                                    
                                                    # writing into the file
                                                    df.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:], index=False);
# -----------------------------------------------------------#
#                 Low Glycemic Glycemic Food
# -----------------------------------------------------------# 
                                    elif 2.5<=TypeFood:
                                        print("Low Glycemic Food");
                                        dtH1 = datetime.datetime(2010, 12, 1,int(MTT[k][0:3]),int(MTT[k][4:6]),int(MTT[k][7:9]));
                                        dtH2= datetime.datetime(2010, 12, 1,int(MTT[k][0:3]),int(MTT[k][4:6]),int(MTT[k][7:9]))+datetime.timedelta(hours=4);# hours=timne needed to find the maximum 
# -----------------------------------------------------------#
#                 Next day condition
# -----------------------------------------------------------#                                    
                                        if  dtH2>datetime.datetime(2010, 12, 1,23,59,59):
                                            dtH3=datetime.datetime(2010, 12, 1,00,00,00);
                                            dtH4=dtH2;
                                            print("dtH2 modified");
                                            # print(dtH3.strftime('%H:%M:%S'));

                                            dataBG1 = pd.read_csv(str(path2)+Matrix[i+1][0]);
                                            BG_=len(dataBG1["Time"]);
                                            BGT_=dataBG1[["Time","BGValue"]];
                                            for l in range(BG_):
                                                    BGdt=datetime.datetime(2010, 12, 1,int(BGT_["Time"][l][0:3]),int(BGT_["Time"][l][4:6]),int(BGT_["Time"][l][7:9]));
                                                    if dtH3.strftime('%H:%M:%S')<=BGdt.strftime('%H:%M:%S')<=dtH4.strftime('%H:%M:%S'): 
                                                        # reading the csv file
                                                        df = pd.read_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i+1][0][29:]);
                                                        
                                                        # updating the column value/data
                                                        df.loc[l, 'Flag'] = 100;
                                                        df.loc[l, 'ValueCh']=df.loc[l, 'BGValue2'];   
                                                        df.loc[l, 'BGValue'] = np.nan;
                                                        
                                                        # writing into the file
                                                        df.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i+1][0][29:], index=False);
                                            dtH2=datetime.datetime(2010, 12, 1,23,59,59);
                                        BG_2=len(dataBG["Time"]); #Find important numbers
# -----------------------------------------------------------#
#                 Chop off
# -----------------------------------------------------------# 
                                        BG_2=len(dataBG["Time"]); #Find important numbers
                                        for l in range(BG_2):
                                                BGdt=datetime.datetime(2010, 12, 1,int(BGT["Time"][l][0:3]),int(BGT["Time"][l][4:6]),int(BGT["Time"][l][7:9]));
                                                if dtH1.strftime('%H:%M:%S')<=BGdt.strftime('%H:%M:%S')<=dtH2.strftime('%H:%M:%S'): 
                                                    # reading the csv file
                                                    df = pd.read_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:]);
                                                    
                                                    # updating the column value/data
                                                    df.loc[l, 'Flag'] = 100;
                                                    df.loc[l, 'ValueCh']=df.loc[l, 'BGValue2'];   
                                                    df.loc[l, 'BGValue'] = np.nan;   

                                                    # writing into the file
                                                    df.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:], index=False);

                                    else:
                                        print("Meal not found");
                                    # GlD.plot('Time',  'BGValue', kind='scatter');
                                    # GlD.plot('Time',  'BGValueF', kind='scatter');
                                    # plt.show();
                                df = pd.read_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_wCN ')+Matrix[i][0][29:]);
                                del df['BGValue2']
                                df.to_csv(str(path2)+listVariables[0]+str(fileToRead)+str('_ToGraph')+Matrix[i][0][29:], index=False);
                    else:
                        print("This event is one"+MK[k]);   
        for j in range(len(filesBolus)):
            #Bolus
            if listVariables[4]+str(fileToRead)+str(' ')+Matrix[i][0][29:]  in filesBolus[j]:
                print("");
                #  print("exist: "+listVariables[4]+str(fileToRead)+str(' ')+filesBG[i][29:]);
except:
    print("file not found");

