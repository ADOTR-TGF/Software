import json
import time
import ftdi as bpi_device
import eMorpho_api as api


def acquire_one_histogram(dwell_time, file_name):
    """
    We assume that only one eMorpho is attached, and that the MCA Data Server is running.

    :param dwell_time: Acquisition time in seconds
    :param file_name: Write the histogram to this file as one long line
    :return: None
    """

    all_mca = bpi_device.bpi_usb().find_all()  # Dictionary of attached eMorphos, with SN as key.
    sn_list = [sn for sn in all_mca]
    print('Attached eMorpho:', sn_list)
    sn = sn_list[0]  # We will use just one eMorpho in this example
    
    # Boot from non-volatile memory
    boot_from_nvmem(all_mca, sn)

    # Start a histogram run 
    cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"clear_histogram": 1, "clear_statistics": 1, "run": 1}}}
    ret = api.process_cmd(cmd, all_mca)

    time.sleep(dwell_time)  # wait

    # Read histogram data
    cmd = {"type": "em_cmd", "name": "fpga_histogram", "dir": "read", "sn": sn}
    ret = api.process_cmd(cmd, all_mca)
    histogram = ret[sn]['registers']

    with open(file_name, 'a') as fout:
        fout.write(json.dumps(histogram) + "\n")
        
    print("Output data file:", file_name)


def acquire_one_histogram_2(dwell_time, file_name):
    """
    We assume that only one eMorpho is attached, and that the eMorpho_server is running.
    Program FPGA control registers to stop counting events when the histogram has finished,
    and set the acquisition time to be dwell time.  Then check the eMorpho if the histogram
    acquisition has finished.  When that is the case, read histogram and count rates and store as one json object in file.

    :param dwell_time: Acquisition time in seconds
    :param file_name: Write the histogram to this file as one long line
    :return: None
    """

    all_mca = bpi_device.bpi_usb().find_all()  # Dictionary of attached eMorphos, with SN as key.
    sn_list = [sn for sn in all_mca]
    print('Attached eMorpho:', sn_list)
    sn = sn_list[0]  # We will use just one eMorpho in this example
    
    # Boot from non-volatile memory
    boot_from_nvmem(all_mca, sn)

    # Program FPGA controls; Note the mixed use of high-level 'user' data and lower-level 'fields' data.
    cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"daq_mode": 1, "rtlt": 2}, "user": {"run_time": dwell_time}}}
    api.process_cmd(cmd, all_mca)

    # Start the histogram run
    cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"clear_histogram": 1, "clear_statistics": 1, "run": 1}}}
    ret = api.process_cmd(cmd, all_mca)

    while True:  # Poll until histogram acquisition has finished
        time.sleep(1)  # wait 1s between polls
        cmd = {"type": "em_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
        ret = api.process_cmd(cmd, all_mca)  # ret is a dictionary with keys "registers", "fields", "user"
        if ret[sn]["user"]["histo_done"] == 1:
            break

    # Read histogram data
    cmd = {"type": "em_cmd", "name": "fpga_histogram", "dir": "read", "sn": sn}
    ret = api.process_cmd(cmd, all_mca)
    histogram = ret[sn]['registers']

    # Read count rate data
    cmd = {"type": "em_cmd", "name": "fpga_statistics", "dir": "read", "sn": sn}
    ret = api.process_cmd(cmd, all_mca)
    count_rates = ret[sn]["user"]["bank_0"]

    with open(file_name, 'a') as fout:
        out_dict = {"count_rates": count_rates, "histogram": histogram}
        fout.write(json.dumps(out_dict) + "\n")
        
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
    

# Run either one, but not both function calls below.

# acquire_one_histogram(dwell_time=10, file_name="./data/one_histo.dat")

acquire_one_histogram_2(dwell_time=10, file_name="./data/rates_histo.dat")
