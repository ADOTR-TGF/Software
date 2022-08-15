#!/usr/bin/python
#
from __future__ import division
import time
import math
import json
import time
import communication as com

version = 1.0

"""
    This example file is for non-standard firmware, where two GPIO inputs are being used
    as external trigger inputs to indicate the source of the signal.
    The MCA runs in acquisition mode 5 and produces 4 512-bin spectra: 
    0-> Coincidence (b11), 1->Ungated (bxx), 2->Singles_1 (b1x), 3->Singles_2 (bx1)
"""


def acquire_one_histogram(dwell_time, file_name):
    """
    We assume that only one MCA is attached, and that the MCA Data Server is running.

    :param dwell_time: Acquisition time in seconds
    :param file_name: Write the histogram to this file as a 4-line json file
    :return: None
    """
    # 127.0.0.1 is the same as localhost
    mds_client = com.zmq_device("tcp://127.0.0.1:5507", "client")  # Communicate with MDS
    
    # get serial number
    cmd = {"type": "server_cmd", "name": "hello"}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    sn_list = ret["sn_list"]
    for sn in sn_list:
        print("Unique serial number:", sn)
    sn = sn_list[0]  # We just serve one device here
    
    # Start new sample histogram acquisition
    cmd = {"type": "mca_cmd", "name": "arm_ctrl",  "dir": "rmw", "sn": sn, 
           "data": {"fields": {"run_time_sample": dwell_time}, 
           "user":{"histogram_run": 1, "acq_type": 5, "clear_statistics": 1, "clear_histogram": 1}}}
    #msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    #time.sleep(dwell_time+1)  # wait

    # Read count rate and histogram data for all 4 histograms
    # And write to file, using one json string per histogram; ie we write 4 lines to file.
    for ch in range(4):
        cmd = {"type": "mca_cmd", "name": "arm_histogram", "ctrl":[ch], "num_items": 528, "dir": "read", "sn": sn}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        mca_data = ret[sn]["fields"]
        
        with open(file_name, 'a') as fout:
            fout.write(json.dumps(mca_data) + "\n")
        

acquire_one_histogram(dwell_time=300, file_name="./data/coinc_bck_histo.dat")

