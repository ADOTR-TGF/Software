import json
import time
import zmq
import communication as com


def run_test(dwell_time, num_records, file_name):
    """
    We assume that only one SiPM-Morpho is attached, and that the MCA Data Server is running.
    
    This example demonstrates loss-less histogram acquisition using the built-in 
    split-histogram mode.  Statistics counters and histogram data appear in two
    equal-sized banks (2Kx32 for the histogram).  While the FPGA on the eMorpho
    is acquiring data into one bank, the client can read and then clear the inactive
    bank at leisure.
    
    The data file will consist one json string per line.

    :param dwell_time: Acquisition time in seconds before switching to the other bank
    :param num_records: Maximum number of records to write to file.
    :param file_name: Write the histogram to this file as one long line
    :return: None
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
    
    # Prepare histogram run without preprogrammed end (run_time = 0)
    cmd = {"type": "sm_cmd", "name": "fpga_ctrl", "dir": "read", "sn": sn}
    
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8'))
    ret = json.loads(msg)
    print(ret[sn])
    


run_test(dwell_time=1.0, num_records=10, file_name="./data/split_histo.dat")
