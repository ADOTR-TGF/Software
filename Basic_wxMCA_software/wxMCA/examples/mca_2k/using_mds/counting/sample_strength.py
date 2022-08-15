import json
import time
import communication as com


def record_sample_counting(file_name="./data/sample_records.json", dt=1, num_records=300):
    """
    We assume that only one device is attached, and that the device_server is running.
    
    1) Preparation:
    User has set 'sample-bck' to 1 in the Alarm panel of the PMT-MCA dashboard. Alternatively, 
    a previous program has set ['user']['sample_alarm'] to 1.  And the user has acquired 
    a background histogram for some time.  The PMT-MCA has not been turned off, and the 
    background histogram is still stored in the device.
    
    2) Sample measurement:
    The function will start a new sample acquisition run and record data once per 'dt' seconds,
    for a total of 'num_records' data points.

    :param file_name: Write the arm_status data to this file.
    :param dt: Time between recordings
    :param num_records: Number of sample records to write to disk.
    :return: None
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
    
    # Start the sample acquisition run
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"run_time": 0},
                    "user": {'sample_alarm': 1, 'clear_statistics': 1, 'clear_histogram': 1, 'histogram_run': 1, 'active_bank': 0}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    
    # Delete previous data
    with open(file_name, 'w') as fout:
        pass
        
    for n in range(num_records):
        time.sleep(dt)
        # Read back data and store
        # In the json file, look for fields with names starting with 'roi'
        cmd = {"type": "mca_cmd", "name": "arm_status", "dir": "read", "sn": sn}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        arm_status = ret[sn]
        with open(file_name, 'a') as fout:
            fout.write(json.dumps(arm_status) + "\n")
    


record_sample_counting(file_name="./data/sample_records.json", num_records=600)
