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
    mode="rate_histogram": save histogram and count rates
    mode="histogram": save histogram

    How to use items when saving data:
    items = ["registers", "fields", "user"], or a shorter list
    For eMorpho the histograms are reported in "registers"
    For all other MCA, histograms are also reported in "fields".

    DAQ.save_histogram automatically saves registers for the eMorpho histogram
    =>
    Use items = ["fields", "user"] saves only useful data from fields and user.
        This is the most practical setting.

    Use items = ["registers", "fields", "user"] adds raw register data to the file

"""

def acquire_histograms(ctrl):
    """
    We assume that only one MCA is attached, and that the MCA Data Server is running.

    :param ctrl["dwell_time"]: Acquisition time in seconds
    :param ctrl["max_time"]:   Total acquisition time
    :param ctrl["lun"]:        Logic unit number or serial number
    :return: None
    """
    MCA_IO = bridgeport_mca.mca_portal.MCA_PORTAL()  # For communication with the MDS
    # Print serial numbers of attached MCA
    print("List of attached devices:", MCA_IO.sn_list)
    then = time.time()
    DAQ = bridgeport_mca.mca_daq.MCA_DAQ(MCA_IO)
    time.sleep(0.1)
    
    while time.time()-then < ctrl["max_time"]:
        MCA_IO.submit_command(ctrl["lun"], "start_mca")

        time.sleep(ctrl["dwell_time"])  # wait

        # Read count rate and histogram data
        par = {}
        par["lun_sn"] = ctrl["lun"]
        par["mode"] = "rate_histogram"
        par["items"] = ["fields", "user"]
        par["prefix"] = "histogram"  # File name prefix, or full file name
        par["comment"] = ""
        DAQ.save_histogram(par)
        

def read_and_clear_histograms(ctrl):
    """
    We assume that only one MCA-1000 is attached, and that the MCA Data Server is running.
    Note: Read and Clear is implemented only for the MCA-1000.  In that mode, the 
    histogram and statistics are cleared automatically after reading a spectrum.

    :param ctrl["dwell_time"]: Acquisition time in seconds
    :param ctrl["max_time"]:   Total acquisition time
    :param ctrl["lun"]:        Logic unit number or serial number
    :return: None
    """
    MCA_IO = bridgeport_mca.mca_portal.MCA_PORTAL()  # For communication with the MDS
    # Print serial numbers of attached MCA
    print("List of attached devices:", MCA_IO.sn_list)
    then = time.time()
    DAQ = bridgeport_mca.mca_daq.MCA_DAQ(MCA_IO)
    MCA_IO.submit_command(ctrl["lun"], "start_mca", data={"fields": {"run_time_sample": 0}, "user":{"read_clear": 1}})
    
    while time.time()-then < ctrl["max_time"]:
        time.sleep(ctrl["dwell_time"])  # wait

        # Read count rate and histogram data
        
        par = {}
        par["lun_sn"] = ctrl["lun"]
        par["mode"] = "rate_histogram"
        par["items"] = ["fields", "user"]
        par["prefix"] = "histogram"  # File name prefix, or full file name
        par["comment"] = ""
        DAQ.save_histogram(par)
        

ctrl = {
    "dwell_time": 1,  # Time between histogram reads
    "max_time": 10,   # Total acquisition time
    "lun": 0
}

acquire_histograms(ctrl)

# read_and_clear_histograms(ctrl)
