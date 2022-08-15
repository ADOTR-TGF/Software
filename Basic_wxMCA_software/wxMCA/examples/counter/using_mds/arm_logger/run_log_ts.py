import json
import time
import zmq
import communication as com


def log_portal(file_name):
    """
    We assume that only one device is attached, and that the mca_server is running.
    Start a log of events and the response of the portal alarm (ie time slice computations)
    The purpose of the logger is to record quick changes of count rate conditions,
    and measure the portal response, without polling the MCA at a high rate.
    
    Polling the counter at a high rate causes extra dead times and interferes with the regular operation
    Instead the logger captures up to 1023 measurements of two variables without requiring host action..
    
    The host can then read the log after it has been completed.  The logger implements a rolling log, 
    meaning that old data will continuously be overwritten by new data.

    :param file_name: Write the voltage data to this file.
    :return:
    """
    time_step = 0.050  # Built-in time granularity is 50ms
    dwell_time = 2  # in 50ms units; 0<= dwell_time <= 255
    wait_bins = 1024  # Wait that many logger dwell times before reading the logger data.
    idx_ts_par = 21  # TS_Alarm=21, TS_Net=22, TS_Prob=24
    idx_events = 0x80 + 1  # The MSB=1 indicates this is computed by the logger; It is not among the arm_status fields
                           # +0 => total events in a time slice
                           # +1 => total events within the alarm-ROI in a time slice
    
    mds_ip = "tcp://127.0.0.1:5507"
    mds_client = com.zmq_device(mds_ip, "client")

    cmd = {"type": "server_cmd", "name": "hello"}
    ret = send_and_receive(mds_client, cmd)
    sn_list = ret['sn_list']
    for sn in sn_list:
        print("Serial number:", sn)
    sn = sn_list[0]  # We only use one attached device here
    
    xctrl_0 = (idx_events << 16) + (idx_ts_par << 8) + dwell_time  # Events per dwell time, operating voltage, dwell_time
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"xctrl_0": xctrl_0, 'run_action': 12}}}
    send_and_receive(mds_client, cmd)
    #msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
           
    time.sleep(1100*dwell_time*time_step)
    
    cmd = {"type": "mca_cmd", "name": "arm_logger", "dir": "read", "sn": sn, 'num_items': 2048}  # For some versions of the PMT-1000, only 1024 items are available, in 2 511-item banks
    ret = send_and_receive(mds_client, cmd)
    
    print(ret[sn]["registers"][0:4])
    
    var_0 = ret[sn]["user"]["var_0"]
    var_1 = ret[sn]["user"]["var_1"]
    out_dict = {"dwell_time": int(xctrl_0)&0xFF, "ch0":(int(xctrl_0)&0xFF00)>>8, "ch1":(int(xctrl_0)&0xFF0000)>>16, "var_0": var_0, "var_1": var_1 }
    
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(out_dict) + "\n")
 
def send_and_receive(mds_client, cmd):
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    return json.loads(msg)
     
log_portal(file_name="./data/ts_log_oct_9.json")

