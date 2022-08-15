#!/usr/bin/python
#
from __future__ import division
import time
import math
import json
import time
import communication as com

version = 1.0


def log_histograms(dwell_time, file_name):
    """
    We assume that only one MCA-3K is attached, and that the mca3k_server is running.
    We assume that the detector has been calibrated and that the following arm_ctrl fields have been set: cal_ov, cal_dg, cal_temp, cal_target.
    In this example, the gain stabilization is performed with an LED and we use the default look up tables programmed into the device.

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
        print("MCA-3K unique serial number:", sn)
    sn = sn_list[0]  # We just serve one mca3k here
    
    
    # Prepare ongoing histogram acquisition

    prepare_mca_cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn, 
           "data": {"fields": {"rtlt": 2, "daq_mode": 1}, 
           "user": {"run_time": dwell_time}}}
    msg = mds_client.send_and_receive(json.dumps(prepare_mca_cmd).encode('utf-8')).decode('utf-8')
    
    time.sleep(1)  # Wait for operating voltage to ramp up and stabilize
    
    # Start new histogram acquisition
    start_mca_cmd = {"type": "mca_cmd", "name": "fpga_action",  "dir": "rmw", "sn": sn, 
           "data": {"fields": {"clear_histogram": 1, "clear_statistics": 1, "histo_run": 1}}}

    arm_status_cmd = {"type": "mca_cmd", "name": "arm_status", "dir": "read", "sn": sn}
    fpga_stats_cmd = {"type": "mca_cmd", "name": "fpga_statistics", "dir": "read", "sn": sn}
    start = time.time()
    while True:
        # Start new histogram acquisition
        mds_client.send_and_receive(json.dumps(start_mca_cmd).encode('utf-8')).decode('utf-8')
        time.sleep(dwell_time)

        # Read ARM status data
        
        msg = mds_client.send_and_receive(json.dumps(arm_status_cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        arm_status = ret[sn]["fields"]
        
        # Read count rate data
        
        msg = mds_client.send_and_receive(json.dumps(fpga_stats_cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        count_rates = ret[sn]["registers"]
        
        if False:   
            # Read histogram data
            cmd = {"type": "mca_cmd", "name": "fpga_histogram", "dir": "read", "sn": sn}
            msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
            ret = json.loads(msg)
            histogram = ret[sn]['registers']
        
            with open(file_name, 'a') as fout:
                out_dict = {"time": time.time(), "status": arm_status, "count_rates": count_rates, "histogram": histogram}
                fout.write(json.dumps(out_dict) + "\n")
         
        with open(file_name, 'a') as fout:
            out_dict = {"time": time.time()-start, "status": arm_status, "count_rates": count_rates }
            fout.write(json.dumps(out_dict) + "\n")
        
log_histograms(dwell_time=2, file_name="./data/log_histo.dat")

