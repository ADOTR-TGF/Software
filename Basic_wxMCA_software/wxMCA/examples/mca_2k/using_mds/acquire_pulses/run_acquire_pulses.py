#!/usr/bin/python
#
from __future__ import division
import time
import math
import json
import time
import communication as com

version = 1.0


def acquire_pulses(num_pulses, num_samples, file_name, wait):
    """
    We assume that only one PMT2K-MCA is attached, and that the MCA Data Server is running.
    

    :param num_pulses: Number of pulses to acquire
    :param num_samples: Number of ADC samples per pulse 
    :param file_name: Write the pulses to this file as a one-line json strings
    :param wait: >=0 => wait x seconds between start and read; <0 check until trace_done=1
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
    
    # We need these three commands
    cmd_start = {"type": "mca_cmd", "name": "arm_ctrl",  "dir": "rmw", "sn": sn, 
                 "data": {"fields": {}, "user":{"trace": 1, "clear_trace": 1}}}
    cmd_read = {"type": "mca_cmd", "name": "arm_trace",  "dir": "read", "num_items": num_samples, "sn": sn }
    cmd_check = {"type": "mca_cmd", "name": "arm_status",  "dir": "read", "sn": sn }
    
    for num_pulse in range(num_pulses):
        msg = send_and_receive(mds_client, cmd_start) #mds_client.send_and_receive(json.dumps(cmd_start).encode('utf-8')).decode('utf-8')
        
        if wait >= 0:
            time.sleep(wait)
        else:
            while True:
                msg = mds_client.send_and_receive(json.dumps(cmd_check).encode('utf-8')).decode('utf-8')
                ret = json.loads(msg)
                trace_done = ret[sn]["user"]["trace_done"]
                print(ret[sn]["fields"]["run_status"], trace_done)
                if trace_done:
                    break;
                
        msg = mds_client.send_and_receive(json.dumps(cmd_read).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        pulse = ret[sn]["registers"]
    
        with open(file_name, 'a') as fout:
            fout.write(json.dumps(pulse) + "\n")
        
def send_and_receive(client, cmd):
    return client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

num_pulses = 10
num_samples = 256
file_name="./data/nai_pulses.txt"
acquire_pulses(num_pulses, num_samples, file_name, wait=-1)
