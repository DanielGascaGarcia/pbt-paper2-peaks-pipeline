#Code: 0.Parser.py
#Description: Parsing XML file from Ohio Dataset.
#Created 24th October 2022
#Author: mbaxdg6

# Importing libreries

import xml.etree.ElementTree as ET
import datetime
import calendar
import os
import globals
# 540,544,552,567,584,596,559,563,570,575,588,591
keys={'ts','tend','tbegin','ts_begin','ts_end'};
# -----------------------------------------------------------#
#              Configurable variables 
# -----------------------------------------------------------#
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



for x in range(len(elemList)):
    open(str(path2)+str(ohioRoot[x].tag)+str(fileToRead)+".csv", 'w').close();
    for y in ohioRoot[x]:
        str1=' ';
        for z in range(len(y.keys())):
            if str1==' ':
                if y.attrib[y.keys()[z]]==' ':
                    str1=str1+ohioRoot[x].tag+str(" , ")+y.keys()[z]+str(" , .");   
                else:
                    if y.keys()[z] in keys: 
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
                            print('Not valid');
                    else:
                        str1=str1+ohioRoot[x].tag+str(" , ")+y.keys()[z]+str(" , ")+y.attrib[y.keys()[z]];

                
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
        file = open('C:/OhioDataset/ExploratoryAnalysisData/OhioT1DM/2018/parsedTexts/'+str(ohioRoot[x].tag)+str(fileToRead)+".csv", 'a');
        file.write(str(str1));
        file.write('\n');
        file.close();
        print(str1); 