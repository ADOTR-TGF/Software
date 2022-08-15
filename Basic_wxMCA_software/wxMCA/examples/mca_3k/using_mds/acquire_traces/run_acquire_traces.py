import json
import time
import zmq
import communication as com


def acquire_traces(num_traces, file_name):
    """
    We assume that only one SiPM-Morpho is attached, and that the mca3k_server is running.
    Program FPGA control registers to set the trace acquisition mode.  Then check the SiPM-Morpho if the trace
    acquisition has finished.  When that is the case, read the trace and store as one json object in file.

    :param num_traces: Number of traces to be acquired
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
        print("Serial number:", sn)
    sn = sn_list[0]  # We only use one attached device here

    # Program FPGA controls to set the trace acquisition mode;
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"trace_mode": 0, "trigger_delay": 100}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    
    start_cmd = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
               "data": {"fields": {"clear_trace": 1, "trace_run": 1}}}
    check_cmd = {"type": "mca_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
    read_cmd = {"type": "mca_cmd", "name": "fpga_trace", "dir": "read", "sn": sn}

    with open(file_name, 'w') as fout:
        pass
    for trace_num in range(num_traces):
        # Start the trace run
        mds_client.send_and_receive(json.dumps(start_cmd).encode('utf-8')).decode('utf-8')
        #time.sleep(0.1)
        while True:  # Poll until trace acquisition has finished
            msg = mds_client.send_and_receive(json.dumps(check_cmd).encode('utf-8')).decode('utf-8')
            ret = json.loads(msg)  # ret is a dictionary with keys "registers", "fields", "user"
            if ret[sn]["user"]["trace_done"] == 1:
                break
            #time.sleep(0.1)

        # Read trace data
        #time.sleep(0.1)
        msg = mds_client.send_and_receive(json.dumps(read_cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        trace = ret[sn]['fields']['trace']
        with open(file_name, 'a') as fout:
            fout.write(json.dumps(trace) + ",\n")


acquire_traces(num_traces=10, file_name="./data/traces.dat")
