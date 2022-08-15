import json
import time
import zmq
import communication as com


def log_voltage_cr(file_name):
    """
    We assume that only one device is attached, and that the mca_server is running.
    Start a log of operating voltage vs count rate on a SiPM-1000.
    The purpose of the logger is to record quick changes of operating conditions,
    eg operating voltage and count rate, without polling the MCA at a high rate.
    
    Polling the MCA-1000 at a high rate causes extra dead times and inteferes with the regular operation
    Instead the logger captures up to 1023 measurements of two variables without requeiring host action..
    
    The host can then read the log after it has been completed.  The logger implements a rolling log, 
    meaning that old data will continuously be overwritten by new data.

    :param file_name: Write the voltage data to this file.
    :return:
    """
    time_step = 0.050  # Built-in time granularirty is 50ms
    dwell_time = 1  # in 50ms units; 0<= dwell_time <= 255
    wait_bins = 1024  # Wait that many logger dwell times before reading the logger data.
    idx_op_volt = 0  # op_voltage
    idx_par = 35 # Measuring the DC baseline in raw 12-bit ADC units
    idx_events = 0x80 + 0  # The MSB=1 indicates this is computed by the logger; It is not amongst the arm_status fields
    
    mds_ip = "tcp://127.0.0.1:5507"
    mds_client = com.zmq_device(mds_ip, "client")

    cmd = {"type": "server_cmd", "name": "hello"}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    sn_list = ret['sn_list']
    for sn in sn_list:
        print("Serial number:", sn)
    sn = sn_list[0]  # We only use one attached device here
    
    volt_steps = [30, 34, 30]
    
    # Set operating voltage
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"cal_ov": volt_steps[0]}}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    time.sleep(256*dwell_time*time_step)
    
    xctrl_0 = (idx_par << 16) + (idx_op_volt << 8) + dwell_time  # DC-baseline, operating voltage, dwell_time
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"xctrl_0": xctrl_0, 'run_action': 8}}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
           
    time.sleep(256*dwell_time*time_step)
    # Set new operating voltage
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn, "data": {"fields": {"cal_ov": volt_steps[1]}}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    time.sleep(256*dwell_time*time_step)
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn, "data": {"fields": {"cal_ov":volt_steps[2]}}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    time.sleep(350*dwell_time*time_step)
    
    cmd = {"type": "mca_cmd", "name": "arm_logger", "dir": "read", "sn": sn, 'num_items': 2048}  # For some versions of the PMT-1000, only 1024 items are available, in 2 511-item banks
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    
    print(ret[sn]["registers"][0:4])
    
    var_0 = ret[sn]["user"]["var_0"]
    var_1 = ret[sn]["user"]["var_1"]
    out_dict = {"var_0": var_0, "var_1": var_1 }
    
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(out_dict) + "\n")
 
 
log_voltage_cr(file_name="./data/voltage_cr_log.json")

