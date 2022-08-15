from __future__ import division
import time
import json
import ctypes
import platform
import sys
import array

"""
Simulator of an eMorpho MCA.

"""

with open("../rad_config/sim/sim_config.json", 'r') as fin:
    cfg_json = fin.read()
cfg = json.loads(cfg_json)

# Figure out what platform we are running on and choose the appropriate libusb shared object or dll
machine = platform.machine()
plat = sys.platform
print("Platform and machine", plat, machine)

if sys.platform.startswith('linux2') and machine == 'armv7l':  # BPI's MDC
    emorpho_sim_selected = "emorpho_sim_arm32.so"  # Use this for linux on a 32-bit BPI MDC
elif sys.platform.startswith('linux'):
    if machine == 'armv7l':
        emorpho_sim_selected = "emorpho_sim_arm32.so"  # Use this for linux on a 32-bit Raspberry Pi
    if machine == 'x86_64':
        emorpho_sim_selected = "emorpho_sim_64.so"  # Use this for linux 64-bit on Intel
    if machine == 'x86':
        emorpho_sim_selected = "emorpho_sim_x86.so"  # Use this for linux 32-bit on Intel
elif sys.platform.startswith('win'):  # Win 32-bit or 64-bit
    if machine == 'x86_64' or machine=="AMD64":
        emorpho_sim_selected = "emorpho_sim_64.dll"  # Use this for Windows 64-bit on Intel
    if machine == 'x86':
        emorpho_sim_selected = "emorpho_sim_x86.dll"  # Use this for Windows 32-bit on Intel

emorpho_sim_lib = cfg["lib_path"]+emorpho_sim_selected  
# emorpho_sim_lib = cfg["lib_path"]+"emorpho_sim_64.dll"  # Use this to hard code a path
# ctypes.cdll.LoadLibrary(emorpho_sim_selected)
emorpho_sim = ctypes.CDLL(emorpho_sim_lib)
emorpho_sim.simulate.restype = ctypes.c_int
emorpho_sim.simulate.argtypes = [ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_double),
                                 ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]


class mca:
    def __init__(self):
        
        self._com = array.array('I', [0]*16)  # array of uint16_t parameters
        self._com_p = ctypes.cast(self._com.buffer_info()[0], ctypes.POINTER(ctypes.c_uint))
        self._host_out = array.array('d', [0]*1024)  # array of double parameters
        self._host_out_p = ctypes.cast(self._host_out.buffer_info()[0], ctypes.POINTER(ctypes.c_double))
        self._host_in = array.array('d', [0]*4096)  # array of double parameters
        self._host_in_p = ctypes.cast(self._host_in.buffer_info()[0], ctypes.POINTER(ctypes.c_double))
        self._debug = array.array('d', [0]*16)  # array of 'double' parameters
        self._debug_p = ctypes.cast(self._debug.buffer_info()[0], ctypes.POINTER(ctypes.c_double))
    
        self.sn = "eRC0001"
        
        self.cmd = {}  # The command is a user-supplied dictionary
        self.cmd_out_list = []
        self.data_in_list = []
        self.data_in_dict = {}
        self.data_out_list = []
        self.data_out_dict = {}
        self.adc_sr = 40e6
        self.start_up_time = time.time()
        
    def update(self):
        emorpho_sim.simulate(self._com_p, self._host_out_p, self._host_in_p, self._debug_p)
        # print(self._debug[0], self._debug[1], self._debug[2])      


class bpi_usb:
    """Unified interface to all Morpho devices that use an FTDI USB interface"""
    def __init__(self):
        self.num_morphos = 0

    def scan_all(self):
        """Scans for morphos and count them; Does not open a Morpho."""
        self.num_morphos = 1
        return 1

    def find_all(self):
        self.scan_all()

        mca_dict = dict()
        for n in range(self.num_morphos):
            ser_num = "eRC{:04d}".format(n) 
            
            mca_dict[ser_num] = mca()
            mca_dict[ser_num].sn = ser_num

        return mca_dict

    # close all open devices
    def close_all(self):
        return 0


