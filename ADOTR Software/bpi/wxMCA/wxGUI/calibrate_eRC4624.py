import time
import wx
import os
import json
import mca_io
import histo_analysis
import histo_calibrator

   
def calibrate(sn="eRC4624"):
    """
        The calibrate() function illustrates how to use the HistogramCalibrator class.
        It is a client to the MCA data server and operates one MCA. It works for any 
        eMorpho, MCA-1000, and MCA-3000.
        For eMorpho and MCA-3000, it is possible to also record pulses during
        the temperature cycle.        
    """
    Cal = histo_calibrator.HistogramCalibrator(sn)
    par = {
        "wait_time":   60,  # Time to wait before performing a new calibration
        "dwell_time":  60,  # Time to acquire fresh data for a calibration step
        "num_pulses":   0,  # Number of pulses to record; Set to 0 to skip this step
        "pulse_skips": 10   # Record pulses only every pulse-skips rounds
    }
    
    pulse_skipper = par["pulse_skips"]
    if Cal.mca_id in [Cal.PMT1K, Cal.SIPM1K]:
        while True:       
            time.sleep(par["wait_time"])
            Cal.MCA_IO.submit_command(Cal.sn, Cal.commands["start_mca"])  # Start new histogram
            time.sleep(par["dwell_time"])
            Cal.cal_mca()
            # Record results
            Cal.MCA_IO.submit_command(Cal.sn, Cal.commands["start_mca"])  # Start new histogram
            time.sleep(par["dwell_time"])
            Cal.refresh()
            Cal.save_histogram()
            
    if Cal.mca_id in [Cal.EMORPHO, Cal.PMT3K, Cal.SIPM3K]:
        if Cal.mca_id == Cal.EMORPHO:
            cmd_histo_amplitude = {"name": "fpga_ctrl",  "dir": "rmw", "data": {"fields": {"ha_run": 1}, "user":{}}}
            cmd_histo_energy = {"name": "fpga_ctrl",  "dir": "rmw", "data": {"fields": {"ha_run": 0}, "user":{}}}
        if Cal.mca_id in [Cal.PMT3K, Cal.SIPM3K]:
            cmd_histo_amplitude = {"name": "fpga_ctrl",  "dir": "rmw", "data": {"fields": {"ha_mode": 1}, "user":{}}}
            cmd_histo_energy = {"name": "fpga_ctrl",  "dir": "rmw", "data": {"fields": {"ha_mode": 0}, "user":{}}}
        while True:
            # First adjust operating voltage to keep the pulse height constant
            time.sleep(par["wait_time"])
            Cal.MCA_IO.submit_command(Cal.sn, cmd_histo_amplitude)  # Prepare for amplitude measurement
            Cal.MCA_IO.submit_command(Cal.sn, Cal.commands["start_mca"])  # Start new histogram
            time.sleep(par["dwell_time"])
            Cal.cal_mca()
            # Record results
            Cal.MCA_IO.submit_command(Cal.sn, Cal.commands["start_mca"])  # Start new histogram
            time.sleep(par["dwell_time"])
            Cal.refresh()
            Cal.save_histogram()
            
            # Now adjust digital gain to keep the keV/MCA_bin calibration constant
            time.sleep(par["wait_time"])
            Cal.MCA_IO.submit_command(Cal.sn, cmd_histo_energy)  # Prepare for amplitude measurement
            Cal.MCA_IO.submit_command(Cal.sn, Cal.commands["start_mca"])  # Start new histogram
            time.sleep(par["dwell_time"])
            Cal.cal_mca()
            # Record results
            Cal.MCA_IO.submit_command(Cal.sn, Cal.commands["start_mca"])  # Start new histogram
            time.sleep(par["dwell_time"])
            Cal.refresh()
            Cal.save_histogram()
            
            # Record pulses
            pulse_skipper += 1
            if par["num_pulses"]>0 and pulse_skipper >= par["pulse_skips"]:
                pulse_skipper = 0
                Cal.save_pulses(par["num_pulses"])
        
calibrate(sn="eRC4624")        
    

    
    
