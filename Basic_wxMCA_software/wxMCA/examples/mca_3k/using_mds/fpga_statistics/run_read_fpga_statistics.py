import json
import time
import zmq
import communication as com


def read_fpga_statistics(file_name):
    """
    We assume that only one MCA-3K is attached, and that the mca3k_server is running.
    Read the fpga_ctrl structure in the MCA-3K to set the high voltage and gain-stabilization mode

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
    
    # Clear statistics
    cmd = {"type": "mca_cmd", "name": "fpga_action",  "dir": "rmw", "sn": sn, 
           "data": {"fields": {"histo_run": 1, "clear_statistics": 1, "clear_histogram": 1}, 
           "user":{}}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    time.sleep(1.0)

    # Read statistics multiple times and store
    cmd = {"type": "mca_cmd", "name": "fpga_statistics", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    print(ret[sn]["fields"])
    time.sleep(1.0)
    
    cmd = {"type": "mca_cmd", "name": "fpga_statistics", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    print(ret[sn]["fields"])
    
    
    
    fpga_statistics = ret[sn]
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(fpga_statistics) + "\n")


read_fpga_statistics(file_name="./data/fpga_statistics.json")
