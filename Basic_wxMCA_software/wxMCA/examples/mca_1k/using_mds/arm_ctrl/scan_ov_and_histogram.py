import json
import time
import zmq
import communication as com
import histo_analysis


def scan_ov(par):
    """
    We assume that only one MCA-1000 is attached, and that the MCA Data Server is running.
    Program the arm_ctrl structure in the MCA-100 to set the operating voltage; 
    then acquire a histogram for a dwell_time and measure the Cs-137 peak position.
    
    :param file_name: Write the resulting peak vs operating_voltage data to this file
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

    num_steps = par["num_steps"]
    ov_max = par["ov_max"]
    ov_min = par["ov_min"]
    dov = (ov_max - ov_min)/num_steps  # Step size
    dwell_time = par["dwell_time"]  # in seconds
    
    with open(par["file_name"], 'w') as fout:
        pass
        
    # Command to clear the old histogram and start a new data acquisition
    new_histo_cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
               "data": {"user": {"histogram_run": 1, "clear_histogram": 1, "clear_statistics": 1}}}
               
    # Command to read the histogram
    histo_read_cmd = {"type": "mca_cmd", "name": "arm_histogram", "dir": "read", "sn": sn}
    
    # Command to set a new operating voltage
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
       "data": {"fields": {"cal_ov": ov_min, "gain_stabilization": 0, "temp_ctrl": 1}}}
    send_and_receive(mds_client, cmd)
    
    for n in range(num_steps+1):
        # Set new operating voltage
        ov = ov_min + n*dov
        cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"cal_ov": ov, "gain_stabilization": 0, "temp_ctrl": 1}}}
        send_and_receive(mds_client, cmd)
        time.sleep(2)  # wait for the voltage to change and be stable
        
        # Accumulate histogram
        send_and_receive(mds_client, new_histo_cmd)
        time.sleep(dwell_time)
        
        #  Read the new histogram
        ret = send_and_receive(mds_client, histo_read_cmd)
        histo = ret[sn]["fields"]["histogram"]  # The raw histogram
        
        # analysis
        off = 100  # Ignore the potentially tall K-alpha peak at 37keV
        histo_max = max(histo[off:]) 
        idx_max = histo[off:].index(histo_max) + off
        imin = int(idx_max-50)
        imax = int(idx_max+60)
        res = histo_analysis.do_gauss_fit(histo[imin: imax+1], bck_model=2, fwhm=25)
        peak = res["x_max"]+imin
        
        #print(idx_max, peak)
        # Create and store output data, one line at a time
        results = {"ov": ov, "peak": peak}
        with open(par["file_name"], 'a') as fout:
            fout.write(json.dumps(results) + "\n")
       
def send_and_receive(mds_client, cmd):
    """ Just to keep the expressions short; send a command and return the answer as a dictionary. """
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    return json.loads(msg)
    
    
par = {
    "file_name": "./data/peak_vs_ov_scan.json",
    "num_steps": 1000,
    "ov_min": 755,
    "ov_max": 780,
    "dwell_time": 30
}   
scan_ov(par)
