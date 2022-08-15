import json
import time
import zmq
import communication as com


def read_arm_ctrl_from_nvmem(file_name):
    """
    We assume that only one SiPM-Morpho is attached, and that the mca3k_server is running.
    Read the arm_ctrl structure in the SiPM-Morpho to set the high voltage and gain-stabilization mode

    :param file_name: Write the resulting arm_ctrl data to this file
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


    # Read controls and store
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "read", "memory": "flash", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    arm_ctrl = json.loads(msg)[sn]
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(arm_ctrl) + "\n")


read_arm_ctrl_from_nvmem(file_name="./data/arm_ctrl.json")
