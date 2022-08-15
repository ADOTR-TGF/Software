import json
import time
import zmq
import communication as com


def acquire_list_mode(num_buffers, file_name):
    """
    We assume that only one MCA is attached, and that the MCA Data Server is running.
    user should program the MCA for gain etc.
    Then use this example to acquire list mode data.

    :param num_buffers: Number of traces to be acquired
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
    
    # Clear both listmode banks
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
                       "data": {"fields": {"lm_mode": 0}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    cmd = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
           "data": {"fields": {"clear_statistics": 1, "clear_list_mode": 1, "histo_run": 1}}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
                       "data": {"fields": {"lm_mode": 1}}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    cmd = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
           "data": {"fields": {"clear_statistics": 1, "clear_list_mode": 1, "histo_run": 1}}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    
    # Start the list-mode run
    cmd = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
           "data": {"fields": {"clear_statistics": 1, "clear_list_mode": 1, "lm_run": 1, "histo_run": 1}}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    
    buffer_count = 0
    cmd_results = {"type": "mca_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
    then = time.time()
    while buffer_count < num_buffers:

        time.sleep(0.05)
        
        while True:
            ret = json.loads(mds_client.send_and_receive(json.dumps(cmd_results).encode('utf-8')).decode('utf-8'))
            # ret is a dictionary with keys "registers", "fields", "user"
            results = ret[sn]["registers"]
            #print("{:X}".format(results[2]))
            # Check which list mode buffer is full
            full_0 = (int(results[2])>>9) & 1
            full_1 = (int(results[2])>>10) & 1
            time.sleep(0.002)
            
            if full_0:  # Read buffer 0
                cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
                       "data": {"fields": {"lm_mode": 0}}}
                mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
                
                # Read list-mode data
                cmd = {"type": "mca_cmd", "name": "fpga_lm_nrl1", "dir": "read", "sn": sn}
                ret = json.loads(mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8'))
                lm_data = {"banks": "{:X}".format((int(results[2])>>9)&0x3), "lm_data": ret[sn]['registers']}
                                    
                with open(file_name, 'a') as fout:
                    fout.write(json.dumps(lm_data) + "\n")
                buffer_count += 1
                
                # Clear this bank
                cmd = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
                       "data": {"fields": {"clear_statistics": 1, "clear_list_mode": 1, "histo_run": 1}}}
                msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
                
                                   
            if full_1: # Read buffer 1
                cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
                       "data": {"fields": {"lm_mode": 1}}}
                mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
            
                # Read list-mode data
                cmd = {"type": "mca_cmd", "name": "fpga_lm_nrl1", "dir": "read", "sn": sn}
                ret = json.loads(mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8'))
                lm_data = {"banks": "{:X}".format((int(results[2])>>9)&0x3), "lm_data": ret[sn]['registers']}
                                    
                with open(file_name, 'a') as fout:
                    fout.write(json.dumps(lm_data) + "\n")
                buffer_count += 1
                
                # Clear this bank
                cmd = {"type": "mca_cmd", "name": "fpga_action", "dir": "rmw", "sn": sn,
                       "data": {"fields": {"clear_statistics": 1, "clear_list_mode": 1, "histo_run": 1}}}
                msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
                
            if full_0 or full_1:
                print("Time: {}; banks: {}, {}".format(time.time()-then, full_0, full_1))
                break

 
            
    print("Output data file:", file_name)

acquire_list_mode(num_buffers=100, file_name="./data/list_mode_nrl100.dat")

