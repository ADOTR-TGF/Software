import json
import time
import zmq
import communication as com


def read_arm_version(file_name):
    """
    We assume that only one SiPM-Morpho is attached, and that the mca3k_server is running.
    Read the arm_version registers.

    :param file_name: Write the arm version registers to this file.
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

    # Read arm_version
    cmd = {"type": "mca_cmd", "name": "arm_version", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    arm_version = ret[sn]
    
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(arm_version) + ",\n")


read_arm_version(file_name="./data/arm_version.json")
