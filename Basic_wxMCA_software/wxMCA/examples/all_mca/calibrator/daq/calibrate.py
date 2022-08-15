import os
import sys
import threading
# Get include_path = ../../common as absolute path;
#include_path = os.getcwd().rsplit("/", 2)[0] # The module is at ../../bridgeport_mca
#print(include_path)
#sys.path.append(include_path)
sys.path.append("../../") # The module is at ../../bridgeport_mca

import bridgeport_mca
import bridgeport_mca.histogram_calibrator


def calibrate(idx, par):
    """
        The calibrate() function illustrates how to use the HistogramCalibrator class.
        It is a client to the MCA data server and operates one MCA. It works for any
        eMorpho, MCA-1000, MCA-2000, and MCA-3000.
        For eMorpho, MCA-2000, and MCA-3000, it is possible to also record pulses during
        the temperature cycle.
    """
    Cal_list = []
    if type(idx)==list:
        Cal_list = [bridgeport_mca.histogram_calibrator.HistogramCalibrator(k, par) for k in idx]
    else:
        Cal_list += [bridgeport_mca.histogram_calibrator.HistogramCalibrator(idx, par)]

    thread_list = []
    for Cal in Cal_list:
        thread = threading.Thread(target=Cal.calibrator_loop, args=())
        thread.start()
        thread_list += [thread]

    for thread in thread_list:
        thread.join()


par = {
    "sipm1k_keV_bin": 2.0,    # Desired MCA gain
    "sipm2k_keV_bin": 1.0,    # Desired MCA gain
    "sipm3k_keV_bin": 1.0,    # Desired MCA gain
    "pmt1k_keV_bin": 2.0,     # Desired MCA gain
    "pmt2k_keV_bin": 1.0,     # Desired MCA gain
    "pmt3k_keV_bin": 1.0,     # Desired MCA gain
    "emorpho_keV_bin": 1.0,   # Desired MCA gain
    "ph": 187.0,        # Pulse height in mV for calibration energy
    "keV": 661.66,      # Calibration energy in keV
    "update": 1,        # 1=> Store updated operating voltage, digital_gain, etc in MCA
    "gain_exp": 5.6,    # For PMT only: gain = K*HV**gain_exp
    "wait_time":   10,  # Time to wait before performing a new calibration
    "dwell_time":  20,  # Time to acquire fresh data for a calibration step
    "max_time": 240,    # 7*24*3600,  # Maximum time to run and save data; in seconds
    "num_pulses":   0,  # Number of pulses to record; Set to 0 to skip this step
    "pulse_skips": 10,  # Record pulses only every pulse-skips rounds
    "data_root": "../data/"
}
"""
    For a quick calibration in the laboratory use count rates of ~3kcps to 10kcps,
    wait_time=1, dwell_time=10 and max_time = 60.
    For a continuing precise calibration, eg during a long temperature cycle, use
    wait_time=60, dwell_time=60 and max_time=7*24*3600.
    
"""
calibrate([0], par)
