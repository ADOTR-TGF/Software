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
    We assume that only one SiPM-Morpho is attached, and that the mca3k_server is running.

    :param dwell_time: Acquisition time in seconds
    :param file_name: Write the histogram to this file as one long line
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
    sn = sn_list[0]  # We just serve one mca3k here
    
    # Enforce some gain and integration time settings, 
    # and prepare new histogram acquisition

    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn, 
           "data": {"fields": {"gain_select": 2, "rtlt": 2, "daq_mode": 1}, 
           "user": {"integration_time": 1.2e-6, "hold_off_time": 1.5e-6, "digital_gain": 4800, 
                    "pulse_threshold": 0.010, "run_time": dwell_time}}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    
    time.sleep(1)  # Wait for operating voltage to ramp up and stabilize
    
    # Start new histogram acquisition
    cmd = {"type": "mca_cmd", "name": "fpga_action",  "dir": "rmw", "sn": sn, 
           "data": {"fields": {"clear_histogram": 1, "clear_statistics": 1, "histo_run": 1}}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    time.sleep(10)  # wait

    # Read count rate data
    cmd = {"type": "mca_cmd", "name": "fpga_statistics", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    count_rates = ret[sn]["user"]["bank_0"]
    #count_rates_reg = ret[sn]["registers"]
    
    # Read histogram data
    cmd = {"type": "mca_cmd", "name": "fpga_histogram", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    histogram = ret[sn]['registers']
    
    with open(file_name, 'w') as fout:
        out_dict = {"count_rates": count_rates, "histogram": histogram}
        fout.write(json.dumps(out_dict) + "\n")
        

def acquire_one_histogram_2(dwell_time, file_name):
    """
    We assume that only one SiPM-Morpho is attached, and that the SiPM-Morpho_server is running.
    Program FPGA control registers to stop counting events when the histogram has finished,
    and set the acquisition time to be dwell time.  Then check the SiPM-Morpho if the histogram
    acquisition has finished.  When that is the case, read histogram and count rates and store as one json object in file.

    :param dwell_time: Acquisition time in seconds
    :param file_name: Write the histogram to this file as one long line
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
    sn = sn_list[0]  # We just serve one mca3k here
    
    # Enforce some gain and integration time settings, 
    # and prepare new histogram acquisition

    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn, 
           "data": {"fields": {"gain_select": 2, "rtlt": 2, "daq_mode": 1}, 
           "user": {"integration_time": 1.2e-6, "hold_off_time": 1.5e-6, "digital_gain": 4800, 
                    "pulse_threshold": 0.010, "run_time": dwell_time}}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    
    time.sleep(1)  # Wait for operating voltage to ramp up and stabilize
    
    # Start new histogram acquisition
    cmd = {"type": "mca_cmd", "name": "fpga_action",  "dir": "rmw", "sn": sn, 
           "data": {"fields": {"clear_histogram": 1, "clear_statistics": 1, "histo_run": 1}}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    while True:  # Poll until histogram acquisition has finished
        time.sleep(1)  # wait 1s between polls
        cmd = {"type": "mca_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)  # ret is a dictionary with keys "registers", "fields", "user"
        if ret[sn]["user"]["histo_done"] == 1:
            break

    # Read histogram data
    cmd = {"type": "mca_cmd", "name": "fpga_histogram", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    histogram = ret[sn]['registers']

    # Read count rate data
    cmd = {"type": "mca_cmd", "name": "fpga_statistics", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    count_rates = ret[sn]["user"]["bank_0"]
    # count_rates_reg = ret[sn]["registers"]
    
    with open(file_name, 'w') as fout:
        out_dict = {"count_rates": count_rates, "histogram": histogram}
        fout.write(json.dumps(out_dict) + "\n")

#acquire_one_histogram(dwell_time=0, file_name="./data/one_histo.dat")

acquire_one_histogram_2(dwell_time=10, file_name="./data/rates_histo.dat")

