import json
import time
import zmq
import communication as com


def acquire_list_mode(lm_mode, num_buffers, file_name):
    """
    We assume that only one SiPM-Morpho is attached, and that the mca3k_server is running.
    Program FPGA control registers to set the list_mode acquisition mode.  Then check the SiPM-Morpho if the
    list_mode acquisition has finished.  When that is the case, read the data buffer
    and store as one json object in file.

    :param lm_mode: Type of list mode: 0 or 1, cf MDS documentation
    :param num_buffers: Number of traces to be acquired
    :param file_name: Write the histogram to this file as one long line
    :return:
    """

    mds_ip = "tcp://127.0.0.1:5507"
    mds_client = com.zmq_device(mds_ip, "client")

    cmd = {"type": "server_cmd", "name": "hello"}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    sn_list = ret['sn_list']
    for sn in sn_list:
        print("Unique serial number:", sn)
    sn = sn_list[0]  # We only use one attached device here

    # Program FPGA controls to set the list-mode acquisition mode;
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"lm_mode": lm_mode, "short_it": 24}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    with open(file_name, 'w') as fout:
        pass
    for buffer_num in range(num_buffers):
        # Start the list-mode run
        cmd = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
               "data": {"fields": {"clear_statistics": 1, "clear_list_mode": 1, "lm_run": 1}}}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)

        while True:  # Poll until list-mode acquisition has finished
            cmd = {"type": "mca_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
            msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
            ret = json.loads(msg)  # ret is a dictionary with keys "registers", "fields", "user"
            if ret[sn]["user"]["lm_done"] == 1:
                break

        # Read list-mode data
        cmd = {"type": "mca_cmd", "name": "fpga_list_mode", "dir": "read", "sn": sn}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        lm_data = ret[sn]['user']
        with open(file_name, 'a') as fout:
            fout.write(json.dumps(lm_data) + "\n")
            
    print("Output data file:", file_name)

lm_mode = 0
acquire_list_mode(lm_mode, num_buffers=1, file_name="./data/list_mode_{}.dat".format(lm_mode))

lm_mode = 1
acquire_list_mode(lm_mode, num_buffers=1, file_name="./data/list_mode_{}.dat".format(lm_mode))
