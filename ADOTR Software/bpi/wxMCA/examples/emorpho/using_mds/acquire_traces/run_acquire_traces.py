import json
import time
import zmq
import communication as com


def acquire_traces(num_traces, file_name):
    """
    We assume that only one eMorpho is attached, and that the MCA Data Server is running.
    Program FPGA control registers to set the trace acquisition mode.  Then check the eMorpho if the trace
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

    # Program FPGA controls to set the trace acquiition mode;
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"vt_run": 0}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    for trace_num in range(num_traces):
        # Start the trace run
        cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
               "data": {"fields": {"clear_trace": 1, "trace_run": 1, "run": 1}}}
        mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

        while True:  # Poll until trace acquisition has finished
            cmd = {"type": "mca_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
            msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
            ret = json.loads(msg)  # ret is a dictionary with keys "registers", "fields", "user"
            if ret[sn]["user"]["trace_done"] == 1:
                break

        # Read trace data
        cmd = {"type": "mca_cmd", "name": "fpga_trace", "dir": "read", "sn": sn}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        trace = ret[sn]['fields']['trace']
        with open(file_name, 'a') as fout:
            fout.write(json.dumps(trace) + ",\n")
            
    print("Output data file:", file_name)


acquire_traces(num_traces=10, file_name="./data/traces.dat")
