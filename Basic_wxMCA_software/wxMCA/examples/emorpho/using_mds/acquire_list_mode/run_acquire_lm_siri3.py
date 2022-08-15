import json
import time
import zmq
import communication as com


def acquire_list_mode(lm_mode, num_buffers, file_name):
    """
    We assume that only one eMorpho is attached, and that the MCA Data Server is running.
    Program FPGA control registers to set the list_mode acquisition mode.  Then check the eMorpho if the
    list_mode acquisition has finished.  When that is the case, read the data buffer
    and store as one json object in file.

    :param lm_mode: Type of list mode: 0 or 1, cf MDS documentation
    :param num_buffers: Number of traces to be acquired
    :param file_name: Write the listmode data to this file , one json string per line.
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
           "data": {"fields": {"lm_mode": lm_mode}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    with open(file_name, 'w') as fout:
        pass
    
    # Start the list-mode run
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"clear_statistics": 1, "clear_list_mode": 1, "lm_run": 1, "run": 1}}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    
    sel_buf = 0
    switch_buffer = 1
    for buffer_num in range(num_buffers):

        time.sleep(0.10)
        
        cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
               "data": {"fields": {"gain_stab": sel_buf, "cr15_b8": switch_buffer}}}
        mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        
        sel_buf = 1 if sel_buf==0 else 0

        cmd = {"type": "mca_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)  # ret is a dictionary with keys "registers", "fields", "user"
        results = ret[sn]["registers"]

        # Read list-mode data
        cmd = {"type": "mca_cmd", "name": "fpga_lm_2b", "dir": "read", "sn": sn}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        lm_data = {"results": "{:X}".format(int(results[2])&0x1A), "lm_data": ret[sn]['registers']}
        with open(file_name, 'a') as fout:
            fout.write(json.dumps(lm_data) + "\n")
            
    print("Output data file:", file_name)

acquire_list_mode(lm_mode=0, num_buffers=3, file_name="./data/list_mode_2b.dat")

