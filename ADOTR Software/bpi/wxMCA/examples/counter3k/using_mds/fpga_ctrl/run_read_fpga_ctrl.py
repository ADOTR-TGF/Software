import json
import time
import zmq
import communication as com


def read_fpga_ctrl(file_name):
    """
    We assume that only one SiPM-Morpho is attached, and that the mca3k_server is running.
    Read the fpga_ctrl structure in the SiPM-Morpho to set the high voltage and gain-stabilization mode

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

    if 1:
        print("Action")
        cmd = {"type": "mca_cmd", "name": "fpga_action",  "dir": "read", "sn": sn,
           "data": {"fields": {"histo_run": 1, "clear_statistics": 1, "clear_histogram": 1}, "user":{}}}
        mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    # Read controls and store
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    fpga_ctrl = ret[sn]
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(fpga_ctrl) + ",\n")


read_fpga_ctrl(file_name="./data/fpga_ctrl.json")
