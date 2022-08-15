#!/usr/bin/python
#
import time
import json
import sys

sys.path.append("../../")  # Add the path to bridgeport_mca
import bridgeport_mca
import bridgeport_mca.mca_portal
import bridgeport_mca.mca_daq

version = 1.0

"""
    You can find all the commands in bridgeport_mca/commands/

    How to use lun:
    lun=None: all attached devices
    lun=0: only first attached device
    lun=[1,3]: only 2nd and 4th attached device
    If you have only one device attached

    How to use dwell_time:
    It is the histogram data acquisition time in seconds.

    How to use mode in save_histogram:
    mode="all": save histogram, count rates and all instrument controls and status
    mode="rates_histogram": save histogram and count rates
    mode="histogram": save histogram

    How to use items in save_histogram:
    items = ["registers", "fields", "user"], or a shorter list
    For eMorpho the histograms are reported in "registers"
    For all other MCA, histograms are also reported in "fields".

    HistogramDAQ.save_histogram automatically saves registers for the eMorpho histogram
    =>
    Use items = ["fields", "user"] saves only useful data from fields and user.
        This is the most practical setting.

    Use items = ["registers", "fields", "user"] adds raw register data to the file

"""

def high_count_rate_pulses(num_pulses, lun=0):
    """
    We assume that only one MCA is attached, and that the MCA Data Server is running.
    When the count rate is beyond 1kcps, pulses arrive so quickly, we can just wait 10ms 
    after the start_pulse command and read the pulse from the MCA.

    :param num_pulses: Number of pulses to acquire
    :param lun: Logic unit number or serial number
    :return: None
    """
    MCA_IO = bridgeport_mca.mca_portal.MCA_PORTAL()  # For communication with the MDS
    # Print serial numbers of attached MCA
    print("List of attached devices:", MCA_IO.sn_list)
    DAQ = bridgeport_mca.mca_daq.MCA_DAQ(MCA_IO)  # Convenience class for storing data
    par = {}
    par["lun_sn"] = lun
    par["mode"] = "status_pulse"
    par["items"] = ["fields", "user"]
    par["prefix"] = "pulses"  # File name prefix, or full file name
    par["comment"] = ""

    for n in range(num_pulses):
        MCA_IO.submit_command(lun, "start_pulse")
        time.sleep(0.02)  # wait

        # Read pulse and save
        DAQ.save_pulse(par)
        
        
def low_count_rate_pulses(num_pulses, lun=0):
    """
    We assume that only one MCA is attached, and that the MCA Data Server is running.
    At low count rate, we must check the MCA status registers to see if a pulse has 
    been captured.
    In this example, lun should select a single device, not an array of devices.

    :param num_pulses: Number of pulses to acquire
    :param lun: Logic unit number or serial number
    :return: None
    """
    MCA_IO = bridgeport_mca.mca_portal.MCA_PORTAL()  # For communication with the MDS
    # Print serial numbers of attached MCA
    print("List of attached devices:", MCA_IO.sn_list)
    DAQ = bridgeport_mca.mca_daq.MCA_DAQ(MCA_IO)  # Convenience class for storing data
    par = {}
    par["lun_sn"] = lun
    par["mode"] = "status_pulse"
    par["items"] = ["fields", "user"]
    par["prefix"] = "pulses"  # File name prefix, or full file name
    par["comment"] = ""
    
    if type(lun)==str:
        sn = lun
    else:
        sn = MCA_IO.sn_list[lun]

    for n in range(num_pulses):
        MCA_IO.submit_command(sn, "start_pulse")
        while True:
            res = MCA_IO.submit_command(sn, "fpga_results")
            if res[sn]["user"]["trace_done"]:
                # Read pulse and save
                DAQ.save_pulse(par)
                break  

        
#high_count_rate_pulses(num_pulses=10, lun=0)
low_count_rate_pulses(num_pulses=10, lun=0)
