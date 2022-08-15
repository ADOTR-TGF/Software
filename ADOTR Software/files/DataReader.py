#! /usr/bin/python3
import re
import json
import pandas as pd
import glob
import os
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning) #suppresses a 'futurewarning' concerning an (bug)incompatibility between python list strings and numpy string element wise comparison. can be ignored UNLESS in future versions of python this gets fixed. This line of code and others like it are the culprit: 'if lines[i]==np.array(traceStrings0)'
import math
import datetime

files = sorted(glob.glob("/Detector1/data/*.txt",recursive = True))
trace_files = sorted(glob.glob("/Detector1/data/*.xtr",recursive = True))


#The following deals with the listmode data files (.txt)

def DataTable(fileName):
    print(fileName)
    lmStrings, timeStrings = readfile(fileName)
    tsSeconds = timestampsToSecondsofDay(timeStrings)       
    D = []
    for i in range(len(tsSeconds)):
        d = pd.concat([listmodeToTable(x) for x in lmStrings[i:i+1]], ignore_index = True)
        #d['PPS'] = pd.Series([int('{0:08b}'.format(x)[-8]) for x in d['flags']])    
        diffwc = np.diff(d.wc)    
        diffwc_index = list(np.where(diffwc<0)[0])
        timestamp_pps = math.floor(tsSeconds[i])
        if diffwc_index != []:
            rowc = np.append(d.wc[:diffwc_index[0]+1],d.wc[diffwc_index[0]+1:]+2**36)
            d['SecondsofDayNoPPS'] = tsSeconds[i] + 25.0e-9*(rowc - rowc[-1])
            PPS_wc = list(rowc[d.pps==1])
            if PPS_wc != []:
                n = len(PPS_wc)-1
                dt = n/float(PPS_wc[-1]-PPS_wc[0])
                d['SecondsofDayPPS'] = timestamp_pps + dt*(rowc - PPS_wc[-1])
            else:
            	pass
            bgrateofbuffer = 10**3*(d.SecondsofDayNoPPS.iat[-1]-d.SecondsofDayNoPPS.iat[0])/len(d)
            print(fileName)
            print('Alert: Wall Clock rollover in buffer '+ str(i))
            print('time difference of ' + str(10**3*(d.SecondsofDayNoPPS[diffwc_index[0]+1]-d.SecondsofDayNoPPS[diffwc_index[0]]))+'ms')
            print('Average background rate of buffer ' + str(bgrateofbuffer) +'ms/event')
        else:
            d['SecondsofDayNoPPS'] = tsSeconds[i] + 25.0e-9*(d.wc - d.wc.iat[-1])
            PPS_wc = list(d.wc[d.pps==1])
            if PPS_wc != []:
            	n = len(PPS_wc)-1
            	dt = n/float(PPS_wc[-1]-PPS_wc[0])
            	d['SecondsofDayPPS'] = timestamp_pps + dt*(d.wc - PPS_wc[-1])
            else:
            	pass
            
        D.append(d)
    data = pd.concat(D,ignore_index = True)
    data['Seconds'] = (data.SecondsofDayNoPPS-data.SecondsofDayNoPPS.iat[0])
    T = []
    if 'SecondsofDayPPS' in data:
        for i in range(len(data)):
            ts = datetime.timedelta(seconds=data.SecondsofDayPPS[i])
            T.append(ts)
        data['TimeStampsPPS']=T
    else:
        for i in range(len(data)):
            ts = datetime.timedelta(seconds=data.SecondsofDayNoPPS[i])
            T.append(ts)
        data['TimeStampsNoPPS']=T
    return(data)

def readfile(fileName):
    with open(fileName) as f:
        lines = f.readlines()

    timeStrings = [s for s in lines if len(s) < 30 and len(s) > 4]
    timeStrings = timeStrings[::4]  
    lmStrings = [s for s in lines if "lm_data" in s]
    return(lmStrings,timeStrings)

def timestampsToSecondsofDay(timeString):
    timestamps = list(map(lambda x: x.split(" ")[3:len(x)],timeString))
    timestamps = [list(map(int,x)) for x in timestamps]
    tsSeconds = []
    for i in range(len(timestamps)):
        ts = timestamps[i][0]*3600 + timestamps[i][1]*60 + timestamps[i][2] + timestamps[i][3]*10**-6
        tsSeconds.append(ts)
    return(tsSeconds)

def listmodeToTable(lmString):
    #jsonDict = json.loads(re.sub("eRC[0-9]{4} ", "", lmString))['lm_data']  #For THOR data
    jsonDict = json.loads(lmString)['lm_data']
    data = pd.DataFrame.from_dict(jsonDict)
    return(data)


def getBgRate(data):
    totalTime = data.Seconds.max() - data.Seconds.min()
    ratePerSecond = len(data) / totalTime
    return(ratePerSecond)

def getBgRateFromFile(fileName):
    data = DataTable(fileName)
    bgRate = getBgRate(data)
    return(bgRate)

def isGpsWorking(fileName):
    data = DataTable(fileName)
    diffs = data[data['PPS'] == 1]['Seconds'].diff()
    isGoodTick = diffs.round(3).apply(lambda x: x == 1)
    goodTicks = isGoodTick.sum()
    print(goodTicks)
    print(len(diffs) - 1)
    return goodTicks >= (0.95 * (len(diffs) - 1))

def isGpsWorkingInLastFile():
    files.sort(key = os.path.getmtime)
    toReturn = isGpsWorking(files[-1])
    return toReturn

#the following deals with the Trace data files (.xtr)

def readtracefile(fileName):
    with open(fileName) as f:
        lines = f.readlines()
 
    traceStrings0 = [s for s in lines if " 0 {" in s]
    traceStrings1 = [s for s in lines if " 1 {" in s]
    traceStrings2 = [s for s in lines if " 2 {" in s]
    traceStrings3 = [s for s in lines if " 3 {" in s]
    traceStrings4 = [s for s in lines if " 4 {" in s]
    timeString0 = '0 0 0 0 0 0 0 0'
    timeString1 = '0 0 0 0 0 0 0 0'
    timeString2 = '0 0 0 0 0 0 0 0'
    timeString3 = '0 0 0 0 0 0 0 0'
    timeString4 = '0 0 0 0 0 0 0 0'
    for i in range(len(lines)):
        if lines[i]==np.array(traceStrings0):
            timeString0 = lines[i-4]
        else:pass
        if lines[i]==np.array(traceStrings1):
            timeString1 = lines[i-4]
        else:pass
        if lines[i]==np.array(traceStrings2):
            timeString2 = lines[i-4]
        else:pass
        if lines[i]==np.array(traceStrings3):
            timeString3 = lines[i-4]
        else:pass
        if lines[i]==np.array(traceStrings4):
            timeString4 = lines[i-4]
        else:pass
    traceStrings = np.array([traceStrings0,traceStrings1,traceStrings2,traceStrings3,traceStrings4])
    timeStrings = np.array([timeString0,timeString1,timeString2,timeString3,timeString4])
    return(traceStrings,timeStrings)

def TraceToTable(traceString):
    jsonDict = json.loads(re.sub(" [0-9] ", "", traceString))
    tracedata = pd.DataFrame.from_dict(jsonDict)
    return(tracedata)

def tracebuffer(traceString,tsSecond,C,buffer_num):
    if [TraceToTable(x) for x in traceString] != []:
        tracedata = pd.concat([TraceToTable(x) for x in traceString], ignore_index = True)
        tracedata['buffer#']= buffer_num
        tracedata['finefreeze']= tracedata.freeze*256+128
        tracedata['wc']=tracedata.finefreeze - C + tracedata.index
        rs = tracedata.wc * 25e-9
        tracedata['Seconds'] = rs - min(rs)
        tracedata['SecondsofDayNoPPS']=tsSecond - (max(tracedata.Seconds) - tracedata.Seconds)
        T = []
        for i in range(len(tracedata)):
            ts = datetime.timedelta(seconds=tracedata.SecondsofDayNoPPS[i])
            T.append(ts)
        tracedata['TimeStampsNoPPS']=T      
    else: tracedata = pd.Series('No trace data')
    return(tracedata)

def TraceDataTable(fileName):
    C = [4096,1024,1024,1024,1024]
    traceStrings, timeStrings = readtracefile(fileName)
    tsSeconds = timestampsToSecondsofDay(timeStrings)
    
    tracedata0 = tracebuffer(traceStrings[0],tsSeconds[0],C[0],0)    
    tracedata1 = tracebuffer(traceStrings[1],tsSeconds[1],C[1],1)
    tracedata2 = tracebuffer(traceStrings[2],tsSeconds[2],C[2],2)
    tracedata3 = tracebuffer(traceStrings[3],tsSeconds[3],C[3],3)
    tracedata4 = tracebuffer(traceStrings[4],tsSeconds[4],C[4],4)
    
    #tracedata = np.array([tracedata0,tracedata1,tracedata2,tracedata3,tracedata4])
    return(tracedata0,tracedata1,tracedata2,tracedata3,tracedata4)




