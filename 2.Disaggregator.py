"""
2.Disaggregator.py   (header of the original file reads "2.Disagregator.py")
Step 2 of the pipeline: split each data type into one CSV per calendar day.

Created: 2 November 2022
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    For every data type produced by 0.Parser.py and named by 1.ColumnNamer.py,
    reads <tag><id>-ws-training_wCN.csv, groups its rows by the second column
    ("Group", which holds "<Weekday>-<YYYY-MM-DD>") and writes one file per
    day. Each output file gets a header with the column names for that data
    type.

Inputs
    globals.id, globals.path1, globals.path2
    <path1>/<id>-ws-training.xml        (only used to list the element tags)
    <path2>/<tag><id>-ws-training_wCN.csv   (output of 1.ColumnNamer.py)

Outputs
    <path2>/<tag><id>-ws-training<Weekday>-<YYYY-MM-DD>.csv
    e.g. glucose_level540-ws-training<Weekday>-<YYYY-MM-DD>.csv
    One file per data type and per day with data. Existing files are
    overwritten.

IMPORTANT - positional assumption
    The column names written for each data type are chosen by the POSITION of
    the element under the XML root (i == 0, 1, 2, ...), not by its tag name.
    The labels next to each branch below (glucose_level, finger_stick, ...)
    describe the order in which the elements appear in the OhioT1DM files:
        0 glucose_level, 1 finger_stick, 2 basal, 3 temp_basal, 4 bolus,
        5 meal, 6 sleep, 7 work, 8 stressors, 9 hypo_event, 10 illness,
        11 exercise, 12 basis_heart_rate, 13 basis_gsr,
        14 basis_skin_temperature, 15 basis_air_temperature, 16 basis_steps,
        17 basis_sleep
    An XML with the same tags in a different order (or with an element
    missing) produces files with the wrong column names, without any error.
    Downstream scripts then fail with a "Usecols do not match columns" error,
    several steps later.
"""

# Importing libraries

from itertools import groupby
import xml.etree.ElementTree as ET
import csv
import globals

# --- Configurable global variable ---
id = globals.id;
fileToRead=str(id)+"-ws-training";
path1=globals.path1;
path2=globals.path2;

# The XML is read again only to get the list of element tags, which
# are used to build the input and output file names.
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

# One branch per data type. Every branch does the same thing; only the
# header written to the output files changes. The try/except skips data
# types whose _wCN file does not exist (or cannot be read) for this
# participant, printing 'Not valid'.
for i in range(len(elemList)):
    print (i);
    # Blood Glucose
    # Position 0 -> expected tag: glucose_level. CGM readings (every 5 min); value column: BGValue.
    if  i==0:
        try: 
            with open(str(path2)+str(ohioRoot[i].tag)+str(fileToRead)+"_wCN"+".csv") as csv_file:
                reader = csv.reader(csv_file);
                next(reader); #skip header
        
                #Group by column 
                # Column 1 ("Group") is "<Weekday>-<YYYY-MM-DD>", so each group is
                # one calendar day. groupby needs the rows sorted by that key first.
                lst = sorted(reader, key=lambda x : x[1])
                groups = groupby(lst, key=lambda x : x[1])

                #Write file for each variable
                for k,g in groups:
                    # One output file per day, e.g. glucose_level540-ws-training<Weekday>-<YYYY-MM-DD>.csv
                    filename = str(ohioRoot[i].tag)+str(fileToRead)+k + '.csv';
                    with open(str(path2)+str(filename), 'w', newline='') as fout:
                        csv_output = csv.writer(fout);
                        csv_output.writerow(['Variable', 'Group','Key','Weekday','Time','TimeVariable','TimeStamp','Value','BGValue']);  #header
                        for line in g:
                            csv_output.writerow(line);
        except:
            print('Not valid');
    # Finger stick 
    # Position 1 -> expected tag: finger_stick. capillary glucose; value column: FingerValue.
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
    # Position 2 -> expected tag: basal. programmed basal rate; value column: BasalValue.
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
    # Position 3 -> expected tag: temp_basal. temporary basal (start and end timestamps); value column: TempBasalValue.
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
    # Position 4 -> expected tag: bolus. insulin bolus (ts_begin, ts_end); columns: BolusValue, CarbInputValue.
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
    # Position 5 -> expected tag: meal. self-reported meals; columns: TypeFood, CarbsValue.
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
    # Position 6 -> expected tag: sleep. self-reported sleep (start and end); column: QualityValue.
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
    # Position 7 -> expected tag: work. work periods (start and end); column: IntensityValue.
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
    # Position 8 -> expected tag: stressors. self-reported stressors; columns: typeValue, DescriptionValue.
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
    # Position 9 -> expected tag: hypo_event. self-reported hypoglycaemia; timestamp only.
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
    # Position 10 -> expected tag: illness. self-reported illness; columns: typeValue, DescriptionValue.
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
    # Position 11 -> expected tag: exercise. self-reported exercise; intensity, type, duration, competitive.
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
    # Position 12 -> expected tag: basis_heart_rate. wristband heart rate; value column: BHValue.
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
    # Position 13 -> expected tag: basis_gsr. wristband galvanic skin response; value column: GSRValue.
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
    # Position 14 -> expected tag: basis_skin_temperature. wristband skin temperature; value column: BSTValue.
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
    # Position 15 -> expected tag: basis_air_temperature. wristband air temperature; value column: BSkinValue.
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
    # Position 16 -> expected tag: basis_steps. wristband step count; value column: BStepsValue.
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
    # Position 17 -> expected tag: basis_sleep. wristband sleep (start and end); columns: QualityValue, TypeValue.
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