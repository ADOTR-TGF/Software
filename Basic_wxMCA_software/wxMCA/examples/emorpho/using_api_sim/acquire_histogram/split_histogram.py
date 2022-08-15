import json
import time
import ftdi as bpi_device
import eMorpho_api as api


def acquire_split_histograms(dwell_time, num_records, file_name):
    """
    We assume that only one eMorpho is attached, and that the eMorpho_server is running.
    
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
    """

    all_mca = bpi_device.bpi_usb().find_all()  # Dictionary of attached eMorphos, with SN as key.
    sn_list = [sn for sn in all_mca]
    print('Attached eMorpho:', sn_list)
    sn = sn_list[0]  # We will use just one eMorpho in this example
    
    # Boot from non-volatile memory
    boot_from_nvmem(all_mca, sn)
    
    # Prepare two-bank histogram acquisition (Note: run=0)
    cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"segment_enable": 0, "segment": 0, 
                               "clear_histogram": 1, "clear_statistics": 1, "run": 0}}}
    api.process_cmd(cmd, all_mca)
    
    # Start two-bank histogram acquisition (Note: segment_enable=1)
    cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"segment_enable": 1, "segment": 0, "run": 1}}}
    api.process_cmd(cmd, all_mca)
    segment = 0
    banks = ["bank_0", "bank_1"]
    offsets = [0, 2048]

    for n in range(num_records):
        time.sleep(dwell_time)
        bank = banks[segment]
        offset = offsets[segment]
        
        # Switch the active segment
        segment = 1 if segment==0 else 0
        cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
               "data": {"fields": {"segment": segment}}}
        api.process_cmd(cmd, all_mca)
        
        # Read count rates
        cmd = {"type": "em_cmd", "name": "fpga_statistics", "dir": "read", "sn": sn}
        ret_rates = api.process_cmd(cmd, all_mca)
        rates = ret_rates[sn]["user"][bank]
              
        # Read histogram bank
        cmd = {"type": "em_cmd", "name": "fpga_histogram", "dir": "read", "sn": sn, "num_items": 2048, "offset": offset}
        ret_histo = api.process_cmd(cmd, all_mca)
        histogram = ret_histo[sn]['registers']
        
        # Clear inactive segment
        cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
               "data": {"fields": {"clear_histogram": 1, "clear_statistics": 1}}}
        api.process_cmd(cmd, all_mca)
        
        out_dict = {"rates": rates, "histogram": histogram}
        with open(file_name, 'a') as fout:
            fout.write(json.dumps(out_dict) + "\n")


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

acquire_split_histograms(dwell_time=1.0, num_records=10, file_name="split_histo.dat")
