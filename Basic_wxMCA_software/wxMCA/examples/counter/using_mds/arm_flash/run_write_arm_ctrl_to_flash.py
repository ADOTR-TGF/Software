import json
import time
import zmq
import communication as com


def write_arm_ctrl_to_flash(file_name):
    """
    We assume that only one PMT-MCA is attached, and that the MCA Data Server is running.
    Program the arm_ctrl structure in the PMT-MCA to set the high voltage and gain-stabilization mode,
    and then write it to non-volatile memory ("memory": "flash")

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

    # Program the three most used members of the arm_ctrl structure;
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn, "memory": "flash",
           "data": {"fields": {"cal_ov": 31.1, "gain_stabilization": 0, "temp_ctrl": 1}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    # Read back and store
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    arm_ctrl = ret[sn]["fields"]
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(arm_ctrl) + ",\n")


write_arm_ctrl_to_flash(file_name="./data/arm_ctrl.json")
