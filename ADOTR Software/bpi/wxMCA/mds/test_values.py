#!/usr/bin/python3.7

import json
import time
import zmq
import communication as com
import numpy as np

def test_values():
    #mds_ip = "tcp://127.0.0.1:5507"
    mds_ip = "tcp://0.0.0.0:5507"
    mds_client = com.zmq_device(mds_ip, "client")
    cmd = {"type": "server_cmd", "name": "hello"}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    sn_list = ret['sn_list']
    with open("/Detector1/bpi/wxMCA/mds/sn_list.txt",'r') as snfile:
        	snnames = snfile.read()
        	snfile.close()
    snnames = snnames.splitlines()
    sn_short = np.array([snnames[1],snnames[3]])

    for i in range(len(sn_list)):
        ssn = sn_short[i]
        # Read volatile memory
        cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "read", "sn": sn_list[i]}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        #hv1 = ret[sn]["fields"]["dac_data"]*3000.0/65536.0
        hv1 = ret[sn_list[i]]["fields"]["cal_ov"]

        # Read non-volatile memory
        cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "read", "memory": "flash", "sn": sn_list[i]}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        #hv2 = ret[sn]["fields"]["dac_data"]*3000.0/65536.0
        hv2 = ret[sn_list[i]]["fields"]["cal_ov"]

        print("%s   %8.1f    %8.1f " % (ssn,hv1,hv2))

test_values()


 
