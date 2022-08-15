import json
import time
import zmq
import communication as com


def read_arm_ctrl(file_name):
    """
    We assume that only one device is attached, and that the pmt_mc_server is running.
    Read the current status data from the ARM processor.

    :param file_name: Write the arm status data to this file.
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

    # Read arm_status
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    arm_ctrl = ret[sn]
    
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(arm_ctrl) + ",\n")


read_arm_ctrl(file_name="./data/arm_ctrl.json")
