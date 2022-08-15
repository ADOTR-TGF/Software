import json
import time
import zmq
import communication as com


def track_voltage(file_name):
    """
    We assume that only one device is attached, and that the pmt_mca_server is running.
    Read the current status data from the ARM processor.
    
    Note that if bit 0 of element [63] of the calibration lookup table data is set to 1,
    then the "lock-bit" is set and all voltages will read back as zero.

    :param file_name: Write the voltage data to this file.
    :return:
    """
    
    dwell_time = 1  # in seconds
    num_data = 200  # Number of voltage readings to record.
    

    mds_ip = "tcp://127.0.0.1:5507"
    mds_client = com.zmq_device(mds_ip, "client")

    cmd = {"type": "server_cmd", "name": "hello"}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    sn_list = ret['sn_list']
    for sn in sn_list:
        print("Serial number:", sn)
    sn = sn_list[0]  # We only use one attached device here

    cmd = {"type": "mca_cmd", "name": "arm_status", "dir": "read", "sn": sn}
    
    voltage_list = []
    for n in range(num_data):
        # Read arm_status
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        arm_status = ret[sn]
        voltage_list += [arm_status["fields"]["op_voltage"]]
        time.sleep(dwell_time)
    
    voltage_record = {"dwell_time": dwell_time, "voltages": voltage_list}
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(voltage_record) + ",\n")
 
 
def log_voltage(file_name):
    """
    We assume that only one device is attached, and that the pmt_mca_server is running.
    Read the current status data from the ARM processor.
    
    Note that if bit 0 of element [63] of the calibration lookup table data is set to 1,
    then the "lock-bit" is set and all voltages will read back as zero.
    
    Write operating voltage to log file while continuously updating the log file.

    :param file_name: Write the voltage data to this file.
    :return:
    """
    
    dwell_time = 1  # in seconds
    num_data = 14*3600 # Number of voltage readings to record.
    
    mds_ip = "tcp://127.0.0.1:5507"
    mds_client = com.zmq_device(mds_ip, "client")

    cmd = {"type": "server_cmd", "name": "hello"}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    sn_list = ret['sn_list']
    for sn in sn_list:
        print("Serial number:", sn)
    sn = sn_list[0]  # We only use one attached device here

    cmd = {"type": "mca_cmd", "name": "arm_status", "dir": "read", "sn": sn}
    
    with open(file_name, 'w') as fout:
        pass
    then = time.time()
    for n in range(num_data):
        # Read arm_status
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        arm_status = ret[sn]
        data_out = {"dt": "{:.3f}".format(time.time()-then), 
                    "ov": "{:.3f}".format(arm_status["fields"]["op_voltage"]), 
                    "cpu": "{:.3f}".format(arm_status["fields"]["cpu_temperature"])}
        time.sleep(dwell_time)
    
        with open(file_name, 'a') as fout:
            fout.write(json.dumps(data_out) + ",\n")


log_voltage(file_name="./data/voltage_log.json")
#track_voltage(file_name="./data/voltage_list.json")
