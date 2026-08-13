#Code: 2.Disagregator.py
#Description: Saving data in different files according to weekdays.
#Created 2nd November 2022
#Author: mbaxdg6

# Importing libreries

from itertools import groupby
import xml.etree.ElementTree as ET
import csv
import globals

# --- Configurable global variable ---
id = globals.id;
fileToRead=str(id)+"-ws-training";
path1=globals.path1;
path2=globals.path2;

ohioTree = ET.parse(str(path1)+str(fileToRead)+'.xml');
ohioRoot = ohioTree.getroot();

elemList = [];

for child in ohioRoot:
    print(child.tag, child.attrib);
    elemList.append(child.tag);

#Duplicities are removed
elemList = list(set(elemList));

# Printing the results
print(len(elemList));

for i in range(len(elemList)):
    print (i);
    # Blood Glucose
    if  i==0:
        try: 
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable', 'Group','Key','Weekday','Time','TimeVariable','TimeStamp','Value','BGValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid');
    # Finger stick 
    if  i==1:
        try: 
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable',	'Group',	'Key',	'Weekday',	'Time',	'TimeVariable',	'TimeStamp',	'Value',	'FingerValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid');


    # Basal 
    if  i==2:
        try:
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable'	,'Group',	'Key'	,'Weekday'	,'Time'	,'TimeVariable',	'TimeStamp',	'Value'	,'BasalValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid');

    # Temp_basal 
    if  i==3:
        try:
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable',	'Group',	'Key1',	'Weekday1',	'Time1',	'TimeVariable1',	'TimeStamp1',	'key2',	'Weekday2',	'Time2',	'TimeVariable2',	'TimeStamp2',	'Type',	'Value',	'TempBasalValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid');       
    # Bolus 
    if  i==4:
        try:
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable',	'Group'	,'Key1',	'Weekday1',	'Time1'	,'TimeVariable1'	,'TimeStamp1'	,'Group2',	'key2'	,'Weekday2'	,'Time2'	,'TimeVariable2'	,'TimeStamp1',	'Type',	'Dose'	,'DoseType'	,'BolusValue'	,'CarbInput'	,'CarbInputValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid');       
    # Meal 
    if  i==5:
        try:
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable',	'Group'	,'Key',	'Weekday',	'Time',	'TimeVariable',	'TimeStamp',	'Type',	'TypeFood',	'Carbs',	'CarbsValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid');       
    # Sleep 
    if  i==6:
        try:
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable',	'Group',	'Key1',	'Weekday1',	'Time1',	'TimeVariable1',	'TimeStamp1',	'Group2',	'key2',	'Weekday2',	'Time2',	'TimeVariable2',	'TimeStamp2',	'Quality',	'QualityValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid');       
    # Work 
    if  i==7:
        try:
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable',	'Group',	'Key1',	'Weekday1',	'Time1',	'TimeVariable1',	'TimeStamp1',	'Group2',	'key2',	'Weekday2',	'Time2',	'TimeVariable2',	'TimeStamp2',	'Intensity',	'IntensityValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid');       

    # Stressors 
    if  i==8:
        try:
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable',	'Group',	'Key1',	'Weekday1',	'Time1',	'TimeVariable1',	'TimeStamp1',	'Type',	'typeValue',	'Description',	'DescriptionValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid');   
    # Hypo_event 
    if  i==9:
        try:
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable',	'Group',	'Key',	'Weekday',	'Time',	'TimeVariable',	'TimeStamp']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid');   
    # Illness 
    if  i==10:
        try:
           with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable',	'Group',	'Key1',	'Weekday1',	'Time1'	,'TimeVariable1',	'TimeStamp1',	'Type',	'typeValue',	'Description',	'DescriptionValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid');  
    #  Exercise
    if  i==11:
        try:
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable',	'Group',	'Key1',	'Weekday1',	'Time1',	'TimeVariable1',	'TimeStamp1',	'Intensity',	'IntensityValue',	'Type',	'TypeValue',	'Duration',	'DurationValue',	'Competitive',	'CompetitiveValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid'); 

    # Basis_heart_rate 
    if  i==12:
        try:
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable',	'Group'	,'Key'	,'Weekday',	'Time',	'TimeVariable',	'TimeStamp'	,'Value',	'BHValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid'); 
    # Basis_gsr
    if  i==13:
        try:
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable',	'Group'	,'Key'	,'Weekday',	'Time',	'TimeVariable',	'TimeStamp'	,'Value',	'GSRValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid'); 
    # Basis_skin_temperature 
    if  i==14:
        try:
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable',	'Group'	,'Key'	,'Weekday',	'Time',	'TimeVariable',	'TimeStamp'	,'Value',	'BSTValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid'); 
    # basis_air_temperature 
    if  i==15:
        try:
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable',	'Group'	,'Key'	,'Weekday',	'Time',	'TimeVariable',	'TimeStamp'	,'Value',	'BSkinValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid'); 
    # Basis_steps 
    if  i==16:
        try:
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable',	'Group'	,'Key'	,'Weekday',	'Time',	'TimeVariable',	'TimeStamp'	,'Value',	'BStepsValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid'); 

    # Basis_sleep 
    if  i==17:
        try:
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable',	'Group',	'Key1',	'Weekday1',	'Time1',	'TimeVariable1',	'TimeStamp1',	'Group2',	'key2',	'Weekday2',	'Time2',	'TimeVariable2',	'TimeStamp2',	'Quality',	'QualityValue',	'Type',	'TypeValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid'); 