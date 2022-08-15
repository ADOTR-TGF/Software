#!/usr/bin/python
#
from __future__ import division
import time
import math
import json
import time
import communication as com

version = 1.0


def acquire_histograms(dwell_time, num_histos, file_name):
    """
    We assume that only one MCA-1000 is attached, and that the MCA Data Server is running.

    :param dwell_time: Acquisition time in seconds
    :param num_histos: Number of histograms to acquire and write to file
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
    start_mca_cmd = {"type": "mca_cmd", "name": "arm_ctrl",  "dir": "rmw", "sn": sn, 
               "data": {"fields": {"run_time_sample": dwell_time}, 
               "user":{"histogram_run": 1, "active_bank": 0, "clear_statistics": 1, "clear_histogram": 1}}}
    read_histogram_cmd = {"type": "mca_cmd", "name": "arm_histogram", "dir": "read", "sn": sn}
    read_status_cmd = {"type": "mca_cmd", "name": "arm_status", "dir": "read", "sn": sn}
    
    # Delete a pre-existing file
    with open(file_name, 'w') as fout:
        pass
        
    for n in range(num_histos):
        # Start new sample histogram acquisition        
        msg = mds_client.send_and_receive(json.dumps(start_mca_cmd).encode('utf-8')).decode('utf-8')

        time.sleep(dwell_time+1)  # wait

        # Read count rate and histogram data
        msg = mds_client.send_and_receive(json.dumps(read_status_cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        status_data = ret[sn]["fields"]
        
        msg = mds_client.send_and_receive(json.dumps(read_histogram_cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        mca_data = ret[sn]["fields"]
                
        out_dict = {"histogram": mca_data, "status": status_data}
        with open(file_name, 'a') as fout:
            fout.write(json.dumps(out_dict) + "\n")
            
def read_and_clear_histograms(dwell_time, num_histos, file_name):
    """
    We assume that only one MCA-1000 is attached, and that the MCA Data Server is running.

    :param dwell_time: Acquisition time in seconds
    :param num_histos: Number of histograms to acquire and write to file
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
    start_mca_cmd = {"type": "mca_cmd", "name": "arm_ctrl",  "dir": "rmw", "sn": sn, 
        "data": {"user":{"histogram_run": 1, "active_bank": 0, "read_clear": 1, "acq_type": 0},
                 "fields": {"run_time_sample": 0}}}
        
    read_histogram_cmd = {"type": "mca_cmd", "name": "arm_histogram", "dir": "read", "sn": sn}
    read_status_cmd = {"type": "mca_cmd", "name": "arm_status", "dir": "read", "sn": sn}
    
    # Delete a pre-existing file
    with open(file_name, 'w') as fout:
        pass
    
    # Start new sample histogram acquisition
    msg = mds_client.send_and_receive(json.dumps(start_mca_cmd).encode('utf-8')).decode('utf-8')    
    for n in range(num_histos):
        time.sleep(dwell_time+1)  # wait

        # Read count rate and histogram data
        msg = mds_client.send_and_receive(json.dumps(read_status_cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        status_data = ret[sn]["fields"]
        
        msg = mds_client.send_and_receive(json.dumps(read_histogram_cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        mca_data = ret[sn]["fields"]
                
        out_dict = {"histogram": mca_data, "status": status_data}
        with open(file_name, 'a') as fout:
            fout.write(json.dumps(out_dict) + "\n")
        

# acquire_histograms(dwell_time=1, num_histos=10, file_name="./data/histo_sipm1k_294.json")

read_and_clear_histograms(dwell_time=1, num_histos=10, file_name="./data/histo_sipm1k_294.json")

