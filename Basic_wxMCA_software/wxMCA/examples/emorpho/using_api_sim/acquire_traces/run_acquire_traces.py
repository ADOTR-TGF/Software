import json
import time
import sim_emorpho as bpi_device
import eMorpho_api as api


def acquire_traces(num_traces, file_name):
    """
    We assume that only one eMorpho is attached, and that the MCA Data Server is running.
    Program FPGA control registers to set the trace acquisition mode.  Then check the eMorpho if the trace
    acquisition has finished.  When that is the case, read the trace and store as one json object in file.

    :param num_traces: Number of traces to be acquired
    :param file_name: Write the histogram to this file as one long line
    :return:
    """

    all_mca = bpi_device.bpi_usb().find_all()  # Dictionary of attached eMorphos, with SN as key.
    sn_list = [sn for sn in all_mca]
    print('Attached eMorpho:', sn_list)
    sn = sn_list[0]  # We will use just one eMorpho in this example
    
    # Boot from non-volatile memory
    boot_from_nvmem(all_mca, sn)

    # Program FPGA controls to set the trace acquisition mode;
    cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"tr_mode": 0}}}
    api.process_cmd(cmd, all_mca)

    for trace_num in range(num_traces):
        # Start the trace run
        cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
               "data": {"fields": {"clear_trace": 1, "trace_run": 1, "vt_run": 0, "run": 1}}}
        api.process_cmd(cmd, all_mca)

        while True:  # Poll until trace acquisition has finished
            cmd = {"type": "em_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
            ret = api.process_cmd(cmd, all_mca)  # ret is a dictionary with keys "registers", "fields", "user"
            if ret[sn]["user"]["trace_done"] == 1:
                break

        # Read trace data and write to file
        cmd = {"type": "em_cmd", "name": "fpga_trace", "dir": "read", "sn": sn}
        ret = api.process_cmd(cmd, all_mca)  # ret is a dictionary with keys "registers", "fields", "user"
        trace = ret[sn]['fields']['trace'] 
        with open(file_name, 'a') as fout:
            fout.write(json.dumps(trace) + "\n") 

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
            
acquire_traces(num_traces=10, file_name="./data/traces.dat")
