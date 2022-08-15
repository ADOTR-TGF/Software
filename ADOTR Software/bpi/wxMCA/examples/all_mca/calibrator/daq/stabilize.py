import os
import sys
import threading

sys.path.append("../../") # The module is at ../../bridgeport_mca
import bridgeport_mca
import bridgeport_mca.histogram_calibrator


def stabilize(idx, par_list):
    """
        The stabilize() function illustrates how to use the HistogramCalibrator class
        to provide gain stabilization for eMorpho MCA (usbBase, oemBase).
        
        It is a client to the MCA data server and operates one MCA. It should be used with
        eMorpho MCA.  All other Bridgeport MCA (MCA-1000, MCA-2000, and MCA-3000) have a 
        built-in ARM processor that can perform the gain stabilization without client-side support.

    """
    Cal_list = []
    if type(idx)==list:
        Cal_list = [bridgeport_mca.histogram_calibrator.HistogramCalibrator(k, par_list[k]) for k in idx]
    else:
        Cal_list += [bridgeport_mca.histogram_calibrator.HistogramCalibrator(idx, par_list[0])]

    thread_list = []
    for Cal in Cal_list:
        thread = threading.Thread(target=Cal.stabilizer_loop, args=())
        thread.start()
        thread_list += [thread]

    for thread in thread_list:
        thread.join()

par_0 = {
    "mode": "led", # 'ov', or 'led', Gain stabilization mode
    "dwell_time": 60, # Time between high_voltage updates, in seconds
    "cal_ov": 755.54, # Calibration voltage
    "cal_dg": 4997, # Calibration digital_gain
    "cal_led": 23500, # LED response at calibration time
    "cal_temperature": 28.15, # Calibration temperature
    "lut" : # Lookup table for operating voltage, digital_gain and LED brightness vs temperature
        {"tmin": -30.0, "dt": 5.0, "len": 20, 
         "ov": [1.042331, 1.038397, 1.034464, 1.030530, 1.026596, 1.022663, 1.018729, 1.014722, 1.010645, 1.006999, 
                1.003686, 1.000664, 0.997950, 0.995617, 0.993794, 0.992669, 0.992485, 0.993544, 0.994302, 0.994897], 
         "dg": [0.654072, 0.683588, 0.713104, 0.742619, 0.772135, 0.801651, 0.831167, 0.860151, 0.888431, 0.920357, 
                0.955921, 0.994833, 1.036520, 1.080130, 1.124525, 1.168290, 1.209725, 1.246849, 1.284958, 1.323679], 
         "led": [1.461962, 1.417449, 1.372937, 1.328424, 1.283912, 1.239400, 1.194887, 1.149162, 1.102291, 1.062513, 
                 1.027820, 0.996610, 0.967693, 0.940288, 0.914024, 0.888939, 0.865483, 0.844513, 0.822972, 0.801082], 
         "mode": 0,
         "comment": "R2D-NaI-2-LED, Detector: 2M2/2-X, measured between 9.7C and 58.4C, eRC4623, IT=48; ie 1.20us, N10L divider, 2021_11_02/histograms_eRC4623_energy.json"
        },
    "gain_exp" : 5.6, # PMT gain exponent; 8-dynode PMT=>5.6, 10-dynode PMT=>7.5
    "data_root": "../data/"
}

stabilize([0], [par_0])  # Stabilize first attached eMorpho MCA
