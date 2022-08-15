import json
import time
import zmq
import communication as com


def write_fpga_weights(file_name):
    """
    We assume that only one MCA-3000 is attached, and that the MCA Data Server is running.
    Write a new set of fpga_weights to the MCA-3000

    :param file_name: Write the resulting fpga_ctrl data to this file
    :return:
    """
    weights = [0]*1024
    #weights[8:19] = [0xA000]*11
    #weights[21:36] = [32000]*15
    weights[6: 18] = [0x9000]*12
    weights[23: 38] = [30000]*15
    
    mds_ip = "tcp://127.0.0.1:5507"
    mds_client = com.zmq_device(mds_ip, "client")

    cmd = {"type": "server_cmd", "name": "hello"}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    sn_list = ret['sn_list']
    for sn in sn_list:
        print("Serial number:", sn)
    sn = sn_list[0]  # We only use one attached device here
    
    if 1:
        print("Action")
        cmd = {"type": "mca_cmd", "name": "fpga_action",  "dir": "rmw", "sn": sn,
           "data": {"fields": {"histo_run": 1, "clear_statistics": 1, "clear_histogram": 1}, "user":{}}}
        mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')


    # Write the new weights
    cmd = {"type": "mca_cmd", "name": "fpga_weights", "dir": "write", "sn": sn,
           "data": {"registers": weights}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    # Read controls and store
    cmd = {"type": "mca_cmd", "name": "fpga_weights", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    fpga_weights = ret[sn]
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(fpga_weights) + ",\n")


write_fpga_weights(file_name="./data/fpga_weights.json")
