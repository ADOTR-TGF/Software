#!/usr/bin/python
#
import time
import math
import json
import time
import communication as com

version = 1.0


def acquire_listmode(num_buffers, file_name, wait, clear_lm_time):
    """
    We assume that only one PMT2K-MCA is attached, and that the MCA Data Server is running.
    This functions acquires list mode data.  It regularly switches between the two buffers,
    and does not wait for either buffer to fill up.
    Note that clear_lmtime is used to clear the wall clock of the list mode module.
    

    :param num_buffers: Number of pulses to acquire
    :param file_name: Write the pulses to this file as a one-line json strings
    :param wait: wait x seconds before switching to the next buffer
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
    
    # We need these commands
    cmd_start = {"type": "mca_cmd", "name": "arm_ctrl",  "dir": "rmw", "sn": sn, 
                 "data": {"fields": {}, "user":{"clear_listmode": 1, "clear_lmtime": 0}}}
    cmd_read = {"type": "mca_cmd", "name": "arm_listmode",  "dir": "read", "sn": sn }
    cmd_status = {"type": "mca_cmd", "name": "arm_status",  "dir": "read", "sn": sn }
    
    active_buffer = 0
    then = time.time()
    cmd_start["data"]["user"]["lm_buffer"] = active_buffer
    cmd_start["data"]["user"]["clear_lmtime"] = clear_lm_time            
    
    for num_buffer in range(num_buffers+1):
        cmd_start["data"]["user"]["lm_buffer"] = active_buffer
        msg = mds_client.send_and_receive(json.dumps(cmd_start).encode('utf-8')).decode('utf-8') # Switches buffer and clears the newly active buffer
        active_buffer = active_buffer ^ 1  # Toggle buffer 
        
        if num_buffer > 0:            
            msg = mds_client.send_and_receive(json.dumps(cmd_read).encode('utf-8')).decode('utf-8')
            print(time.time()-then)
            
            ret = json.loads(msg)
            listmode_data = ret[sn]["fields"]
            
            with open(file_name, 'a') as fout:
                fout.write(json.dumps(listmode_data) + "\n")
                
        time.sleep(wait)    
        
       
num_buffers = 10
file_name="./data/lm2b.dat"
wait = 1
clear_lm_time = 1
acquire_listmode(num_buffers, file_name, wait, clear_lm_time)
