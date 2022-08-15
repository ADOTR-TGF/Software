#!/usr/bin/python
#
import time
import json
import sys

sys.path.append("../../")  # Add the path to bridgeport_mca
import bridgeport_mca
import bridgeport_mca.mca_portal
import bridgeport_mca.mca_daq

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

def acquire_split_histograms(dwell_time, lun=0, num_records=1):
    """
    We assume that only one eMorpho or MCA-3000 is attached, and that the MCA Data server is running.

    This example demonstrates loss-less histogram acquisition using the built-in
    split-histogram mode.  Statistics counters and histogram data appear in two
    equal-sized banks (2Kx32 for the histogram).  While the FPGA on the MCA
    is acquiring data into one bank, the client can read and then clear the inactive
    bank at leisure.

    The data file will consist one json string per line.

    :param dwell_time: Acquisition time in seconds before switching to the other bank
    :param lun: Logic unit number or serial number
    :param num_records: Maximum number of records to write to file.
    :return: None
    """

    MCA_IO = bridgeport_mca.mca_portal.MCA_PORTAL()  # For communication with the MDS
    # Print serial numbers of attached MCA
    print("List of attached devices:", MCA_IO.sn_list)
    DAQ = bridgeport_mca.mca_daq.MCA_DAQ(MCA_IO)
    par = {}
    par["lun_sn"] = lun
    par["mode"] = "rate_histogram"
    par["items"] = ["fields", "user"]
    par["prefix"] = "histogram_2b"  # File name prefix, or full file name
    par["comment"] = ""

    # Prepare two-bank histogram acquisition (Note: run=0)
    MCA_IO.submit_command(lun, "prepare_split")
    # Start two-bank histogram acquisition (Note: segment_enable=1)
    MCA_IO.submit_command(lun, "start_bank_0")

    segment = 0
    bank_cmd = ["start_bank_0", "start_bank_1"]

    for n in range(num_records):
        time.sleep(dwell_time)
        bank = banks[segment]
        offset = offsets[segment]

        # Switch the active segment
        segment = 1 if segment==0 else 0
        MCA_IO.submit_command(lun, bank_cmd[segment])

        # Read data and save
        DAQ.save_histogram(par)

        # Clear inactive segment by setting clear_statistics and clear_histogram
        MCA_IO.submit_command(lun, "start_mca")


acquire_split_histograms(dwell_time=1.0, lun=0, num_records=5)
