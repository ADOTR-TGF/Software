import json
import time
import zmq
import communication as com


def acquire_time_slice(num_slices, file_name):
    """
    We assume that only one eMorpho is attached, and that the emorpho_server is running.
    Check the results registers for availability of a new time slice.  When that is the case, read the data buffer
    and store as one json object in file.

    :param num_slices: Number of time slices to be acquired
    :param file_name: Write the time slices to file
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

    # Program FPGA controls to reset the statistics counters and the time_slice machinery.;
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"clear_statistics": 1, "clear_histogram": 1, "run": 1}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    status_cmd = {"type": "mca_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
    status_cmd = json.dumps(status_cmd).encode('utf-8')
    slice_cmd = {"type": "mca_cmd", "name": "fpga_time_slice", "dir": "read", "sn": sn}
    slice_cmd = json.dumps(slice_cmd).encode('utf-8')
    buffer_number = 0
    for slice_number in range(num_slices):
        
        while True:  # Poll until one or more time slices are available
            msg = mds_client.send_and_receive(status_cmd).decode('utf-8')
            ret = json.loads(msg)  # ret is a dictionary with keys "registers", "fields", "user"
            num_buffers = (ret[sn]["fields"]["status"] >> 3) & 0x1F  # Number of 105ms time slices that are available
            if num_buffers > 0:
                break
        # Read slice data
        for n in range(num_buffers):
            msg = mds_client.send_and_receive(slice_cmd).decode('utf-8')
            ret = json.loads(msg)
            slice_data = ret[sn]['fields']
            if slice_data['buffer_number'] == buffer_number:  # incomplete buffer
                continue
            
            with open(file_name, 'a') as fout:
                fout.write(json.dumps(slice_data) + "\n")


acquire_time_slice(num_slices=10, file_name="ts.dat")
