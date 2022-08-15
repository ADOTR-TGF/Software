import json
import time
import zmq
import communication as com


def read_fpga_results(file_name):
    """
    We assume that only one SiPM-Morpho is attached, and that the mca3k_server is running.
    Read control registers or statistics first, then read results.

    :param file_name: Write the resulting fpga_ctrl data to this file
    :return:
    """

    mds_ip = "tcp://127.0.0.1:5507"
    mds_client = com.zmq_device(mds_ip, "client")

    cmd = {"type": "server_cmd", "name": "hello"}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    sn_list = ret['sn_list']
    for sn in sn_list:
        print("Serial number:", sn)
    sn = sn_list[0]  # We only use one attached device here
    
    if 0:
        # Clear statistics
        cmd = {"type": "mca_cmd", "name": "fpga_action",  "dir": "rmw", "sn": sn, 
               "data": {"fields": {"histo_run": 1, "clear_statistics": 1, "clear_histogram": 1}, 
               "user":{}}}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

        # Read statistics
        cmd = {"type": "mca_cmd", "name": "fpga_statistics", "dir": "read", "sn": sn}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        print(ret[sn]["registers"])
        
        cmd = {"type": "mca_cmd", "name": "fpga_statistics", "dir": "read", "sn": sn}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        print(ret[sn]["registers"])

        cmd = {"type": "mca_cmd", "name": "fpga_statistics", "dir": "read", "sn": sn}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        print(ret[sn]["registers"])
    
    # Read controls multiple times
    ctrl = [11200, 3, 5, 72, 60, 12832, 100, 1092, 0, 0, 32, 0, 580, 0, 33008, 32772, 31200, 3, 5, 72, 60, 12832, 100, 1092, 0, 0, 32, 0, 580, 0, 33008, 32772]
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "write", "sn": sn, "data": {"registers": ctrl}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    print(ret[sn]["registers"])
    
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    print(ret[sn]["registers"])

    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    print(ret[sn]["registers"])

    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    print(ret[sn]["registers"])


    # Read results multiple times and store
    cmd = {"type": "mca_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    print(ret[sn]["fields"])
    
    cmd = {"type": "mca_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    print(ret[sn]["fields"])
    
    cmd = {"type": "mca_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    print(ret[sn]["fields"])
    
    
    fpga_ctrl = ret[sn]["fields"]
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(fpga_ctrl) + ",\n")


read_fpga_results(file_name="./data/fpga_results.json")
