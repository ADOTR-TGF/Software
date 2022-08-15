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

def acquire_background_and_sample(bck_time, sample_time, lun=0):
    """
        Prepare the detector for the measurement,
        Enter Y when prompted.
        Wait until the background measurement has finished.
        Then add your sample and and enter Y at the prompt
        Wait until the sample measurement has finished.
        In the data folder you will find a file with three
        consecutive entries:
        background histogram
        sample histogram
        sample-background histogram

        Note: background and sample measurement times can be different.
        They can be programmed into the instrument.  In this example,
        we let this program control the measurement time.

    :param bck_time: Acquisition time in seconds for the background
    :param sample_time: Acquisition time in seconds for the sample measurement
    :param lun: Logic unit number or serial number
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
    par["prefix"] = "histogram"  # File name prefix, or full file name
    par["comment"] = ""

    while True:
        answer = input("Ready for background measurement? ")
        answer = answer.strip().lower()
        if answer in ["y", "yes" ]:
            break
    # Start sample measurement
    MCA_IO.submit_command(lun, "start_mca", data={"user":{"active_bank": 1}})
    then = time.time()
    time.sleep(bck_time)
    DAQ.save_background(par)
    print("Background measurement has been completed.")

    while True:

        while True:
            answer = input("Ready for sample measurement? ")
            answer = answer.strip().lower()
            if answer in ["y", "yes" ]:
                break

        # Start background measurement
        MCA_IO.submit_command(lun, "start_mca", data={"user":{"active_bank": 0}})
        then = time.time()
        time.sleep(sample_time)
        DAQ.save_histogram(par)  # Save sample histogram
        DAQ.save_difference(par) # Save ample-background (computed by MCA)
        print("Sample measurement has been completed.")

        while True:
            answer = input("Do another sample measurement? ")
            answer = answer.strip().lower()
            if answer in ["y", "yes", "n", "no" ]:
                break
        if answer in ["n", "no" ]:
            break

acquire_background_and_sample(bck_time, sample_time, lun=0)
