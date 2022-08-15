import json
import time
import ftdi as bpi_device
import eMorpho_api as api


def acquire_time_slice(num_slices, file_name):
    """
    We assume that only one eMorpho is attached, and that the eMorpho_server is running.
    Check the results registers for availability of a new time slice.  When that is the case, read the data buffer
    and store as one json object in file.

    :param num_slices: Number of time slices to be acquired
    :param file_name: Write the time slices to file
    :return:
    """

    all_mca = bpi_device.bpi_usb().find_all()  # Dictionary of attached eMorphos, with SN as key.
    sn_list = [sn for sn in all_mca]
    print('Attached eMorpho:', sn_list)
    sn = sn_list[0]  # We will use just one eMorpho in this example
    
    # Boot from non-volatile memory
    boot_from_nvmem(all_mca, sn)

    # Program FPGA controls to reset the statistics counters and the time_slice machinery.
    cmd = {"type": "em_cmd", "name": "fpga_ctrl", "dir": "rmw", "sn": sn,
           "data": {"fields": {"clear_statistics": 1, "clear_histogram": 1, "run": 1}}}
    api.process_cmd(cmd, all_mca)

    status_cmd = {"type": "em_cmd", "name": "fpga_results", "dir": "read", "sn": sn}
    slice_cmd = {"type": "em_cmd", "name": "fpga_time_slice", "dir": "read", "sn": sn}
    buffer_number = 0
    for slice_number in range(num_slices):
        while True:  # Poll until one or more time slices are available
            ret = api.process_cmd(status_cmd, all_mca)
            num_buffers = (ret[sn]["fields"]["status"] >> 3) & 0x1F  # Number of 105ms time slices that are available
            if num_buffers > 0:
                break
        # Read slice data
        for n in range(num_buffers):
            ret = api.process_cmd(slice_cmd, all_mca)
            slice_data = ret[sn]['fields']
            if slice_data['buffer_number'] == buffer_number:  # incomplete buffer
                continue
            
            with open(file_name, 'a') as fout:
                fout.write(json.dumps(slice_data) + "\n")


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
    
    
acquire_time_slice(num_slices=10, file_name="time_slices.dat")
