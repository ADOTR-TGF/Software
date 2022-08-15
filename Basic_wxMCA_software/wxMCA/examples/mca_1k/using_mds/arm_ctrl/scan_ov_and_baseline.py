import json
import time
import zmq
import communication as com


def write_arm_ctrl(file_name):
    """
    We assume that only one MCA-1000 is attached, and that the MCA Data Server is running.
    Program the arm_ctrl structure in the MCA-1000 to set the high voltage and gain-stabilization mode

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

    n_max = 4
    ov_max = 36.0
    ov_min = 34.0
    dov = (ov_max - ov_min)/n_max
    
    with open(file_name, 'w') as fout:
        pass
    
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
       "data": {"fields": {"cal_ov": ov_min, "gain_stabilization": 0, "temp_ctrl": 1}}}
    #mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    #time.sleep(40)
    
    for n in range(n_max+1):
        # Set new operating voltage
        ov = ov_min + n*dov
        cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"cal_ov": ov, "gain_stabilization": 0, "temp_ctrl": 1}}}
        mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        time.sleep(10)

        cmd = {"type": "mca_cmd", "name": "arm_status", "dir": "read", "sn": sn}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        reg = ret[sn]["registers"]
        results = {"ov": reg[0], "g_thr": reg[61], "thr": reg[62], "base": reg[63]}
        with open(file_name, 'a') as fout:
            fout.write(json.dumps(results) + "\n")
       

write_arm_ctrl(file_name="./data/baseline_scan.json")
