import json
import time
import zmq
import communication as com


def acquire_coincidence_list_mode(lm_mode, num_buffers, file_name):
    """
    This example shows list mode acquisition for the case where an external logic,
    implemented in the FPGA of a Counter-3K, controls the list mode data acquisition.
    In this example, the logic simply enforces a two-MCA coincidence from two
    MCA-3K trigger signals.

    Note that this requires non-standard MCA-3K firmware.

    Each of the two MCA-3K has been programmed to have modified GPIO signals on
    its 8-pin GPIO connector:
    Pin 1: Trigger output => to the coincidence logic
    Pin 2: Veto input <= from the coincidence logic
    Pin 3: Clear list mode input  <= Daisy chain input
    Pin 4: Clear list mode output => Daisy chain output

    Pins 3 and 4 are part of a daisy chain.  The user sends a clear_listmode
    command to the first MCA-3K.  It creates a pulse on Pin 4 which is sent
    to Pin 3 of the second MCA-3K.  On receipt of a clear_list_mode input,
    the MCA-3K will also reset its time and events counter via an internal
    clear_statistics command.

    When a list mode run has stopped, the user only needs to send a command via
    USB to the first MCA-3K and both will start the list mode run at the same
    time (within two clock cyles).

    The veto input is common to both MCA and the list mode buffers will fill in
    lockstep and and finish with the same event.

    We assume that two MCA-3K are attached, and that the MCA Data Server is running.
    Program FPGA control registers to prepare the MCA-3K.  Then check either
    MCA-3K if the list_mode acquisition has finished.  When that is the case,
    read both data buffers and store as one json object in file.

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
    """
    If the Counter3K with its coincidence logic is USB connected, it needs to
    be removed from the mca_list
    The first MCA-3K in the list is expected to be at the beginning of the daisy chain.
    """
    cmd = {"type": "server_cmd", "name": "identify"}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    identities = json.loads(msg)['mca_id']  # List of {sn: mca_id_str} dictionaries

    mca_list = []
    for identity in identities:
        sn = list(identity)[0]
        if identity[sn] in ["0x103", "0x203"]:
            mca_list += [sn]
    mca_list = sorted(mca_list)
    print(mca_list)
    sn_0 = mca_list[0]

    # Program FPGA controls to set the list-mode acquisition mode;
    for sn in mca_list:
        cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
               "data": {"fields": {"cr15_upper":1, "lm_mode": lm_mode}}}
        mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        
        cmd = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
               "data": {"fields": {"lm_run": 1}}}
        mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    with open(file_name, 'w') as fout:  # Delete old data
        pass
        
    then = time.time()
    for buffer_num in range(num_buffers):
        # Start the list-mode run in both MCA-3K
        cmd = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn_0,
               "data": {"fields": {"clear_statistics": 1, "clear_list_mode": 1}}}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)

        while True:  # Poll until list-mode acquisition has finished
            cmd = {"type": "mca_cmd", "name": "fpga_results", "dir": "read", "sn": sn_0}           
            msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
            ret = json.loads(msg)  # ret is a dictionary with keys "registers", "fields", "user"
            if ret[sn_0]["user"]["lm_done"] == 1:
                break
 
        # Read list-mode data from both MCA into a single json object
        with open(file_name, 'a') as fout:
            lm_data_dict = {}
            for sn in mca_list:
                cmd = {"type": "mca_cmd", "name": "fpga_list_mode", "dir": "read", "sn": sn}
                msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
                ret = json.loads(msg)
                lm_data_dict[sn] = ret[sn]['user']
            fout.write(json.dumps(lm_data_dict) + "\n")
        print("Buffer completed {}, {:.2f}s".format(buffer_num, time.time()-then))
        then = time.time()

    print("Output data file:", file_name)

lm_mode = 0
acquire_coincidence_list_mode(
    lm_mode, num_buffers=10,
    #file_name="./data/coinc_list_mode_{}.dat".format(lm_mode))
    file_name="./data/coinc_lm.dat")
