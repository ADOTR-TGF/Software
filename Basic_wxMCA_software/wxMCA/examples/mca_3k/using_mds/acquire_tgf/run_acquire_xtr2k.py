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

def acquire_xtrace(params):
    """
    We assume that only one MCA is attached, and that the MCA Data Server is running.
    user should program the MCA for gain etc.
    Then use this example to acquire list mode data.

    :param num_buffers: Number of traces to be acquired
    :param file_name: Write the 2K samples pulse train data to this file , one json string per line.
    :return: None
    """
    num_buffers = params["num_buffers"]
    
    mds_ip = "tcp://127.0.0.1:5507"
    mds_client = com.zmq_device(mds_ip, "client")

    cmd = {"type": "server_cmd", "name": "hello"}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    sn_list = ret['sn_list']
    for sn in sn_list:
        print("Unique serial number:", sn)
    sn = sn_list[0]  # We only use one attached device here

    with open(params["file_name"], 'w') as fout:
        pass
        
    # Command list
    xt_number = params["xt_number"]
    if xt_number == 0:
        pulse_name = "fpga_tgf_xt28k"
    else:
        pulse_name = "fpga_tgf_xt2k_{}".format(xt_number)
    
    cmd_clr = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
               "data": {"fields": {"clear_trace": 1, "run": 1}}}
    cmd_start = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
                 "data": {"fields": {"clear_statistics": 1, "clear_trace": 1, "trace_run": 1, "run": 1}}}
    cmd_read = {"type": "mca_cmd", "name": pulse_name, "dir": "read", "sn": sn}
    cmd_tgf_status = {"type": "mca_cmd", "name": "fpga_tgf_results", "dir": "read", "sn": sn}
    cmd_read_fpga_tgf_ctrl = {"type": "mca_cmd", "name": "fpga_tgf_ctrl", "dir": "read", "sn": sn}
    cmd_read_fpga_ctrl = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "read", "sn": sn}
       
    N_field = "xtrn{}".format(xt_number)
    M_field = "xtrm{}".format(xt_number)
    C_field = "xtrc{}".format(xt_number)
    cmd_set_xtr_ctrl = {"type": "mca_cmd", "name": "fpga_tgf_ctrl", "dir": "rmw", "sn": sn,
                        "data": {"fields": {N_field: params["ctrl_N"],
                                            M_field: params["ctrl_M"],
                                            C_field: params["ctrl_C"]}}}
    
    print(cmd_set_xtr_ctrl)
    # Program the fpga controls pertaining to the 2K trace
    msg = mds_client.send_and_receive(json.dumps(cmd_set_xtr_ctrl).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    fpga_tgf_ctrl = ret[sn]["registers"]
    print(fpga_tgf_ctrl)
    
    if 0:  # Just some read backs to check that control registers were written correctly
        msg = mds_client.send_and_receive(json.dumps(cmd_read_fpga_ctrl).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        fpga_tgf_ctrl = ret[sn]["registers"]
        print(fpga_tgf_ctrl)
        
        msg = mds_client.send_and_receive(json.dumps(cmd_read_fpga_tgf_ctrl).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        fpga_tgf_ctrl = ret[sn]["registers"]
        print(fpga_tgf_ctrl)
    
    
    buffer_count = 0
    then = time.time()
    while buffer_count < num_buffers:

        # Start the x_trace run
        msg = mds_client.send_and_receive(json.dumps(cmd_start).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        
        xtr_done = False
        while not xtr_done:
            # Check if trace mode buffer is full
            ret_status = json.loads(mds_client.send_and_receive(json.dumps(cmd_tgf_status).encode('utf-8')).decode('utf-8'))
            # ret_status is a dictionary with keys "registers", "fields", "user"
            results = ret_status[sn]["registers"]            
            xtr_done = ret_status[sn]['user']['xt{}_done'.format(xt_number)]
        
        ret_xtr = json.loads(mds_client.send_and_receive(json.dumps(cmd_read).encode('utf-8')).decode('utf-8'))
        pulse_data = {"freeze": ret_status[sn]['fields']['xtwc{}'.format(xt_number)], "pulse": ret_xtr[sn]['registers']}
        print("Pulse Max:", max(pulse_data['pulse']))
        print("Freeze time: {}ms".format(pulse_data['freeze']/5e3))
        #print(results)
                            
        with open(params["file_name"], 'a') as fout:
            fout.write(json.dumps(pulse_data) + "\n")
        buffer_count += 1
        
        # Clear this bank
        msg = mds_client.send_and_receive(json.dumps(cmd_clr).encode('utf-8')).decode('utf-8')

    print("Output data file:", params["file_name"])
    
    
par = {
    "num_buffers": 10,
    "file_name": "./data/list_mode_xt2k_10.dat",
    "xt_number": 2, # 1,2,3, or 4: Choose one of four trace buffers; 0 selects the 28K trace
    "ctrl_C": 100,
    "ctrl_N": 1,
    "ctrl_M": 2
}
par["file_name"] = "./data/list_mode_xtr{}_10.dat".format(par["xt_number"])
acquire_xtrace(par)

