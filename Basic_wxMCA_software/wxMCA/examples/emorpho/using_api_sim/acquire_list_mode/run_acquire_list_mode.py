import json
import time
import sim_emorpho as bpi_device
import eMorpho_api as api


def acquire_list_mode(lm_mode, num_buffers, file_name):
    """
    We assume that only one eMorpho is attached, and that the MCA Data Server is running.
    Program FPGA control registers to set the list_mode acquisition mode.  Then check the eMorpho if the
    list_mode acquisition has finished.  When that is the case, read the data buffer
    and store as one json object in file.

    :param lm_mode: Type of list mode: 0 or 1, cf MDS documentation
    :param num_buffers: Number of traces to be acquired
    :param file_name: Write the histogram to this file as one long line
    :return:
    """

    all_mca = bpi_device.bpi_usb().find_all()  # Dictionary of attached eMorphos, with SN as key.
    sn_list = [sn for sn in all_mca]
    print('Attached eMorpho:', sn_list)
    sn = sn_list[0]  # We will use just one eMorpho in this example
    
    # Boot from non-volatile memory
    boot_from_nvmem(all_mca, sn)

    # Program FPGA controls to set the list-mode acquisition mode;
    cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"lm_mode": lm_mode}}}
    api.process_cmd(cmd, all_mca)

    for buffer_num in range(num_buffers):
        # Start the list-mode run
        cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
               "data": {"fields": {"clear_statistics": 1, "clear_list_mode": 1, "lm_run": 1, "run": 1}}}
        api.process_cmd(cmd, all_mca)

        while True:  # Poll until list-mode acquisition has finished
            cmd = {"type": "em_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
            ret = api.process_cmd(cmd, all_mca)
            if ret[sn]["user"]["lm_done"] == 1:
                break

        # Read list-mode data
        cmd = {"type": "em_cmd", "name": "fpga_list_mode", "dir": "read", "sn": sn}
        ret = api.process_cmd(cmd, all_mca)
        lm_data = ret[sn]['user']
        with open(file_name, 'a') as fout:
            fout.write(json.dumps(lm_data) + "\n")
            
    print("Output data file:", file_name)


def boot_from_nvmem(all_mca, sn):
    """
    Load the FPGA control registers from the content of the non-volatile memory and 
    turn on the high voltage.

    :param all_mca: A dictionary of mca objects, and the keys are their serial numbers
    :param sn: The serial number
    :return: None
    """

    # Load ADC sampling rate
    cmd = {"type": "em_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
    ret = api.process_cmd(cmd, all_mca)
    adc_sr = ret[sn]['user']['adc_sr']
    all_mca[sn].adc_sr = adc_sr
    #  Read nv-mem
    cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "read", "memory": "flash", "sn": sn}
    ret = api.process_cmd(cmd, all_mca)
    # Load FPGA control registers and turn on HV.
    cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "write", "sn": sn,
           "data": {"registers": ret[sn]['registers']} }  # Writing registers does not automatically set program_hv=1
    api.process_cmd(cmd, all_mca)
    cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
               "data": {"fields": {"program_hv": 1}} }
    api.process_cmd(cmd, all_mca)
    time.sleep(2)  # Let the high voltage ramp up
    
    
lm_mode = 0
acquire_list_mode(lm_mode, num_buffers=1, file_name="./data/list_mode_{}.dat".format(lm_mode))

lm_mode = 1
acquire_list_mode(lm_mode, num_buffers=1, file_name="./data/list_mode_{}.dat".format(lm_mode))
