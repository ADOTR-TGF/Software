Instructions for DataReader.py and DataPlotter.py

-open terminal and navigate to directory where DataReader.py is located
-open python3 environment

$python
Python 3.6.8 (default, Sep  9 2021, 07:49:02) 
[GCC 8.5.0 20210514 (Red Hat 8.5.0-3)] on linux
Type "help", "copyright", "credits" or "license" for more information.

-To view listmode data table:

>>> import DataReader as DR
>>> lmdata = DR.DataTable(DR.files[1]) #DR.files is an array of eRC*.txt files. DR.files[1] is the second file in that array.
>>> lmdata
       num_events  energies  psd           wc  peak  tbnt  flags  PPS  SecondsofDayNoPPS  SecondsofDayPPS     Seconds   TimeStampsPPS
0            2047       702  255  24147164252   508     0      0    0       56226.171610     56226.167014    0.000000 15:37:06.167014
1            2047       526  154  24147356695   498     0      0    0       56226.174015     56226.169420    0.002406 15:37:06.169420
2            2047       236  122  24147518987   464     0      0    0       56226.176044     56226.171448    0.004434 15:37:06.171448
3            2047       250   55  24147870700   461     0      0    0       56226.180440     56226.175845    0.008831 15:37:06.175845
4            2047      3431  570  24148874881   787     0      0    0       56226.192992     56226.188397    0.021383 15:37:06.188397
...           ...       ...  ...          ...   ...   ...    ...  ...                ...              ...         ...             ...
40915        2047       319    6  34417798605   470     0      0    0       56354.553341     56354.546649  128.382929 15:39:14.546649
40916        2047       306   69  34418001661   482     0      0    0       56354.555879     56354.549187  128.385468 15:39:14.549187
40917        2047      1041   72  34418057988   549     0      0    0       56354.556583     56354.549891  128.386172 15:39:14.549891
40918        2047       684  229  34418170156   517     0      0    0       56354.557985     56354.551293  128.387574 15:39:14.551293
40919        2047       911  153  34418199003   524     0      0    0       56354.558346     56354.551654  128.387934 15:39:14.551654

[40920 rows x 12 columns]


-The data columns are: 
num_events 
energies (ADC values) 
psd(see firmware documentation)
wc (ADC wall clock 36bit), 
peak(see firmware documentation) 
tbnt(see firmware documentation) 
flags (see firmware documentation)
PPS (pulse per second boolian value. If 'true'(1) that event is a PPS event) 
SecondsofDayNoPPS (Absolute time in seconds of the day using only the computer timetag of data readout. 10's of milliseconds of error) 
SecondsofDayPPS (Absolute time in seconds of the day using PPS events and computer timetag to align the ADC wall clock to absolute time. 1-2us of error) 
Seconds (relative seconds) 
TimeStampsPPS (SecondsofDayPPS converted to datetime format. Note that python datetime truncates to microseconds and the precision is lost)

-A note on if the wall clock rolls over in the middle of a buffer:
The analysis code is written to account for this. The wall clock values are not altered in the data table so comparison to trace files can be made, but the rollover is accounted for when converting the wall clock to seconds (both relative and absolute). An Alert will print when running the DataTable() function if a rollover occurs. It will say which buffer it occured in, what the time difference was between the last wc value and the new rolled over wc value and what the average count rate of the buffer is. If the time difference if significantly different from the buffer's average count rate this should be investigated.  

-Seconds of day is calculated as follows: 

SecondsofDayNoPPS: the last event in each buffer is associated with the first computer time tag (of which there are four) at the beginning of each buffer and using each events relative time subtracts from that reference time to give a first order aproximation of the absolute time for each event. This always done by default. 

SecondsofDayPPS: If there are PPS events in the data they will be used to calculate a more accurate absolute time in two ways. First an average delta time between clock ticks is found using the first and last PPS event in each buffer. The nominal value is 12.5e-9seconds but is never exactly that because of clock drift. Second, the last PPS event in each buffer is assigned the integer seconds value of the datetime stamp used in the first order approximation. i.e. if the datetime stamp in seconds of day is 5623.004598 then the last PPS event in the buffer is assigned the time 5623.000000. Using this and the more accurate sample rate the absolute time of all events in the buffer are calculated from the wall clock and the last PPS locked in time.  note: this is done buffer by buffer. This is only done if PPS events exist in the data. If the GPS wasn't working and no PPS events recorded the code will not output a SecondsofDayPPS column in the data table

-You can filter DR.files to make an array that only contain Nai detector files for example. e.g.
>>> naiFiles = [x for x in DR.files if "nai" in x]
>>> lmdata = DR.DataTable(naiFiles[0])

-any column in the data table can be called using the column name. e.g.
>>> lmdata.SecondsofDayPPS
0        56226.167014
1        56226.169420
2        56226.171448
3        56226.175845
4        56226.188397
             ...     
40915    56354.546649
40916    56354.549187
40917    56354.549891
40918    56354.551293
40919    56354.551654
Name: SecondsofDayPPS, Length: 40920, dtype: float64
-Note: that when the data table is displayed any Seconds value is truncating to the microsecond but the full precision isn't lost

-An element of any column can be called via array indexing e.g. 
>>> lmdata.SecondsofDayPPS[0]
56226.167014418366

-Conditional statements can be used to filter data in the table by column. e.g.
>>> lmdata.PPS[lmdata.PPS==1]
257      1
568      1
905      1
1228     1
1520     1
        ..
39442    1
39768    1
40103    1
40421    1
40748    1
Name: PPS, Length: 128, dtype: int64

-This filtered the column PPS elementwise under the condition that data.PPS was equal to 1.

-Pulse Per Second Diagnostics:

-To check if the PPS flags in a file exist and are coming in every one second.
>>> DR.isGpsWorking(DR.files[1])
127  #number of PPS flags within 1.001 seconds of eachother
127  #total number of PPS flags in file
True #If ratio between these two numbers is greater than 95% returns True

-To check the PPS flags in the most recent file created.
DR.isGpsWorkingInLastFile()
127
127
True

-To view Trace data tables:
NOTE: The C values in TraceDataTable must match the C values used in onedet.py where the trace capture parameters are set.
>>> tracedata = DR.TraceDataTable(DR.trace_files[1])
>>> tracedata[0]
           freeze  pulse  buffer#     finefreeze             wc       Seconds  SecondsofDayNoPPS TimeStampsNoPPS
0      4033127893      0        0  1032480740736  1032480726400  0.000000e+00       56922.098006 15:48:42.098006
1      4033127893     28        0  1032480740736  1032480726401  1.250010e-08       56922.098006 15:48:42.098006
2      4033127893     28        0  1032480740736  1032480726402  2.500019e-08       56922.098006 15:48:42.098006
3      4033127893     28        0  1032480740736  1032480726403  3.750029e-08       56922.098006 15:48:42.098006
4      4033127893     28        0  1032480740736  1032480726404  5.000038e-08       56922.098006 15:48:42.098006
...           ...    ...      ...            ...            ...           ...                ...             ...
28701  4033127893     28        0  1032480740736  1032480755101  3.587625e-04       56922.098365 15:48:42.098365
28702  4033127893     28        0  1032480740736  1032480755102  3.587750e-04       56922.098365 15:48:42.098365
28703  4033127893     28        0  1032480740736  1032480755103  3.587875e-04       56922.098365 15:48:42.098365
28704  4033127893     28        0  1032480740736  1032480755104  3.588000e-04       56922.098365 15:48:42.098365
28705  4033127893     28        0  1032480740736  1032480755105  3.588125e-04       56922.098365 15:48:42.098365

[28706 rows x 8 columns]
>>> tracedata[3]
          freeze  pulse  buffer#     finefreeze             wc       Seconds  SecondsofDayNoPPS TimeStampsNoPPS
0     4033127985      0        3  1032480764288  1032480763264  0.000000e+00       56922.098339 15:48:42.098339
1     4033127985      0        3  1032480764288  1032480763265  1.250010e-08       56922.098339 15:48:42.098339
2     4033127985      0        3  1032480764288  1032480763266  2.500019e-08       56922.098339 15:48:42.098339
3     4033127985      0        3  1032480764288  1032480763267  3.750029e-08       56922.098339 15:48:42.098339
4     4033127985      0        3  1032480764288  1032480763268  5.000038e-08       56922.098339 15:48:42.098339
...          ...    ...      ...            ...            ...           ...                ...             ...
2103  4033127985      0        3  1032480764288  1032480765367  2.628750e-05       56922.098365 15:48:42.098365
2104  4033127985      0        3  1032480764288  1032480765368  2.630000e-05       56922.098365 15:48:42.098365
2105  4033127985      0        3  1032480764288  1032480765369  2.631250e-05       56922.098365 15:48:42.098365
2106  4033127985      0        3  1032480764288  1032480765370  2.632500e-05       56922.098365 15:48:42.098365
2107  4033127985      0        3  1032480764288  1032480765371  2.633750e-05       56922.098365 15:48:42.098365

[2108 rows x 8 columns]

>>> tracedata[1]
0    No trace data
dtype: object
>>> tracedata[2]
0    No trace data
dtype: object
>>> tracedata[4]
0    No trace data
dtype: object

-In this example trace file only buffers 0 and 3 were triggered and saved to the .xtr file. 

-The trace data columns are:
freeze (32 bit wall clock time (upper 32bits of the 36bit wall clock used in listmode) when the trace was triggered) 
pulse (trace sample amplitudes)
buffer# (there are 5 trace buffers(0-4) where 0 is the largest)
finefreeze (freeze wall clock time with lower 4 bits added to match the 36bit wall clock of the listmode data)
wc (wall clock time for each pulse(sample))
Seconds (relative seconds of each sample using the nominal 12.5e-9 sampling rate and wc)
SecondsofDayNoPPS (Absolute time in seconds of the day using only the computer timetag)
TimeStampsNoPPS (SecondsofDayNoPPS converted to datetime format. Note that python datetime truncates to microseconds and loses the precision)

-absolute time in seconds of day is calculated as follows: 

SecondsofDayNoPPS: the last event in each buffer is associated with the first computer time tag (of which there are four) at the beginning of each buffer and using each events relative time subtracts from that reference time to give a first order aproximation of the absolute time for each sample. This is a very very rough estimate and should only be used to associate the trace file to a grouping of events in the listmode but not to align them in any way.  
Note: there are no PPS events in the trace files. In order to align the trace time with PPS precision timing the ADC wall clock of the associated listmode data along with it's SecondsofDayPPS time can be used to align the trace data wall clock to the PPS of the listmode data.  

-tracedata columns can be called in the same way as previously mentioned. e.g.
>>> tracedata[0].wc
0        1032480726400
1        1032480726401
2        1032480726402
3        1032480726403
4        1032480726404
             ...      
28701    1032480755101
28702    1032480755102
28703    1032480755103
28704    1032480755104
28705    1032480755105
Name: wc, Length: 28706, dtype: int64

-To plot data
>>> import DataPlotter as DP

List mode data plotting:

-Count rate histrogram: CountRateHist(fileName,binsize,tmin,tmax):

Entire data set with bin size of 50ms
>>> DP.CountRateHist(DP.files[1],.05,data.SecondsofDayPPS[0],data.SecondsofDayPPS.iat[-1]) 

subset of the data with bin size 1ms. 
>>> DP.CountRateHist(DP.files[1],.001,56226.167014,56227)

-Energy vs time scatter plot: EnergyvsTimeScatter(fileName,tmin,tmax,maxenergy=66000,markersize=.01): Note: maxenergy defaults to 66000 and markersize defaults to .01

entire file
>>> DP.EnergyvsTimeScatter(DP.files[1],data.SecondsofDayPPS[0],data.SecondsofDayPPS.iat[-1])

entire file with a max ADC energy value of 10,000 and markersize of .02
>>> DP.EnergyvsTimeScatter(DP.files[1],data.SecondsofDayPPS[0],data.SecondsofDayPPS.iat[-1],10000,.02)

-Energy Spectrum: EnergySpectrum(fileName,binsize,Emin=0,Emax=66000,log=False):
Emin defaults to 0, Emax defaults to 66000, log scale defaults to False(linear)

Log scale spectrum binned at 10 with max energy 10000.  
>>> DP.EnergySpectrum(DP.files[1],10,Emax=10000,log=True)

Linear scale spectrum binned at 10 with max energy 10000. 
>>> DP.EnergySpectrum(DP.files[1],10,Emax=10000)

Trace file data plotting:

-Trace plot: Traceplot(fileName,Buffer,tmin,tmax)

trace plot of buffer 0 
>>> DP.Traceplot(DP.trace_files[1],0,tracedata[0].SecondsofDayNoPPS[0],tracedata[0].SecondsofDayNoPPS.iat[-1])

trace plot of buffer 3
>>> DP.Traceplot(DP.trace_files[1],3,tracedata[3].SecondsofDayNoPPS[0],tracedata[3].SecondsofDayNoPPS.iat[-1])

trace plot of a subset of buffer 3
>>> DP.Traceplot(DP.trace_files[1],3,56922.098345,56922.098365)


-To export data tables to csv file:
lmdata.to_csv('file_name.csv')
tracedata[i].to_csv('file_name.csv')

To export data tables to txt file:
lmdata.to_csv('file_name.txt',sep='\t')
tracedata[i].to_csv('textfiletest.txt',sep='\t')

