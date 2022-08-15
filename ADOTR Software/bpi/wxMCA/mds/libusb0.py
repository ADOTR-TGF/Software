from __future__ import division
import os
import time
import ctypes as CT
import array
import sys
import platform
import struct
import json
"""
Bare-metal interface to the FTDI FT245 USB controller on the eMorpho MCA and to the generic CDC USB interface on the PMT/SiPM-1K/3K, PMT/SIPM-N3K.
We use ctypes to make the connection between python variables and C-variables of libusb0.1.


"""

# print(sys.version_info)

LIBUSB_HAS_GET_DRIVER_NP = sys.platform.startswith('linux')

USE_WIN32 = sys.platform.startswith('win32')  # returns TRUE or FALSE

# Figure out what platform we are running on and choose the appropriate libusb shared object or dll
machine = platform.machine()
_PATH_MAX = 511  # maximum file path name length
if sys.platform.startswith('linux2') and machine == 'armv7l':  # BPI's MDC
    _PATH_MAX = 4096
elif sys.platform.startswith('linux'):
    _PATH_MAX = 4096
elif sys.platform.startswith('win'):  # Win 32-bit or 64-bit
    _PATH_MAX = 511

# libusb_selected = "/home/bpiuser/bpi/mds_v3/lib/libusb-0.1.so.4.4.4-x86_64"    # Force using a specific libusb 0.1 if necessary
#try:


# except:
    # print("Python version ".format(sys.version_info))
    # print("Unsupported combination of OS and/or hardware: OS={},  HW={}".format(sys.platform, platform.machine()))


# libusb-win32 forces all structures to be packed, while
# default libusb only enforces this for some structures
# _PackPolicy defines the structure packing according to the platform.

class _PackPolicy(object):
    pass


if sys.platform == 'win32' or sys.platform == 'cygwin':
    _PackPolicy._pack_ = 1


class _usb_descriptor_header(CT.Structure):
    _pack_ = 1
    _fields_ = [('blength', CT.c_uint8),
                ('bDescriptorType', CT.c_uint8)]


class _usb_string_descriptor(CT.Structure):
    _pack_ = 1
    _fields_ = [('bLength', CT.c_uint8),
                ('bDescriptorType', CT.c_uint8),
                ('wData', CT.c_uint16)]


class _usb_endpoint_descriptor(CT.Structure, _PackPolicy):
    _fields_ = [('bLength', CT.c_uint8),
                ('bDescriptorType', CT.c_uint8),
                ('bEndpointAddress', CT.c_uint8),
                ('bmAttributes', CT.c_uint8),
                ('wMaxPacketSize', CT.c_uint16),
                ('bInterval', CT.c_uint8),
                ('bRefresh', CT.c_uint8),
                ('bSynchAddress', CT.c_uint8),
                ('extra', CT.POINTER(CT.c_uint8)),
                ('extralen', CT.c_int)]


class _usb_interface_descriptor(CT.Structure, _PackPolicy):
    _fields_ = [('bLength', CT.c_uint8),
                ('bDescriptorType', CT.c_uint8),
                ('bInterfaceNumber', CT.c_uint8),
                ('bAlternateSetting', CT.c_uint8),
                ('bNumEndpoints', CT.c_uint8),
                ('bInterfaceClass', CT.c_uint8),
                ('bInterfaceSubClass', CT.c_uint8),
                ('bInterfaceProtocol', CT.c_uint8),
                ('iInterface', CT.c_uint8),
                ('endpoint', CT.POINTER(_usb_endpoint_descriptor)),
                ('extra', CT.POINTER(CT.c_uint8)),
                ('extralen', CT.c_int)]


class _usb_interface(CT.Structure, _PackPolicy):
    _fields_ = [('altsetting', CT.POINTER(_usb_interface_descriptor)),
                ('num_altsetting', CT.c_int)]


class _usb_config_descriptor(CT.Structure, _PackPolicy):
    _fields_ = [('bLength', CT.c_uint8),
                ('bDescriptorType', CT.c_uint8),
                ('wTotalLength', CT.c_uint16),
                ('bNumInterfaces', CT.c_uint8),
                ('bConfigurationValue', CT.c_uint8),
                ('iConfiguration', CT.c_uint8),
                ('bmAttributes', CT.c_uint8),
                ('bMaxPower', CT.c_uint8),
                ('interface', CT.POINTER(_usb_interface)),
                ('extra', CT.POINTER(CT.c_uint8)),
                ('extralen', CT.c_int)]


class _usb_device_descriptor(CT.Structure, _PackPolicy):
    _pack_ = 1
    _fields_ = [('bLength', CT.c_uint8),
                ('bDescriptorType', CT.c_uint8),
                ('bcdUSB', CT.c_uint16),
                ('bDeviceClass', CT.c_uint8),
                ('bDeviceSubClass', CT.c_uint8),
                ('bDeviceProtocol', CT.c_uint8),
                ('bMaxPacketSize0', CT.c_uint8),
                ('idVendor', CT.c_uint16),
                ('idProduct', CT.c_uint16),
                ('bcdDevice', CT.c_uint16),
                ('iManufacturer', CT.c_uint8),
                ('iProduct', CT.c_uint8),
                ('iSerialNumber', CT.c_uint8),
                ('bNumConfigurations', CT.c_uint8)]


class _usb_device(CT.Structure, _PackPolicy):
    pass


class _usb_bus(CT.Structure, _PackPolicy):
    pass


_usb_device._fields_ = [('next', CT.POINTER(_usb_device)),
                        ('prev', CT.POINTER(_usb_device)),
                        ('filename', CT.c_int8 * (_PATH_MAX + 1)),
                        ('bus', CT.POINTER(_usb_bus)),
                        ('descriptor', _usb_device_descriptor),
                        ('config', CT.POINTER(_usb_config_descriptor)),
                        ('dev', CT.c_void_p),
                        ('devnum', CT.c_uint8),
                        ('num_children', CT.c_ubyte),
                        ('children', CT.POINTER(CT.POINTER(_usb_device)))]

_usb_bus._fields_ = [('next', CT.POINTER(_usb_bus)),
                     ('prev', CT.POINTER(_usb_bus)),
                     ('dirname', CT.c_char * (_PATH_MAX + 1)),
                     ('devices', CT.POINTER(_usb_device)),
                     ('location', CT.c_uint32),
                     ('root_dev', CT.POINTER(_usb_device))]

_usb_dev_handle = CT.c_void_p


def make_libusb0():
    """
        Prepare a libusb0 driver interface according to the OS we are running on
    """
    with open("./mds_config.json", "r") as fin:
        cfg = json.loads(fin.read())
    
    print(cfg["simulate"])
    mca_simulator = {"SiPM-Counter": "sipm_counter_simusb", "SiPM-1000": "sipm_1k_simusb", "PMT-1000": "pmt_1k_simusb",
                     "SiPM-3000": "sipm_3k_simusb", "PMT-3000": "pmt_3k_simusb", "PMT-N3000": "pmt_n3k_simusb",
                     "eMorpho": "emorpho_simusb"}
    if cfg["simulate"] in mca_simulator:
        if sys.platform.startswith('linux'):
            ext = "so"
        else:
            ext = "dll"
        libusb_selected = "./lib/{}.{}".format(mca_simulator[cfg["simulate"]], ext)
        sim_mca_id = {'eMorpho': 0x6001, 'SiPM-Counter': 0x200, 
                      'PMT-1000': 0x101, 'SiPM-1000': 0x201, 
                      'PMT-2000': 0x102, 'SiPM-2000': 0x202,
                      'PMT-3000': 0x103, 'SiPM-3000': 0x203,
                      'PMT-N3000': 0x104}
        with open("./lib/sim_data/sim_init.txt", "w") as fout:
            fout.write("{:d} 0 40.0e6".format(sim_mca_id[cfg["simulate"]]))  # For now, just hard-code the sim_init.txt file
        
    else:
        # Figure out what platform we are running on and choose the appropriate libusb shared object or dll
        machine = platform.machine()
        if sys.platform.startswith('linux2') and machine == 'armv7l':  # BPI's MDC
            libusb_selected = "./lib/libusb-0.1.so.4.4.4-ARM"  # Use this for linux on a 32-bit BPI MDC
        elif sys.platform.startswith('linux'):
            if machine == 'armv7l':
                libusb_selected = "./lib/libusb-0.1.so.4.4.4-PI"  # Use this for linux on a 32-bit Raspberry Pi
            if machine == 'x86_64':
                libusb_selected = "./lib/libusb-0.1.so.4.4.4-x86_64"  # Use this for linux 64-bit on Intel
            if machine == 'x86':
                libusb_selected = "./lib/libusb-0.1.so.4.4.4-x86"  # Use this for linux 32-bit on Intel
        elif sys.platform.startswith('win'):  # Win 32-bit or 64-bit
            libusb_selected = "C:\\Windows\\System32\\libusb0.dll"  # Absolute path for Windows

        # libusb_selected = "/home/bpiuser/bpi/mds_v3/lib/libusb-0.1.so.4.4.4-x86_64"    # Force using a specific libusb 0.1 if necessary

    print("Selected libusb library: {}".format(libusb_selected))
    CT.cdll.LoadLibrary(libusb_selected)
    libusb0 = CT.CDLL(libusb_selected)

    libusb0.usb_get_busses.restype = CT.POINTER(_usb_bus)
    libusb0.usb_get_busses.argtypes = []
    
    libusb0.usb_open.restype = _usb_dev_handle
    libusb0.usb_open.argtypes = [CT.POINTER(_usb_device)]

    libusb0.usb_get_string_simple.argtypes = [_usb_dev_handle, CT.c_int, CT.c_char_p, CT.c_size_t]

    if LIBUSB_HAS_GET_DRIVER_NP:
        libusb0.usb_detach_kernel_driver_np.argtypes = [_usb_dev_handle, CT.c_int]

    libusb0.usb_set_configuration.argtypes = [_usb_dev_handle, CT.c_int]
    libusb0.usb_claim_interface.argtypes = [_usb_dev_handle, CT.c_int]
    libusb0.usb_control_msg.argtypes = [_usb_dev_handle, CT.c_int, CT.c_int, CT.c_int, CT.c_int, CT.c_char_p, CT.c_int, CT.c_int]

    libusb0.usb_close.argtypes = [_usb_dev_handle]

    libusb0.usb_bulk_read.argtypes = [_usb_dev_handle, CT.c_int, CT.c_char_p, CT.c_int, CT.c_int]
    libusb0.usb_bulk_read.restypes = CT.c_int

    libusb0.usb_bulk_write.argtypes = [_usb_dev_handle, CT.c_int, CT.c_char_p, CT.c_int, CT.c_int]
    libusb0.usb_bulk_write.restypes = CT.c_int
    
    return libusb0