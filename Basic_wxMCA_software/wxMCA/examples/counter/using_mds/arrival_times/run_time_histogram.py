#!/usr/bin/python
#
from __future__ import division
import time
import math
import json
import time
import communication as com

version = 1.0


def acquire_one_histogram(dwell_time, file_name):
    """
    We assume that only one SiPM-Counter is attached, and that the mca data server is running.

    :param dwell_time: Acquisition time in seconds
    :param file_name: Write the histogram to this file as a on-line json file
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
           "data": {"fields": {"run_time_sample": 0}, 
           "user":{"histogram_run": 1, "active_bank": 0, "clear_statistics": 1, "clear_histogram": 1, "acq_type": 1}}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    time.sleep(dwell_time+1)  # wait

    # Read count rate and histogram data
    cmd = {"type": "mca_cmd", "name": "arm_histogram", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    mca_data = ret[sn]
    
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(mca_data) + "\n")
        

acquire_one_histogram(dwell_time=90, file_name="./data/arrival_times.json")

