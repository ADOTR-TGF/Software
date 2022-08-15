import json
import time
import zmq
import communication as com


def reset_fpga_ctrl(file_name):
    """
    We assume that only one SiPM-Morpho is attached, and that the mca3k_server is running.
    Read the factory default from internal memory.  The default automatically is stored in 
    non-volatile memory.  Note: "memory": "reset"

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


    # Read controls and store
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "read", "memory": "reset", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    fpga_ctrl = ret[sn]["fields"]
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(fpga_ctrl) + ",\n")


reset_fpga_ctrl(file_name="./data/fpga_ctrl.json")
