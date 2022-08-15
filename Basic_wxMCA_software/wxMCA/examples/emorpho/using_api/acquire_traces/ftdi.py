from __future__ import division
import os
import time
import ctypes as CT
import array
import sys
import platform
import struct
"""
Bare-metal interface to the FTDI FT245 USB controller on the eMorpho MCA.
We use ctypes to make the connection between python variables and C-variables of libusb0.1.
Originally written for Python 2.7

May 16: Tested against Python 2.7.6 and 3.5.2
Note: Clients can not mix python versions.
After having called ftdi from Python 3.5, calling with Python 2.7 will not work - until the device is unplugged and plugged back in. But calls from Python 3.5 will continue to work without unplugging.
"""

# print(sys.version_info)

LIBUSB_HAS_GET_DRIVER_NP = sys.platform.startswith('linux')

USE_WIN32 = sys.platform.startswith('win32')  # returns TRUE or FALSE

# Figure out what platform we are running on and choose the appropriate libusb shared object or dll
machine = platform.machine()
if sys.platform.startswith('linux2') and machine == 'armv7l':  # BPI's MDC
    libusb_selected = "./lib/libusb-0.1.so.4.4.4-ARM"  # Use this for linux on a 32-bit BPI MDC
    _PATH_MAX = 4096
elif sys.platform.startswith('linux'):
    _PATH_MAX = 4096
    if machine == 'armv7l':
        libusb_selected = "./lib/libusb-0.1.so.4.4.4-PI"  # Use this for linux on a 32-bit Raspberry Pi
    if machine == 'x86_64':
        libusb_selected = "./lib/libusb-0.1.so.4.4.4-x86_64"  # Use this for linux 64-bit on Intel
    if machine == 'x86':
        libusb_selected = "./lib/libusb-0.1.so.4.4.4-x86"  # Use this for linux 32-bit on Intel
elif sys.platform.startswith('win'):  # Win 32-bit or 64-bit
    libusb_selected = "C:\\Windows\\System32\\libusb0.dll"  # Absolute path for Windows
    _PATH_MAX = 511

# libusb_selected = "/home/bpiuser/bpi/mds_v3/lib/libusb-0.1.so.4.4.4-x86_64"    # Force using a specific libusb 0.1 if necessary
#try:
print("Selected libusb library: {}".format(libusb_selected))
CT.cdll.LoadLibrary(libusb_selected)
libusb0 = CT.CDLL(libusb_selected)
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

libusb0.usb_bulk_write.argtypes = [_usb_dev_handle, CT.c_int, CT.c_char_p, CT.c_int, CT.c_int]

USB_RECIP_DEVICE = 0
USB_TYPE_VENDOR = 64
USB_ENDPOINT_OUT = 0x02
USB_ENDPOINT_IN = 0x81
FTDI_DEVICE_OUT_REQTYPE = (USB_TYPE_VENDOR | USB_RECIP_DEVICE | USB_ENDPOINT_OUT)
FTDI_DEVICE_IN_REQTYPE = (USB_TYPE_VENDOR | USB_RECIP_DEVICE | USB_ENDPOINT_IN)


# FT245 chip control I/O requests
SIO_SET_LATENCY_TIMER_REQUEST = 0x9
SIO_GET_LATENCY_TIMER_REQUEST = 0xA
SIO_READ_EEPROM_REQUEST = 0x90
SIO_WRITE_EEPROM_REQUEST = 0x91
SIO_ERASE_EEPROM_REQUEST = 0x92

SIO_RESET_REQUEST = 0x0

SIO_RESET_SIO = 0x0
SIO_RESET_PURGE_RX = 0x1
SIO_RESET_PURGE_TX = 0x2
SIO_RESET_PURGE_RX_TX = 0x3

# FT230 requests, in addition to above
SIO_SET_BAUDRATE_REQUEST = 0x03


class mca:
    def __init__(self):
        self.sn = "eRC0001"
        self.handle = None
        self.write_ep = USB_ENDPOINT_OUT  # The endpoint to write to
        self.read_ep = USB_ENDPOINT_IN  # # The endpoint to read from
        self.usb_read_timeout = 1000  # in ms
        self.usb_write_timeout = 1000  # in ms
        self.cmd = {}  # The command is a user-supplied dictionary
        self.bytes_out = array.array('B', [0]*64)
        self.bytes_in = array.array('B', [0]*256)
        self.num_bytes = None
        self.cmd_out_list = []
        self.data_in_list = []
        self.data_in_dict = {}
        self.data_out_list = []
        self.data_out_dict = {}
        self.adc_sr = 40e6

        # set latency timer in this device
    def set_latency_timer(self, latency):
        """
        Controls the time out on the device
        :param latency: Timeout in ms; set to 2, except for writing the EEPROM, which needs 0x77
        :return: 0
        """
        latency &= 0xFF  # only lower byte is valid
        libusb0.usb_control_msg(self.handle, 64, SIO_SET_LATENCY_TIMER_REQUEST, latency, 0, CT.c_char_p(0), 0,
                                self.usb_write_timeout)
        return 0

    def purge_tx_buffer(self):
        ret = libusb0.usb_control_msg(self.handle, 64, SIO_RESET_REQUEST, SIO_RESET_PURGE_TX, 0, CT.c_char_p(0), 0,
                                      self.usb_write_timeout)
        return ret

    # read byte data from device dev_num
    def read_data(self, bytes_per_datum):
        """
        Read data from the Morpho device to the host
        self.cmd['num_bytes']: number of bytes requested by the host
        bytes_per_datum: 2 or 4
        :return: data array with num_bytes/2 words or num_bytes/4 longs
        """
        read_bytes = int(((self.num_bytes + 256)//62 + 1)*64)  # Each USB packet contains 2 status bytes
        self.purge_tx_buffer()
        # Fast conversion from C-array of bytes to python list of integers
        if sys.byteorder == "little":  # This works on little-endian machines
            word_buf = array.array('H', [0]*read_bytes)  # don't use a string; this ensures 4-byte alignment
            buffer_p = CT.cast(word_buf.buffer_info()[0], CT.c_char_p)
            ret = libusb0.usb_bulk_read(self.handle, self.read_ep, buffer_p, read_bytes, self.usb_read_timeout)

            # extract 16-bit integers, discarding the modem status at offsets n*32
            rb2 = read_bytes//2
            self.data_in_list = [word_buf[n] for n in range(0, rb2) if n & 31]

            if bytes_per_datum == 4:
                nb2 = int(self.num_bytes//2)
                w0 = self.data_in_list[0:nb2:2]
                w1 = self.data_in_list[1:nb2:2]
                self.data_in_list = [ww0 + ww1*0x10000 for ww0, ww1 in zip(w0, w1)]

        else:  # standard code executes correctly on all platforms
            # Remove the modem status bytes, which are the first two bytes sent in every 64-byte data packet
            buffer = array.array('B', [0]*read_bytes)  # don't use a string; this ensures 4-byte alignment
            buffer_p = CT.cast(buffer.buffer_info()[0], CT.c_char_p)
            libusb0.usb_bulk_read(self.handle, self.read_ep, buffer_p, read_bytes, self.usb_read_timeout)

            bytes_out = [d for n, d in zip(range(read_bytes), buffer) if n & 62]  # Remove modem status bytes

            # Combine bytes into data words (16-bit or 32-bit)
            if bytes_per_datum == 2:
                b0 = bytes_out[0::2]
                b1 = bytes_out[1::2]
                self.data_in_list = [bb0 + bb1*0x100 for bb0, bb1 in zip(b0, b1)]

            else:  # assume bytes_per_datum == 4:
                b0 = bytes_out[0::4]
                b1 = bytes_out[1::4]
                b2 = bytes_out[2::4]
                b3 = bytes_out[3::4]
                self.data_in_list = [bb0 + bb1*0x100 + bb2*0x10000 + bb3*0x1000000
                                     for bb0, bb1, bb2, bb3 in zip(b0, b1, b2, b3)]

        # Do not send more data than expected
        self.data_in_list = self.data_in_list[0:int(self.num_bytes/bytes_per_datum)]
        return None

    def write_data_old(self):
        """
        Write data to the eMorpho FPGA
        cmd['data']: List of 16-bit unsigned integers
        :return:
        """
        num_words = len(self.cmd['data'])
        buffer = array.array('B', [0] * 2 * num_words)
        buffer_p = CT.cast(buffer.buffer_info()[0], CT.c_char_p)
        struct.pack_into("<{}H".format(num_words), buffer, 0, *self.cmd['data'])
        ret = libusb0.usb_bulk_write(self.handle, self.write_ep, buffer_p, num_words * 2, self.usb_write_timeout)
        return ret

    def write_data(self):
        """
        Write data to the eMorpho FPGA
        The host filled mca.bytes_out with data
        :return:
        """
        buffer_p = CT.cast(self.bytes_out.buffer_info()[0], CT.c_char_p)
        ret = libusb0.usb_bulk_write(self.handle, self.write_ep, buffer_p, len(self.bytes_out), self.usb_write_timeout)
        return ret


class bpi_usb:
    """Unified interface to all Morpho devices that use an FTDI USB interface"""
    def __init__(self):
        self.max_packet_size = 64
        self.usb_read_timeout = 1000
        self.usb_write_timeout = 1000
        self.bpi_vid = 0x1FA4
        self.devices = list()
        self.handles = list()
        self.num_morphos = 0

    def scan_all(self):
        """Scans for morphos and count them; Does not open a Morpho."""
        libusb0.usb_init()
        libusb0.usb_find_busses()
        libusb0.usb_find_devices()
        bus = libusb0.usb_get_busses()  # get won't work without the find's above
        count = 0
        while bool(bus):
            dev = bus[0].devices
            while bool(dev):
                vid = dev[0].descriptor.idVendor
                pid = dev[0].descriptor.idProduct
                ok = vid == 0x1FA4 and pid == 0x6001  # find emorpho with BPI VID
                if ok:
                    count += 1
                dev = dev[0].next
            bus = bus[0].next
        self.num_morphos = count
        return count

    def find_all(self):
        libusb0.usb_init()
        libusb0.usb_find_busses()
        libusb0.usb_find_devices()
        bus = libusb0.usb_get_busses()  # get won't work without the find's above
        while bool(bus):
            dev = bus[0].devices
            while bool(dev):
                vid = dev[0].descriptor.idVendor
                pid = dev[0].descriptor.idProduct
                ok = vid == 0x1FA4 and pid == 0x6001  # find emorpho with BPI VID
                if ok:
                    self.devices.append(dev)
                dev = dev[0].next
            bus = bus[0].next
        self.num_morphos = len(self.devices)
        print("number of eMorphos: {}".format(len(self.devices)))
        if self.num_morphos == 0:
            return dict()

        mca_dict = dict()
        dev = self.devices[0]
        offset = dev[0].descriptor.iSerialNumber
        for dev in self.devices:
            handle = libusb0.usb_open(dev)
            self.handles.append(handle)  # open and store handle
            buffer = array.array('B', [0]*16)
            buffer_p = CT.cast(buffer.buffer_info()[0], CT.c_char_p)
            libusb0.usb_get_string_simple(handle, offset, buffer_p, 16)
            sn_char = map(chr, buffer)
            ser_num = ''.join(sn_char).split(chr(0), 1)[0]  # treat first null-byte as stop character
            # After the open, we need to detach the linux kernel driver and claim the interface
            if LIBUSB_HAS_GET_DRIVER_NP:
                libusb0.usb_detach_kernel_driver_np(handle, 0)

            if USE_WIN32:  # for ft245 config_value = 1 always
                libusb0.usb_set_configuration(handle, 1)

            libusb0.usb_claim_interface(handle, 0)

            # now reset the device
            libusb0.usb_control_msg(handle, 64, 0, 0, 0, CT.c_char_p(0), 0, self.usb_write_timeout)

            self.handles.append(handle)
            mca_dict[ser_num] = mca()
            mca_dict[ser_num].sn = ser_num
            mca_dict[ser_num].handle = handle
            mca_dict[ser_num].set_latency_timer(2)

        return mca_dict

    # close all open devices
    def close_all(self):
        for handle in self.handles:
            libusb0.usb_close(handle)
        self.devices = []  # now an empty list
        self.handles = []  # now an empty list
        return 0


