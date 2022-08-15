import json
import time
import communication as com


def read_and_clear(file_name, dwell_time, num_data_points):
    """
    We assume that only one device is attached, and that the device_server is running.
    Program the arm_ctrl structure in the device to enable the read_and_clear feature.
    Now, after every read, the counters are cleared without needing an extra command.
    Hence, loss-less reading.

    :param file_name: Write the count rate data to this file.
    :param dwell_time: Time in seconds per measurement point
    :param num_data_points: Number of data points to write to file
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
    
    count_rates = []

    # Set the parameters for sample counting
    # run_mode bits: 1 -> counting, 8 -> read_and_clear
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"run_mode": 9, "run_action": 1, "run_time_sample": 20.0}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    for n in range(num_data_points):
        time.sleep(dwell_time)
        # Read back data and store
        # In arm_status.json look for the fields "run_time", "count_rate", and "count_rate_err".
        cmd = {"type": "mca_cmd", "name": "arm_status", "dir": "read", "sn": sn}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        arm_status = ret[sn]
        count_rates += [arm_status["fields"]["count_rate"]]
        # print(arm_status)
        
    with open(file_name, 'w') as fout:
        # out_str = ["{}\n".format(cr) for cr in count_rates]  # for a csv file
        out_str = json.dumps({"count_rates": count_rates})
        fout.write(out_str)


read_and_clear(file_name="./data/count_rates.json", dwell_time=1, num_data_points=10)
