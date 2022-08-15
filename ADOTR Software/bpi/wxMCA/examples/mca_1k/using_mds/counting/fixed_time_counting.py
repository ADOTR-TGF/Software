import json
import time
import communication as com


def count_and_read(file_name):
    """
    We assume that only one device is attached, and that the device_server is running.
    Program the arm_ctrl structure in the device to count for 10 seconds, then read the result.

    :param file_name: Write the arm_status data to this file after the read back.
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

    # Set the parameters for sample counting
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"run_mode": 1, "run_action": 1, "run_time_sample": 10.0}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    
    time.sleep(10)

    # Read back data and store
    # In arm_status.json look for the fields "run_time", "count_rate", and "count_rate_err".
    cmd = {"type": "mca_cmd", "name": "arm_status", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    arm_status = ret[sn]
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(arm_status) + ",\n")


count_and_read(file_name="./data/arm_status.json")
