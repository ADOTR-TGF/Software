import json
import time
import zmq
import communication as com

"""
This example shows how to access a custom feature of the TGF firmware.
This firmware requires non-standard usbBases with a larger than normal FPGA, 
loaded with the TGF firmware.
The customization number for this firmware is 21505.
"""

def acquire_list_mode(num_buffers, file_name):
    """
    We assume that only one MCA is attached, and that the MCA Data Server is running.
    user should program the MCA for gain etc.
    Then use this example to acquire list mode data.

    :param num_buffers: Number of list mode bufers to be acquired
    :param file_name: Write the listmode data to this file , one json string per line.
    :return: None
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

    with open(file_name, 'w') as fout:
        pass
        
    # Command list
    cmd_clr = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
                 "data": {"fields": {"clear_statistics": 1, "clear_list_mode": 1, "lm_run": 1}}}    
    cmd_stop = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn, "data": {"fields": {"lm_run": 0}}}
    cmd_start = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn, "data": {"fields": {"lm_run": 1}}}
                 
    cmd_sel_0 = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn, "data": {"fields": {"lm_mode": 0}}}
    cmd_sel_1 = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn, "data": {"fields": {"lm_mode": 1}}}
    
    cmd_results = {"type": "mca_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
    cmd_read = {"type": "mca_cmd", "name": "fpga_tgf_lm", "dir": "read", "sn": sn}
    
    # Clear both listmode banks
    send_and_receive(mds_client, cmd_stop)
    send_and_receive(mds_client, cmd_sel_0)
    send_and_receive(mds_client, cmd_clr)
    send_and_receive(mds_client, cmd_sel_1)
    send_and_receive(mds_client, cmd_clr)
    
    # Start the list-mode run
    send_and_receive(mds_client, cmd_start)
    
    buffer_count = 0
    
    """
    time.sleep(10)
    send_and_receive(mds_client, cmd_sel_0)
    ret = send_and_receive(mds_client, cmd_read)  # Read list-mode data       
    lm_data = {"banks": 0, "lm_data": ret[sn]['fields']}
                        
    with open(file_name, 'a') as fout:
        fout.write(json.dumps(lm_data) + "\n")
    
    return
    """
    
    then = time.time()
    while buffer_count < num_buffers:

        time.sleep(0.05)
        
        while True:
            ret = send_and_receive(mds_client, cmd_results) 
            # ret is a dictionary with keys "registers", "fields", "user"
            results = ret[sn]["registers"]
            # Check which list mode buffer is full
            full_0 = (int(results[2])>>1) & 1
            full_1 = (int(results[2])>>3) & 1
            #print(results)
            time.sleep(0.002)
            
            if full_0:  # Read buffer 0
                send_and_receive(mds_client, cmd_sel_0)
                ret = send_and_receive(mds_client, cmd_read)  # Read list-mode data       
                lm_data = {"banks": "{:X}".format(2*full_1+full_0), "lm_data": ret[sn]['fields']}
                                    
                with open(file_name, 'a') as fout:
                    fout.write(json.dumps(lm_data) + "\n")
                buffer_count += 1
                
                # Clear this bank
                send_and_receive(mds_client, cmd_clr)
                

            if full_1: # Read buffer 1
                send_and_receive(mds_client, cmd_sel_1)
                ret = send_and_receive(mds_client, cmd_read)  # Read list-mode data       
                lm_data = {"banks": "{:X}".format(2*full_1+full_0), "lm_data": ret[sn]['fields']}
                                    
                with open(file_name, 'a') as fout:
                    fout.write(json.dumps(lm_data) + "\n")
                buffer_count += 1
                
                # Clear this bank
                send_and_receive(mds_client, cmd_clr)
                
                
            if full_0 or full_1:
                print("Time: {}; banks: {}, {}".format(time.time()-then, full_0, full_1))
                break

 
            
    print("Output data file:", file_name)
    
def send_and_receive(client, cmd):
    return json.loads(client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8'))

acquire_list_mode(num_buffers=1, file_name="./data/list_mode_tgf_3.json")

