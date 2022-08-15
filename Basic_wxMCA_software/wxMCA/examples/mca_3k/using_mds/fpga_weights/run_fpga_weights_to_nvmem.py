import json
import time
import zmq
import communication as com


def fpga_weights_to_nvmem(file_name):
    """
    We assume that only one MCA-3000 is attached, and that the MCA Data Server is running.
    Write a new set of fpga_weights to the MCA-3000 FPGA and its non-volatile flash memory

    :param file_name: Write the resulting fpga_ctrl data to this file
    :return:
    """
    # make the weights; The length of the weights list should be multiples of 32, up 1024 weights.
    weights = [65535]*1024
    weights += [0]*(1024-len(weights))
    
    mds_ip = "tcp://127.0.0.1:5507"
    mds_client = com.zmq_device(mds_ip, "client")

    cmd = {"type": "server_cmd", "name": "hello"}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    sn_list = ret['sn_list']
    for sn in sn_list:
        print("Serial number:", sn)
    sn = sn_list[0]  # We only use one attached device here
    
    # Write the new weights to flash memory (memory: flash)
    cmd = {"type": "mca_cmd", "name": "fpga_weights", "dir": "write", "memory": "flash", "sn": sn,
           "data": {"registers": weights}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    

    # Read controls and store
    cmd = {"type": "mca_cmd", "name": "fpga_weights", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    fpga_weights = ret[sn]
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(fpga_weights) + ",\n")


fpga_weights_to_nvmem(file_name="./data/fpga_weights.json")
