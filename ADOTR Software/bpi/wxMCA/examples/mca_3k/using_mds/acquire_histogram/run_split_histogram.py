import json
import time
import zmq
import communication as com


def acquire_split_histograms(dwell_time, num_records, file_name):
    """
    We assume that only one SiPM-Morpho is attached, and that the mca3k_server is running.
    
    This example demonstrates loss-less histogram acquisition using the built-in 
    split-histogram mode.  Statistics counters and histogram data appear in two
    equal-sized banks (2Kx32 for the histogram).  While the FPGA on the eMorpho
    is acquiring data into one bank, the client can read and then clear the inactive
    bank at leisure.
    
    The data file will consist one json string per line.

    :param dwell_time: Acquisition time in seconds before switching to the other bank
    :param num_records: Maximum number of records to write to file.
    :param file_name: Write the histogram to this file as one long line
    :return: None
    
    Program parameters
    :param summary: 0=> print full count rate and histogram data to file
                    1=> print raw statistics and sum of histogram entries to file.
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
    
    # Prepare histogram run without preprogrammed end (run_time = 0)
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"daq_mode": 0}, "user": {"run_time": 0}}}
    # cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn, 
           # "data": {"fields": {"gain_select": 2, "rtlt": 2, "daq_mode": 1}, 
           # "user": {"integration_time": 1.2e-6, "hold_off_time": 1.5e-6, "digital_gain": 4800, 
                    # "pulse_threshold": 0.010, "run_time": 0}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8'))
    
    
    # Prepare two-bank histogram acquisition (Note: histo_run=0)
    cmd = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
           "data": {"fields": {"segment_enable": 0, "segment": 0, 
                               "clear_histogram": 1, "clear_statistics": 1, "histo_run": 0}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8'))
    
    # Start two-bank histogram acquisition (Note: segment_enable=1)
    cmd = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
           "data": {"fields": {"segment_enable": 1, "segment": 0, "histo_run": 1}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8'))
    segment = 0
    banks = ["bank_0", "bank_1"]
    summary = 0
    
    with open(file_name, 'w') as fout:  # Erase the file
        pass
        
    for n in range(num_records):
        time.sleep(dwell_time)
        if (n%2)==1:
            time.sleep(dwell_time)
            
        bank = banks[segment]
        
        # Switch the active segment
        segment = 1 if segment==0 else 0
        cmd = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
               "data": {"fields": {"segment": segment}}}
        mds_client.send_and_receive(json.dumps(cmd).encode('utf-8'))
        
        # Read count rates
        cmd = {"type": "mca_cmd", "name": "fpga_statistics", "dir": "read", "sn": sn}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8'))
        ret_rates = json.loads(msg)
        rates = ret_rates[sn]["user"][bank]
        #rates = ret_rates[sn]["registers"]
              
        # Read histogram bank
        cmd = {"type": "mca_cmd", "name": "fpga_histogram", "dir": "read", "sn": sn, "num_items": 2048}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8'))
        ret_histo = json.loads(msg)
        histogram = ret_histo[sn]['registers']
        
        # Clear inactive segment
        cmd = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
               "data": {"fields": {"clear_histogram": 1, "clear_statistics": 1}}}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8'))
        ret_action = json.loads(msg)
        action = ret_action[sn]['registers']
        
        if summary:
            out_dict = {"rates": ret_rates[sn]["registers"], "histogram": sum(histogram)}
        else:
            out_dict = {"rates": rates, "histogram": histogram}

        with open(file_name, 'a') as fout:
            fout.write(json.dumps(out_dict) + "\n")
            
    print("Output data file:", file_name)


acquire_split_histograms(dwell_time=1.0, num_records=10, file_name="./data/split_histo.dat")
