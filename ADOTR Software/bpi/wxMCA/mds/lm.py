#!/usr/bin/python3.7
#
from __future__ import division

import numpy as np
import time
import json
import zmq
import communication as com

from datetime import datetime
import subprocess

#Version for PMT3k TGF firmware, 7/2022, including triggered traces (xtr):
version = 1.0

def pullbuffer(mds_client,sn,fout,reading_buffer,t1a,t1b,full):
    cmd_sel_0 = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
                 "data": {"fields": {"lm_mode": 0}}}
    cmd_sel_1 = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
                 "data": {"fields": {"lm_mode": 1}}}

    cmd_read = {"type": "mca_cmd", "name": "fpga_tgf_lm", "dir": "read", "sn": sn}

    #Select buffer for reading:
    if reading_buffer==0:
        mds_client.send_and_receive(json.dumps(cmd_sel_0).encode('utf-8')).decode('utf-8')            
    else:
        mds_client.send_and_receive(json.dumps(cmd_sel_1).encode('utf-8')).decode('utf-8')            

    #get the actual data & write to file.
    t2a=datetime.now() #capture the time the buffer is read and switched (before)

    #Read listmode data:
    ret = json.loads(mds_client.send_and_receive(json.dumps(cmd_read).encode('utf-8')).decode('utf-8'))
    lm_data = {"lm_data": ret[sn]['fields']}

    t2b=datetime.now() #capture the time the buffer is read and switched (after)

    #Convert all the 4 capture times to strings:
    st1a='%s %s %s %s %s %s %s\n' %(str(t1a.year),str(t1a.month),str(t1a.day),str(t1a.hour),str(t1a.minute),str(t1a.second),str(t1a.microsecond))
    st1b='%s %s %s %s %s %s %s\n' %(str(t1b.year),str(t1b.month),str(t1b.day),str(t1b.hour),str(t1b.minute),str(t1b.second),str(t1b.microsecond))
    st2a='%s %s %s %s %s %s %s\n' %(str(t2a.year),str(t2a.month),str(t2a.day),str(t2a.hour),str(t2a.minute),str(t2a.second),str(t2a.microsecond))
    st2b='%s %s %s %s %s %s %s\n' %(str(t2b.year),str(t2b.month),str(t2b.day),str(t2b.hour),str(t2b.minute),str(t2b.second),str(t2b.microsecond))

    #show reading buffer and flag saying if it's a full one, and all 4 time strings
    fout.write(str(reading_buffer) + ' ' + str(full) + "\n" + st1a+ st1b + st2a +  st2b  ) 

    
    fout.write(json.dumps(lm_data)+"\n") 

def pullxtr(mds_client,sn,statusfields,xtrnum,t1a,t1b):

    if xtrnum == 0:
        pulse_name = "fpga_tgf_xt28k"
    else:
        pulse_name = "fpga_tgf_xt2k_{}".format(xtrnum)
    cmd_read = {"type": "mca_cmd", "name": pulse_name, "dir": "read", "sn": sn}
    
    #get the actual data & write to file.
    t2a=datetime.now() #capture the time the buffer is read and switched (before)

    #Read trace data:
    ret_xtr = json.loads(mds_client.send_and_receive(json.dumps(cmd_read).encode('utf-8')).decode('utf-8'))
    pulse_data = {"freeze": statusfields['xtwc{}'.format(xtrnum)], "Tracesample": ret_xtr[sn]['registers']}

    t2b=datetime.now() #capture the time the buffer is read and switched (after)

    #Convert all the 4 capture times to strings:
    st1a='%s %s %s %s %s %s %s\n' %(str(t1a.year),str(t1a.month),str(t1a.day),str(t1a.hour),str(t1a.minute),str(t1a.second),str(t1a.microsecond))
    st1b='%s %s %s %s %s %s %s\n' %(str(t1b.year),str(t1b.month),str(t1b.day),str(t1b.hour),str(t1b.minute),str(t1b.second),str(t1b.microsecond))
    st2a='%s %s %s %s %s %s %s\n' %(str(t2a.year),str(t2a.month),str(t2a.day),str(t2a.hour),str(t2a.minute),str(t2a.second),str(t2a.microsecond))
    st2b='%s %s %s %s %s %s %s\n' %(str(t2b.year),str(t2b.month),str(t2b.day),str(t2b.hour),str(t2b.minute),str(t2b.second),str(t2b.microsecond))

    #create string to write to output file along with any other live traces:
    xtrdata = st1a+ st1b + st2a +  st2b + ' ' + str(xtrnum)  +' '+json.dumps(pulse_data)+"\n"
    return xtrdata
    

def process_lm(mds_client,sn,fout):

    cmd_results = {"type": "mca_cmd", "name": "fpga_results", "dir": "read", "sn": sn}

    #check status to see if either or both buffers is full:
    t1a=datetime.now()  #capture the time you first found out the buffer was full (before).
    # Check which list mode buffer is full
    # ret is a dictionary with keys "registers", "fields", "user"
    ret = json.loads(mds_client.send_and_receive(json.dumps(cmd_results).encode('utf-8')).decode('utf-8'))
    results = ret[sn]["registers"]
    buffer_0_is_full = (int(results[2])>>1) & 1
    buffer_1_is_full = (int(results[2])>>3) & 1

    t1b=datetime.now()  #capture the time you first found out the buffer was full (after).

    if buffer_0_is_full or buffer_1_is_full:
 
        #Buffer 0 gets priority this time if both are full:
        reading_buffer = 0 if buffer_0_is_full else 1

        print("Buffers (0,1) fullness, choice: ",buffer_0_is_full,buffer_1_is_full,reading_buffer)

        pullbuffer(mds_client,sn,fout,reading_buffer,t1a,t1b,1)
        status = 1

    else:
        status = 0
        
    return status
 

def xml22_daq(num_buffers,sn,sn_short,detlabel,rootdir):

    #LIST MODE COMMANDS:
    cmd_clr_0 = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
                 "data": {"fields": {"lm_mode": 0, "clear_statistics": 1, "clear_list_mode": 1, "run": 1}}}
    cmd_clr_1 = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
                 "data": {"fields": {"lm_mode": 1, "clear_statistics": 1, "clear_list_mode": 1, "run": 1}}}
    cmd_start_lm = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
                    "data": {"fields": {"clear_statistics": 1, "clear_list_mode": 1, "lm_run": 1, "run": 1}}}

    #TRIGGERED TRACE (XTR) COMMANDS:
    cmd_clr_xtr = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
               "data": {"fields": {"clear_trace": 1, "run": 1}}}
    cmd_start_xtr = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
                 "data": {"fields": {"clear_statistics": 1, "clear_trace": 1, "trace_run": 1, "run": 1}}}
    cmd_tgf_status = {"type": "mca_cmd", "name": "fpga_tgf_results", "dir": "read", "sn": sn}

    
    #start listmode data:

    mds_client = com.zmq_device("tcp://127.0.0.1:5507", "client")  # Communicate with MDS

    # Clear both listmode banks & Start the list-mode run
    mds_client.send_and_receive(json.dumps(cmd_clr_0).encode('utf-8')).decode('utf-8')
    mds_client.send_and_receive(json.dumps(cmd_clr_1).encode('utf-8')).decode('utf-8')
    mds_client.send_and_receive(json.dumps(cmd_start_lm).encode('utf-8')).decode('utf-8')
    #Clear and start the triggered trace run
    mds_client.send_and_receive(json.dumps(cmd_clr_xtr).encode('utf-8')).decode('utf-8')
    mds_client.send_and_receive(json.dumps(cmd_start_xtr).encode('utf-8')).decode('utf-8')
    #initialize state of traces-triggered-to-be-read-out as zeros:
    xtr_done=np.array([0,0,0,0,0])

    redundantfilename = 0
    lastfnamestring=""

    redundantfilename_xtr = 0
    lastfnamestring_xtr=""

    #loop until killed:
    while True:

        #File is .tmp while being written and moved to .txt when done.   Make sure that a new file
        #with the same name doesn't overwrite an older one by adding an appendage to the name.
        fnamestring =  "/"+rootdir+"/data/%s%s"%('ARM'+sn_short+'_'+detlabel,time.strftime("_lm_%y%m%d_%H%M%S"))
        appendage=""
        if fnamestring == lastfnamestring:
            appendage = "_"+str(redundantfilename)
            redundantfilename += 1
        else:
            redundantfilename = 0
            appendage=""
        file_name = fnamestring + appendage + ".tmp"
        file_name_after_closing = fnamestring + appendage + ".txt"
        lastfnamestring = fnamestring

        fout = open(file_name, 'w')

        buffer_count = 0  # Number of buffers read
        status = 0
        
        #collect & write data until file hits max size
        while buffer_count < num_buffers:

            status = process_lm(mds_client,sn,fout)
            buffer_count += status

            
            if buffer_count < num_buffers and status==0:
        
                t1a = datetime.now()
                ret_status = json.loads(mds_client.send_and_receive(json.dumps(cmd_tgf_status).encode('utf-8')).decode('utf-8'))
                t1b = datetime.now()
                statusfields =  ret_status[sn]['fields']
                xtr_done = np.array([ ret_status[sn]['user']['xt0_done'],
                                      ret_status[sn]['user']['xt1_done'],
                                      ret_status[sn]['user']['xt2_done'],
                                      ret_status[sn]['user']['xt3_done'],
                                      ret_status[sn]['user']['xt4_done']])
                print(xtr_done)                      
	
                if np.sum(xtr_done) > 0:

                    #Again make sure we don't double up on filenames:
                    fnamestring_xtr =  "/"+rootdir+"/data/"'ARM'+sn_short+'_'+detlabel+"_xtr"+time.strftime("_%y%m%d_%H%M%S")
                    
                    appendage_xtr=""
                    if fnamestring_xtr == lastfnamestring_xtr:
                        appendage_xtr = "_"+str(redundantfilename_xtr)
                        redundantfilename_xtr += 1
                    else:
                        redundantfilename_xtr = 0
                        appendage=""
                    file_name_xtr = fnamestring_xtr + appendage_xtr + ".xtr"
                    lastfnamestring_xtr = fnamestring_xtr
                        
                    fout_xtr = open(file_name_xtr, 'w')
                    outstring = ""
                    for i in np.arange(0,5):
                        if xtr_done[i] > 0:
                            print("Pulling trace: ",i)
                            xtrdata = pullxtr(mds_client,sn,statusfields,i,t1a,t1b)
                            outstring = outstring+xtrdata
                            #Keep checking for LM buffers so we don't lose any!  Note we might get an extra buffer
                            #or two tacked on to a LM file since we don't check for buffer_count = num_buffers to
                            #close the lm file while we are in the throes of getting traces
                            status = process_lm(mds_client,sn,fout)
                            buffer_count += status

                    #Clear trace flags (we hope), write output
                    mds_client.send_and_receive(json.dumps(cmd_clr_xtr).encode('utf-8')).decode('utf-8')
                    fout_xtr.write(outstring)
                    fout_xtr.close()

            if buffer_count >= num_buffers:
                fout.close()
                #mv the file just closed to its permanent name
                subprocess.call(['mv',file_name,file_name_after_closing])


                
                    
 
