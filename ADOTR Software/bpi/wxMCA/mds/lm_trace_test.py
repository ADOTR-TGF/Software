#!/usr/bin/python3.8
#
from __future__ import division

import numpy as np
import time
import json
import zmq
import communication as com

from datetime import datetime
import subprocess



def xml22_daq(num_buffers,sn,sn_short,detlabel,rootdir):


    #TRIGGERED TRACE (XTR) COMMANDS:
    cmd_clr_xtr = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
               "data": {"fields": {"clear_trace": 1, "run": 1}}}
    cmd_start_xtr = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
                 "data": {"fields": {"clear_statistics": 1, "clear_trace": 1, "trace_run": 1, "run": 1}}}
    cmd_tgf_status = {"type": "mca_cmd", "name": "fpga_tgf_results", "dir": "read", "sn": sn}

    mds_client = com.zmq_device("tcp://127.0.0.1:5507", "client")  # Communicate with MDS

    #Clear and start the triggered trace run
    mds_client.send_and_receive(json.dumps(cmd_clr_xtr).encode('utf-8')).decode('utf-8')
    mds_client.send_and_receive(json.dumps(cmd_start_xtr).encode('utf-8')).decode('utf-8')

    while True:
        ret_status = json.loads(mds_client.send_and_receive(json.dumps(cmd_tgf_status).encode('utf-8')).decode('utf-8'))
        statusfields =  ret_status[sn]['fields']
        xtr_done = np.array([ ret_status[sn]['user']['xt0_done'],
                                      ret_status[sn]['user']['xt1_done'],
                                      ret_status[sn]['user']['xt2_done'],
                                      ret_status[sn]['user']['xt3_done'],
                                      ret_status[sn]['user']['xt4_done']])
        print('Status of 5 traces: ',xtr_done)
 
        #Clear trace flags (we hope)
        mds_client.send_and_receive(json.dumps(cmd_clr_xtr).encode('utf-8')).decode('utf-8')

