#!/usr/bin/python
#
import time
import json
import sys

sys.path.append("../../")  # Add the path to bridgeport_mca
import bridgeport_mca
import bridgeport_mca.mca_portal
import bridgeport_mca.mca_daq
import bridgeport_mca.histogram_analysis

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

def scan_ov_histograms(ctrl):
    """
    We assume that only one MCA is attached, and that the MCA Data Server is running.
    This code serves all MCA-1000, MCA-2000, MCA-3000 devices

    :param ctrl["dwell_time"]: Acquisition time in seconds
    :param ctrl["ov_min"]:     Minimum operating voltage
    :param ctrl["ov_max"]:     Maximum operating voltage
    :param ctrl["num_steps"]:  Number of steps
    :param ctrl["file_name"]:  Name of the output data file
    :param ctrl["lun"]:        Logic unit number or serial number
    :return: None
    """
    MCA_IO = bridgeport_mca.mca_portal.MCA_PORTAL()  # For communication with the MDS
    # Print serial numbers of attached MCA
    print("List of attached devices:", MCA_IO.sn_list)
    then = time.time()
    DAQ = bridgeport_mca.mca_daq.MCA_DAQ(MCA_IO)
    time.sleep(0.1)
    
    dov = (ctrl["ov_max"] - ctrl["ov_min"])/num_steps  # Step size
    
    save_par = {}
    save_par["lun_sn"] = ctrl["lun"]
    save_par["mode"] = "rate_histogram"
    save_par["items"] = ["fields", "user"]
    save_par["prefix"] = "histogram"  # File name prefix, or full file name
    save_par["comment"] = ""
    
    for n in ctrl["num_steps"]:
        ov = ctrl["ov_min"] + n*dov
        MCA_IO.submit_command(ctrl["lun"], "write_arm_ctrl", data = {"fields":{"cal_ov": ov}})
        time.sleep(1)
        
        MCA_IO.submit_command(ctrl["lun"], "start_mca")
        time.sleep(ctrl["dwell_time"])  # wait
        if ctrl["save_histograms"]:
            DAQ.save_histogram(par)
        histo = MCA_IO.submit_command(ctrl["lun"], "histogram")
        
        # analysis
        off = 100  # Ignore the potentially tall K-alpha peak at 37keV
        histo_max = max(histo[off:]) 
        idx_max = histo[off:].index(histo_max) + off
        imin = int(idx_max-50)
        imax = int(idx_max+60)
        res = bridgeport_mca.histogram_analysis.do_gauss_fit(histo[imin: imax+1], bck_model=2, fwhm=25)
        peak = res["x_max"]+imin
        
        # Create and store output data, one line at a time
        results = {"ov": ov, "peak": peak}
        with open(par["file_name"], 'a') as fout:
            fout.write(json.dumps(results) + "\n")



ctrl = {
    "dwell_time": 1,  # Time between histogram reads
    "max_time": 10,   # Total acquisition time
    "lun": 0,
    "save_histograms": False
}

scan_ov_histograms(ctrl)

