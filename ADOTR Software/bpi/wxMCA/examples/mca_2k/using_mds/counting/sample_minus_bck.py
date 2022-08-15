import json
import time
import communication as com


def sample_minus_bck(file_name):
    """
    We assume that only one device is attached, and that the device_server is running.
    Here we simulate a sample minus background counting by doing this:
    1) Set trigger threshold to 0.2 (reducing the simulated count rate to 400cps) 
    and collect data as a background measurement
    2) Set the trigger threshold to 0.1 to increase the count rate to 450cps, 
    and colect data as a sample measurement.
    
    We also turn on computing the probability of the measured sample count rate is 
    compatible with the background count rate.

    :param file_name: Write the arm_status data to this file after the read back.
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
    
    dwell_time = float(input("Measure background for how many seconds? "))
    print("You asked for {} sec.".format(dwell_time))

    # Set the parameters for background counting
    # run_mode bits: 1 -> counting, 2-> background
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"run_mode": 3, "run_action": 1, "run_time_bck": dwell_time}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
           
    time.sleep(dwell_time+1)
    
    print("Background measurement is done.")
    dwell_time = float(input("Measure sample for how many seconds? "))
    print("You asked for {} sec.".format(dwell_time))
    
    # Set the parameters for sample counting
    # run_mode bits: 1 -> counting, 0x80 -> sample_alarm
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"run_mode": 0x81, "run_action": 1, "run_time_sample": dwell_time}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    
    time.sleep(dwell_time+1)

    # Read back data and store
    # In arm_status.json look for the fields "run_time", "count_rate", and "count_rate_err",
    # "run_time_bck", "count_rate_bck", and "count_rate_bck_err",
    # "count_rate_diff", and "count_rate_diff_err", and "background_probability"
    cmd = {"type": "mca_cmd", "name": "arm_status", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    arm_status = ret[sn]
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(arm_status) + ",\n")
    
    status = arm_status["fields"]
    print("count_rate difference = {:.3f} +/- {:.3f}".format(status["count_rate_diff"], status["count_rate_diff_err"]))
    print("Probability that sample = background: {:.6g}".format(status["background_probability"]))


sample_minus_bck(file_name="./data/arm_status.json")
