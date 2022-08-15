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

    How to use mode when saving data:
    mode="all": save listmode, count rates and all instrument controls and status
    mode="status_listmode": save list mode and status data
    mode="listmode": save listmode data only

    How to use items when saving data:
    items = ["registers", "fields", "user"], or a shorter list
    items = ["fields", "user"] is the preferred default
    items = ["registers", "fields", "user"] adds raw register data to the file

"""

def listmode_daq(num_buffers, lun=0):
    """
    We assume that only one MCA is attached, and that the MCA Data Server is running.
    Use the graphical user interface to adjust the instrument parameters,
    including the choice of list mode type.

    :param num_buffers: Number of pulses to acquire
    :param lun: Logic unit number or serial number
    :return: None
    """
    MCA_IO = bridgeport_mca.mca_portal.MCA_PORTAL()  # For communication with the MDS
    # Print serial numbers of attached MCA
    print("List of attached devices:", MCA_IO.sn_list)
    DAQ = bridgeport_mca.mca_daq.MCA_DAQ(MCA_IO)  # Convenience class for storing data
    par = {
        "lun_sn": lun,
        "mode": "status_listmode",
        "items": ["fields", "user"],
        "prefix": "listmode",  # File name prefix, or full file name ending in .json
        "comment"] = ""
    }

    for n in range(num_buffers):
        MCA_IO.submit_command(sn, "start_listmode")
        while True:
            res = MCA_IO.submit_command(sn, "fpga_results")
            if res[sn]["user"]["lm_done"]:
                # Read listmode data and save
                DAQ.save_listmode(par)
                break



listmode_daq(num_buffers, lun=0)
