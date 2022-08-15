import json
import time
import zmq
import communication as com


def log_net_alarm_cr(file_name):
    """
    We assume that only one device is attached, and that the mca_server is running.
    Start a log of measured net count rate over back ground and alarm probability on a SiPM-Counter.
    
    In preparation, we assume that the user has measured the background count rate setting the "active_bank"
    control to 1 for some time.  After that, "active_bank" must be set to zero again to measure samples, 
    eg soil samples.
    
    Next, we turn on the alarm computation by setting the "sample_alarm" control to 1.
    
    Here, the purpose of the logger is to record how the measured net count rate from a weakly radioactive 
    sample slowly stabilizes over time and how the corresponding alarm probability stabilizes as well.
    

    :param file_name: Write the voltage data to this file.
    :return:
    """
    time_step = 0.050  # Built-in time granularity is 50ms; Don't change this value
    dwell_time = 20  # in 50ms units; 0<= dwell_time <= 255
    wait_bins = 1024  # Wait that many logger dwell times before reading the logger data.
    idx_0 = 15 # net count rate
    idx_1 = 17 # Background probability
    
    mds_ip = "tcp://127.0.0.1:5507"
    mds_client = com.zmq_device(mds_ip, "client")

    cmd = {"type": "server_cmd", "name": "hello"}
    msg = send_and_receive(mds_client, cmd)
    ret = json.loads(msg)
    sn_list = ret['sn_list']
    for sn in sn_list:
        print("Serial number:", sn)
    sn = sn_list[0]  # We only use one attached device here
    
    xctrl_0 = (idx_1 << 16) + (idx_0 << 8) + dwell_time  # DC-baseline, operating voltage, dwell_time
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"xctrl_0": xctrl_0, 'run_action': 8}, "user": {"clear_statistics": 1}}
          }
    msg = send_and_receive(mds_client, cmd)
           
    time.sleep(256*dwell_time*time_step)
    
    cmd = {"type": "mca_cmd", "name": "arm_logger", "dir": "read", "sn": sn, 'num_items': 2048}  # For some versions of the PMT-1000, only 1024 items are available, in 2 511-item banks
    msg = send_and_receive(mds_client, cmd)
    ret = json.loads(msg)
    
    print(ret[sn]["registers"][0:4])
    
    var_0 = ret[sn]["user"]["var_0"]
    var_1 = ret[sn]["user"]["var_1"]
    out_dict = {"var_0": var_0, "var_1": var_1 }
    
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(out_dict) + "\n")
        fout.write(json.dumps(ret[sn]) +"\n")
 
def send_and_receive(client, cmd):
    return client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    
log_net_alarm_cr(file_name="./data/sample_alarm.json")

