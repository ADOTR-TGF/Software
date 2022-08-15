import json
import time
import zmq
import communication as com


def test_nv_mem(trigger_delay=200):
    """
    We assume that only one eMorpho is attached, and that the eMorpho_server is running.
    To test communication with the non-volatile memory, perform these steps:

    We'll seek to change the trigger_delay parameter, which determines where in a recorded trace the 
    rising edge of the pulse will be.  The default value often is trigger_delay = 100
    
    Step 1: Run test_nvm(200).  It will change the trigger_delay value in nv-mem from what it was
    before to 200 thereafter.
    
    Step 2: Disconnect the eMorpho and make sure it is powered down.
    
    Step 3: Reconnect the eMorpho to the computer
    
    Step 4: Run test_nvm(200).  It should print first
        Trigger delay, before = 200
        
        followed by
        
        Trigger delay, before = 100

    :param trigger_delay: A parameter to change in nv-mem
    :return None
    
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

    # Read non-volatile memory
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "read", "memory": "flash", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    print("Trigger delay, before = ", ret[sn]["fields"]["trigger_delay"])
    
    # Read-modify-write to fpga_ctrl
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"trigger_delay": trigger_delay}}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    print("Trigger delay, in fpga = ", ret[sn]["fields"]["trigger_delay"])

    # A write command demands a register list; fields and user is not used.
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "write", "memory": "flash", "sn": sn,
           "data": { "registers": ret[sn]["registers"]}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)

    # Read non-volatile memory
    cmd = {"type": "mca_cmd", "name": "fpga_ctrl", "dir": "read", "memory": "flash", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    print("Trigger delay, after = ", ret[sn]["fields"]["trigger_delay"])



test_nv_mem(100)

