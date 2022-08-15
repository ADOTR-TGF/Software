import json
import time
import ftdi as bpi_device
import eMorpho_api as api


def test_nv_mem(trigger_delay=200):
    """
    We assume that only one eMorpho is attached, and that the eMorpho_server is running.
    To test communication with the non-volatile memory, perform these steps:

    We'll seek to change the trigger_delay parameter, which determines where in a recorded trace the 
    rising edge of the pulse will be.  The default value often is trigger_delay = 100
    
    Step 1: Run test_nvm(200).  It will change the trigger_delay value in nv-mem 
    from what it was before, to 200 thereafter.
    
    Step 2: Disconnect the eMorpho and make sure it is powered down.
    
    Step 3: Reconnect the eMorpho to the computer
    
    Step 4: Run test_nvm(200).  It should print first
        Trigger delay, before = 200
        
        followed by
        
        Trigger delay, before = 100

    :param trigger_delay: A parameter to change in nv-mem
    :return None
    
    """

    all_mca = bpi_device.bpi_usb().find_all()  # Dictionary of attached eMorphos, with SN as key.
    sn_list = [sn for sn in all_mca]
    print('Attached eMorpho:', sn_list)
    sn = sn_list[0]  # We will use just one eMorpho in this example
    
    # Read non-volatile memory
    cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "read", "memory": "flash", "sn": sn}
    ret = api.process_cmd(cmd, all_mca)
    print("Trigger delay, before = ", ret[sn]["fields"]["trigger_delay"])
    
    # Read-modify-write to fpga_ctrl
    cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"trigger_delay": trigger_delay}}}
    ret = api.process_cmd(cmd, all_mca)
    print("Trigger delay, in fpga = ", ret[sn]["fields"]["trigger_delay"])

    # A write command demands a register list; fields and user is not used.
    cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "write", "memory": "flash", "sn": sn,
           "data": { "registers": ret[sn]["registers"]}}
    ret = api.process_cmd(cmd, all_mca)

    # Read non-volatile memory
    cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "read", "memory": "flash", "sn": sn}
    ret = api.process_cmd(cmd, all_mca)
    print("Trigger delay, after = ", ret[sn]["fields"]["trigger_delay"])


test_nv_mem(100)
