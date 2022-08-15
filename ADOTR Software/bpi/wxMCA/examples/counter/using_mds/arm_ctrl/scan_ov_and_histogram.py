import json
import time
import zmq
import communication as com
import histogram_fit


def scan_ov(file_name):
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

    n_max = 4
    ov_max = 36.0
    ov_min = 34.0
    dov = (ov_max - ov_min)/n_max  # Step size
    dwell_rime = 60  # in seconds
    
    with open(file_name, 'w') as fout:
        pass
        
    # Command to clear the old histogram and start a new data acquistion
    new_histo_cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
               "data": {"fields": {"histogram_run": 1, "clear_histogram": 1, "clear_statistics": 1}}}
               
    # Command to read the histogram
    histo_read_cmd = {"type": "mca_cmd", "name": "arm_histogram", "dir": "read", "sn": sn}
    
    # Command to set a new operating voltage
    cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
       "data": {"fields": {"cal_ov": ov_min, "gain_stabilization": 0, "temp_ctrl": 1}}}
    send_and_receive(mds_client, cmd)
    
    for n in range(n_max+1):
        # Set new operating voltage
        ov = ov_min + n*dov
        cmd = {"type": "mca_cmd", "name": "arm_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"cal_ov": ov, "gain_stabilization": 0, "temp_ctrl": 1}}}
        send_and_receive(mds_client, cmd)
        time.sleep(2)  # wait for the voltage to chnage and be stable
        
        # Accumulate histogram
        send_and_receive(mds_client, new_histo_cmd)
        time.sleep(dwell_time)
        
        #  Read the new histogram
        ret = send_and_receive(mds_client, histo_read_cmd)
        histo = ret[sn]["fields"]["histogram"]  # The raw histogram
        
        # analysis
        off = 100  # Ignore the potentially tall K-alpha peak at 37keV
        histo_max = max(histo[off:]) 
        idx_max = histo[off:].index(idx_max)
        imin = int(idx_max-100)
        imax = int(idx_max+120)
        res = histogram_fit.do_gauss_fit(histo[imin: imax+1], bck_model=2, fwhm=50)
        peak = res[0]+off
        
        # Create and store output data, one line at a time
        results = {"ov": ov, "peak": peak}
        with open(file_name, 'a') as fout:
            fout.write(json.dumps(results) + "\n")
       
def send_and_receive(mds_client, cmd):
    """ Just to keep the experessions short; send a command and return the answer as a dictionary. """
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    return json.loads(msg)
    
    
    
write_arm_ctrl(file_name="./data/baseline_scan.json")
