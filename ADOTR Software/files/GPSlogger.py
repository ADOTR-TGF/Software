#! /usr/bin/python3.8
from gps import *
import time, inspect

filename = 'GPSData_'+time.strftime("%Y%m%d_%H%M%S")+'.csv'
path = '/Detector1/GPSdata/'+filename
f = open(path,'w+')
gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
f.write("GPStime(utc),latitude,longitude,altitude(m),speed(km/h)\n")
while True:
	report = gpsd.next()
	if report['class']=='TPV':
		GPStime = str(getattr(report,'time',''))
		lat = str(getattr(report,'lat',0.0))
		lon = str(getattr(report,'lon',0.0))
		alt = str(getattr(report,'altMSL',0.0))
		spe = str(getattr(report,'speed',0.0))
		f.write(GPStime+','+lat+','+lon+','+alt+','+spe+'\n')
		
f.close()
