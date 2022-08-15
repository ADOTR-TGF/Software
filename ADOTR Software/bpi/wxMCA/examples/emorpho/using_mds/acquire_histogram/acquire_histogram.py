import json
import time
import zmq
import communication as com


def acquire_one_histogram(dwell_time, file_name):
    """
    We assume that only one eMorpho is attached, and that the MCA Data Server is running.

    :param dwell_time: Acquisition time in seconds
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

    # Start a histogram run 
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"clear_histogram": 1, "clear_statistics": 1, "run": 1}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8'))

    time.sleep(dwell_time)  # wait

    # Read histogram data
    cmd = {"type": "mca_cmd", "name": "fpga_histogram", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    # print(ret)
    histogram = ret[sn]['registers']

    with open(file_name, 'a') as fout:
        fout.write(json.dumps(histogram) + "\n")


def acquire_one_histogram_2(dwell_time, file_name):
    """
    We assume that only one eMorpho is attached, and that the eMorpho_server is running.
    Program FPGA control registers to stop counting events when the histogram has finished,
    and set the acquisition time to be dwell time.  Then check the eMorpho if the histogram
    acquisition has finished.  When that is the case, read histogram and count rates and store as one json object in file.

    :param dwell_time: Acquisition time in seconds
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

    # Program FPGA controls; Note the mixed use of high-level 'user' data and lower-level 'fields' data.
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"daq_mode": 1, "rtlt": 2}, "user": {"run_time": dwell_time}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    # Start the histogram run
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"clear_histogram": 1, "clear_statistics": 1, "run": 1}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    while True:  # Poll until histogram acquisition has finished
        time.sleep(1)  # wait 1s between polls
        cmd = {"type": "mca_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)  # ret is a dictionary with keys "registers", "fields", "user"
        if ret[sn]["user"]["histo_done"] == 1:
            break

    # Read histogram data
    cmd = {"type": "mca_cmd", "name": "fpga_histogram", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    histogram = ret[sn]['registers']

    # Read count rate data
    cmd = {"type": "mca_cmd", "name": "fpga_statistics", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    count_rates = ret[sn]["user"]["bank_0"]

    with open(file_name, 'a') as fout:
        out_dict = {"count_rates": count_rates, "histogram": histogram}
        fout.write(json.dumps(out_dict) + "\n")


acquire_one_histogram(dwell_time=10, file_name="one_histo.dat")

acquire_one_histogram_2(dwell_time=10, file_name="rates_histo.dat")
