import json
import time
import zmq
import communication as com


def write_psd_weights(file_name, mode):
    """
    We assume that only one MCA-2000 is attached, and that the MCA Data Server is running.
    Write a new set of fpga_weights to the MCA-2000

    :param file_name: Write the resulting fpga_ctrl data to this file
    :return:
    """
    if mode == "unity_weights":
        weights = [32767]*512
    else:
        weights = [0]*512
        with open(file_name, "r") as fin:
            wt = json.loads(fin.read())["registers"]
        
        for n in range(len(wt)):
            weights[n] = -wt[n]
        abs_max = max([abs(x) for x in weights])
        norm = 32767/abs_max
        weights = [int(w*norm) if w>=0 else 65536+int(w*norm) for w in weights]
    #print(weights)
    
    mds_ip = "tcp://127.0.0.1:5507"
    mds_client = com.zmq_device(mds_ip, "client")

    cmd = {"type": "server_cmd", "name": "hello"}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    sn_list = ret['sn_list']
    for sn in sn_list:
        print("Serial number:", sn)
    sn = sn_list[0]  # We only use one attached device here
    
    # Write the new weights
    cmd = {"type": "mca_cmd", "name": "arm_weights", "dir": "write", "memory": "flash", "sn": sn, "num_items": 512,
           "data": {"registers": weights}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')



write_psd_weights(file_name="./data/nai_pvt_weights.json", mode="unity_weights")
