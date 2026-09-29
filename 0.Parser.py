"""
0.Parser.py
Step 0 of the pipeline: parse one OhioT1DM XML file into one CSV per data type.

Created: 24 October 2022
Author:  mbaxdg6 (Daniel Gasca Garcia)

What it does
    Reads the training XML of a single participant (<id>-ws-training.xml) and
    writes one CSV for each top-level element of the XML (glucose_level,
    finger_stick, basal, temp_basal, bolus, meal, sleep, work, stressors,
    hypo_event, illness, exercise, basis_heart_rate, basis_gsr,
    basis_skin_temperature, basis_air_temperature, basis_steps, basis_sleep).
    Each XML <event> becomes one line of its CSV.

Inputs
    globals.id     participant ID (one of 540, 544, 552, 559, 563, 567, 570,
                   575, 584, 588, 591, 596)
    globals.path1  folder containing the OhioT1DM XML files
    <path1>/<id>-ws-training.xml
    Only the TRAINING portion of OhioT1DM is used, not the test files.

Outputs
    <path2>/<element_tag><id>-ws-training.csv   (one file per element)
    e.g. glucose_level540-ws-training.csv

Output line format
    Lines are comma-separated with " , " and have no header row. Every line
    starts with a single space. For each attribute of the event:
      - timestamp attributes (ts, tend, tbegin, ts_begin, ts_end) are expanded
        into five fields:
            <Weekday>-<YYYY-MM-DD> , <Weekday>-<HH:MM:SS> , <Weekday> ,
            <HH:MM:SS> , <attribute name> , <original value>
      - any other attribute is written as:  <attribute name> , <value>
      - an attribute whose value is a single space is written as:
            <attribute name> , .
    The element tag is written once, at the start of the line.
    Column names are assigned later, in 1.ColumnNamer.py.

Notes
    - OhioT1DM timestamps use the format dd-mm-YYYY HH:MM:SS; the fixed
      character slices below rely on that exact format.
    - Output files are overwritten on every run.
"""

# Importing libraries

import xml.etree.ElementTree as ET
import datetime
import calendar
import os
import globals
# 540,544,552,567,584,596,559,563,570,575,588,591
# XML attributes that hold timestamps; these are expanded into date/time fields.
keys={'ts','tend','tbegin','ts_begin','ts_end'};

# --- Configurable global variables (set in globals.py) ---
id = globals.id;
fileToRead=str(id)+"-ws-training";
path1=globals.path1;
path2=globals.path2;

# Load the participant's XML. The root is <patient id weight insulin_type>.
ohioTree = ET.parse(str(path1)+str(fileToRead)+'.xml');
ohioRoot = ohioTree.getroot();

# Collect the tag of every top-level element (one per data type).
elemList = [];

for child in ohioRoot:
    print(child.tag, child.attrib);
    elemList.append(child.tag);

# Duplicates are removed
elemList = list(set(elemList));
# Printing the number of distinct data types found
print(len(elemList));


# Loop over the top-level elements BY POSITION (ohioRoot[x]). elemList is only
# used for its length; this assumes each tag appears once under the root, as
# in the OhioT1DM files.
for x in range(len(elemList)):
    # Create (or empty) the output CSV for this data type.
    open(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv", 'w').close();
    # Each child y is one <event> of this data type.
    for y in ohioRoot[x]:
        # str1 accumulates the output line. The initial ' ' marks "nothing
        # written yet", so the first attribute also writes the element tag.
        str1=' ';
        for z in range(len(y.keys())):
            # ---- First attribute of the event: prefix the element tag ----
            if str1==' ':
                if y.attrib[y.keys()[z]]==' ':
                    # Blank value: write the attribute name and '.'
                    str1=str1+ohioRoot[x].tag+str(" , ")+y.keys()[z]+str(" , .");   
                else:
                    if y.keys()[z] in keys: 
                        # Timestamp (dd-mm-YYYY HH:MM:SS): derive weekday,
                        # ISO date and time from fixed character positions.
                        try:   
                            dateMeasurement = calendar.day_name[datetime.date(int(y.attrib[y.keys()[z]][6:10]),int(y.attrib[y.keys()[z]][3:5]),int(y.attrib[y.keys()[z]][0:2])).weekday()];
                            dateV=y.attrib[y.keys()[z]][6:10]+"-"+y.attrib[y.keys()[z]][3:5]+"-"+y.attrib[y.keys()[z]][0:2];
                            time=datetime.time(int(y.attrib[y.keys()[z]][11:13]),int(y.attrib[y.keys()[z]][14:16]),int(y.attrib[y.keys()[z]][17:19]));
                            str1=str1+ohioRoot[x].tag+str(" , ")+str(dateMeasurement)+'-'+str(dateV)+str(" , ")+str(dateMeasurement)+'-'+str(time)+str(" , ")+str(dateMeasurement)+str(" , ")+str(time)+str(" , ")+y.keys()[z]+str(" , ")+y.attrib[y.keys()[z]];
                            # print(dateMeasurement);      
                            # print(y.attrib[y.keys()[z]][11:13]);
                            # print(y.attrib[y.keys()[z]][14:16]);
                            # print(y.attrib[y.keys()[z]][17:19]);
                            # print(time);
                        except:
                            # Malformed timestamp: the attribute is skipped and
                            # only a message is printed.
                            print('Not valid');
                    else:
                        # Non-timestamp attribute: name , value
                        str1=str1+ohioRoot[x].tag+str(" , ")+y.keys()[z]+str(" , ")+y.attrib[y.keys()[z]];

                
            # ---- Remaining attributes: same logic, without the tag ----
            else:
                if y.attrib[y.keys()[z]]==' ':
                    str1=str1+str(" , ")+y.keys()[z]+str(" , .");
                else:
                    if y.keys()[z] in keys:
                        try:
                            dateMeasurement = calendar.day_name[datetime.date(int(y.attrib[y.keys()[z]][6:10]),int(y.attrib[y.keys()[z]][3:5]),int(y.attrib[y.keys()[z]][0:2])).weekday()]; 
                            dateV=y.attrib[y.keys()[z]][6:10]+"-"+y.attrib[y.keys()[z]][3:5]+"-"+y.attrib[y.keys()[z]][0:2];
                            time=datetime.time(int(y.attrib[y.keys()[z]][11:13]),int(y.attrib[y.keys()[z]][14:16]),int(y.attrib[y.keys()[z]][17:19]));
                            str1=str1+str(" , ")+str(dateMeasurement)+'-'+str(dateV)+str(" , ")+str(dateMeasurement)+'-'+str(time)+str(" , ")+str(dateMeasurement)+str(" , ")+str(time)+str(" , ")+y.keys()[z]+str(" , ")+y.attrib[y.keys()[z]];
                            # print(dateMeasurement);      
                            # print(y.attrib[y.keys()[z]][11:13]);
                            # print(y.attrib[y.keys()[z]][14:16]);
                            # print(y.attrib[y.keys()[z]][17:19]);
                            # print(time);
                        except:
                            print('Not valid');
                    else:
                         str1=str1+str(" , ")+y.keys()[z]+str(" , ")+y.attrib[y.keys()[z]];                  
        # Append the finished line for this event to the CSV.
        file = open(globals.path2+str(ohioRoot[x].tag)+str(fileToRead)+".csv", 'a');
        file.write(str(str1));
        file.write('\n');
        file.close();
        print(str1); 
