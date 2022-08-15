from __future__ import division
import ctypes
import array
import sys
import platform
import json
import time
import struct
import libusb0

"""
libusb 0.1, libusb-win32 documentation:
https://sourceforge.net/p/libusb-win32/wiki/Documentation/

"""

libusb0 = libusb0.make_libusb0()

COMMAND_OUT_EP = 0x01  # To program the data port of the bpi_usb device
COMMAND_IN_EP = 0x81   # Read back log and status information
DATA_OUT_EP = 0x02  # To send data to the bpi_usb device (destined for the ARM or the FPGA)
DATA_IN_EP = 0x82  # To read data from the bpi_usb device (from for the ARM or the FPGA)

"""
MCA ID and USB Product ID:
mca_id byte 0: 0->counter, 1->arm-based MCA, 2->FPGA-based MCA, 3->with eMorpho FPGA; 
mca_id byte 1: 1 for PMT, 2 for SiPM
"""

PMT_COUNTER_PID = 0x100
SIPM_COUNTER_PID = 0x200
EMORPHO_PID = 0x6001
PMT3K_MCA_PID = 0x103 # PMT-3000 
SIPM3K_MCA_PID = 0x203 # SiPM-3000 
PMT2K_MCA_PID = 0x102 # PMT-2000 
SIPM2K_MCA_PID = 0x202 # SiPM-2000  
PMT1K_MCA_PID = 0x101 # PMT-1000 
SIPM1K_MCA_PID = 0x201 # SiPM-1000 
PMT_N3K_PID = 0x104 # PMT-3K neutron counter
SIPM_N3K_PID = 0x204 # SiPM-3K neutron counter
COUNTER_3K = 0x005 # Digital pulse counter with ARM and FPGA
HV_ARM = 0x106 # ARM-controlled PMT high voltage supply

pid_list = [EMORPHO_PID, PMT1K_MCA_PID, SIPM1K_MCA_PID, PMT2K_MCA_PID, SIPM2K_MCA_PID, PMT3K_MCA_PID, SIPM3K_MCA_PID, 
            PMT_COUNTER_PID, SIPM_COUNTER_PID, PMT_N3K_PID, SIPM_N3K_PID, COUNTER_3K, HV_ARM]  # Valid product ID's

class bpi_usb:
    """
    A minimal class to count the number of attached MCAs (scan_all) and to claim and open all
    attached MCAs (find_all).
    scan_all() can be used at any time.
    find_all() attempts to claim and open all attached MCAs.  It returns a dictionary of mca objects.
    close_all() can be used to close all MCAs.  But the user will have to discard the mca-object dictionary,
    since its usb handles will now be invalid.
    """
    def __init__(self):
        self.max_packet_size = 64
        self.cmd_out_ep = COMMAND_OUT_EP  # To program the data port of the bpi_usb device
        self.cmd_in_ep = COMMAND_IN_EP  # Read back log and status information
        self.data_out_ep = DATA_OUT_EP  # To send data to the bpi_usb device (destined for the ARM or the FPGA)
        self.data_in_ep = DATA_IN_EP  # To read data from the bpi_usb device (from the ARM or the FPGA)
        self.usb_read_timeout = 1000  # in ms
        self.usb_write_timeout = 1000  # in ms
        self.bpi_vid = 0x1FA4
        self.devices = list()
        self.pids = list()
        self.handles = list()
        self.sernums = list()
        self.LIBUSB_HAS_GET_DRIVER_NP = sys.platform.startswith('linux')
        self.USE_WIN32 = sys.platform.startswith('win32')  # returns TRUE or FALSE


    def scan_all(self):
        """Scans for MCA and count them; Does not open an MCA."""
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
                print("VID/PID", vid, pid)
                ok = (vid == self.bpi_vid and (pid in pid_list))  # find an MCA with BPI VID and a supported PID
                if ok:
                    count += 1
                dev = dev[0].next
            bus = bus[0].next
        return count

    def find_all(self):
        """
            Scan the USB bus for all acceptable devices and claim the interface for communication.
        """
        # libusb0.usb_set_debug(4)
        self.handles = list()
        libusb0.usb_init()
        libusb0.usb_find_busses()
        libusb0.usb_find_devices()
        bus = libusb0.usb_get_busses()  # get won't work without the find()'s above
        
        while bool(bus):
            print("finding")
            dev = bus[0].devices
            while bool(dev):
                vid = dev[0].descriptor.idVendor
                pid = dev[0].descriptor.idProduct
                print("PID: {:X}, VID: {:X}".format(pid, vid))
                ok = (vid == self.bpi_vid and (pid in pid_list))  # find PMT-MCA with BPI VID
                if ok:
                    self.devices.append(dev)
                    self.pids.append(pid)
                    # open device and store handle
                    handle = libusb0.usb_open(dev)
                    self.handles.append(handle)
                    # After the open, we need to detach the linux kernel driver, and claim the interface
                    if self.LIBUSB_HAS_GET_DRIVER_NP:
                        libusb0.usb_detach_kernel_driver_np(handle, 0)

                    if self.USE_WIN32:  # This call is necessary for libusb-win32; config_value = 1 always
                        # select a configuration in software; Call does not communicate with the device
                        libusb0.usb_set_configuration(handle, 1)
                    if pid == 0x6001:
                        libusb0.usb_claim_interface(handle, 0)  # device only has interface no. 0
                    else:
                        libusb0.usb_claim_interface(handle, 1)  # device only has interface no. 0
                dev = dev[0].next
            bus = bus[0].next

        
        print("number of MCA: {}".format(len(self.devices)))
        return self.make_mca_dict()

        
    def make_mca_dict(self):
        """
            Create a dictionary of mca or eMorpho objects.
            The eMorpho uses an FT245RL USB interface chip and so its methods for I/O and communication with non-volatile memory differ from those devices that have an ARM SAML21 processor with a software-defined USB interface.
        """
        mca_dict = {}
        sn_list = []

        self.sernums = []
        for handle, pid, dev in zip(self.handles, self.pids, self.devices):
            # Now that we claimed the interface, we can read the software-defined serial numbers
            if pid == 0x6001:  # eMorpho
                # Reset the FTDI chip
                libusb0.usb_control_msg(handle, 64, 0, 0, 0, ctypes.c_char_p(0), 0, self.usb_write_timeout)
                offset = dev[0].descriptor.iSerialNumber
                buffer = array.array('B', [0]*16)
                buffer_p = ctypes.cast(buffer.buffer_info()[0], ctypes.c_char_p)
                libusb0.usb_get_string_simple(handle, offset, buffer_p, 16)
                sn_char = map(chr, buffer)
                ser_num = ''.join(sn_char).split(chr(0), 1)[0]  # treat first null-byte as stop 
                
                mca_dict[ser_num] = emorpho()
                mca_dict[ser_num].sn = ser_num
                mca_dict[ser_num].short_sn = ser_num
                mca_dict[ser_num].mca_id = 0x6001
                mca_dict[ser_num].mca_id_str = "0x6001"
                mca_dict[ser_num].handle = handle
                mca_dict[ser_num].set_latency_timer(2)
                self.sernums.append(ser_num)
                mca_dict[ser_num].boot_from_nvmem()
                mca_dict[ser_num].get_adc_sr()
                
            else:  # MCA with ARM
                # Create command-out byte array
                bytes_out = array.array('B', [0] * 64)
                bytes_out[0] = 4   # ARM_READ = 4
                bytes_out[2] = 64  # Read 64 bytes
                buffer_out_p = ctypes.cast(bytes_out.buffer_info()[0], ctypes.c_char_p)
                
                bytes_in = array.array('B', [0] * 64)  # Create a receive byte buffer
                buffer_in_p = ctypes.cast(bytes_in.buffer_info()[0], ctypes.c_char_p)
                
                # Send the read command and read the version registers
                ret1 = 0
                count = 0
                ret0 = libusb0.usb_bulk_write(handle, self.cmd_out_ep, buffer_out_p, 64, self.usb_write_timeout)
                time.sleep(0.001)
                while ret1 == 0:
                    ret1 = libusb0.usb_bulk_read(handle, self.data_in_ep, buffer_in_p, 64, self.usb_read_timeout)
                    count += 1

                # Extract the unique serial number as a string
                #sn = ''.join(['{:X}'.format(bytes_in[23-n]) for n in range(16)])  # Location of the unique serial number
                sn = ''.join(['{:X}'.format(bytes_in[n+8]) for n in range(16)])  # Location of the unique serial number
                mca_dict[sn] = mca()
                mca_dict[sn].handle = handle
                mca_dict[sn].sn = sn
                mca_dict[sn].mca_id = struct.unpack_from("<1I", bytes_in)[0]
                mca_dict[sn].mca_id_str = "0x{:X}".format(mca_dict[sn].mca_id)
                mca_dict[sn].get_adc_sr()
                mca_dict[sn].short_sn = struct.unpack_from("<1I", bytes_in[4: 8])[0]
                self.sernums.append(sn)
                print("MCA unique ser num: {}; short ser num: {}".format(sn, mca_dict[sn].short_sn))
                sn_list.append(sn)
                sn_list.append(mca_dict[sn].short_sn)
        
        with open("sn_list.txt",'w') as snfile:
        	for item in sn_list:
        		snfile.write(str(item)+'\n')
        	snfile.close()    
        return mca_dict


    # close all open devices
    def close(self):
        for handle in self.handles:
            libusb0.usb_close(handle)
        self.handles = []  # now an empty list
        self.devices = []  # now an empty list
        self.sernums = []  # now an empty list
        return 0


class mca:
    """
        Class for communication with MCA that have an ARM and a software USB interface.
    """
    def __init__(self):
        self.sn = "0123456789ABCDEF0123456789ABCDEF"
        self.mca_id = 257
        self.mca_id_str = "0x101"
        self.handle = None
        self.cmd_out_ep = COMMAND_OUT_EP  # To program the data port of the bpi_usb device
        self.cmd_in_ep = COMMAND_IN_EP  # Read back log and status information
        self.data_out_ep = DATA_OUT_EP  # To send data to the bpi_usb device (destined for the ARM or the FPGA)
        self.data_in_ep = DATA_IN_EP  # To read data from the bpi_usb device (from the ARM or the FPGA)
        self.write_ep = COMMAND_OUT_EP  # The endpoint we write to depends on the command
        self.read_ep = DATA_IN_EP  # # The endpoint we read from depends on the command
        self.usb_read_timeout = 1000  # in ms
        self.usb_write_timeout = 1000  # in ms
        self.cmd = {}  # The command is a user-supplied dictionary
        self.mem_type = 0,  # 0->RAM, 1->FLASH
        self.num_bytes = 0
        self.bytes_out = array.array('B', [0]*256)
        self.bytes_in = array.array('B', [0]*256)
        self.cmd_in_list = []
        self.cmd_in_dict = {}
        self.cmd_out_list = []
        self.cmd_out_dict = {}
        self.data_in_list = []
        self.data_in_dict = {}
        self.data_out_list = []
        self.data_out_dict = {}
        self.adc_sr = 40e6
        
    def __repr__(self):
        repr_dict = {
            "sn": self.sn,
            "cmd_in_list": self.cmd_in_list,
            "cmd_out_list": self.cmd_out_list,
            # "cmd_in_dict": self.cmd_in_dict,
            # "cmd_out_dict": self.cmd_out_dict,
            "data_in_list": self.data_in_list,
            # "data_in_dict": self.data_in_dict,
            "data_out_list": self.data_out_list
            # "data_out_dict": self.data_out_dict
        }
        return json.dumps(repr_dict)

    # read byte data from device
    def read_data(self):
        """
        Read data from the device in chunks of 256 bytes or less.  The ARM MCU only buffers data up to 256 bytes.
        The function assumes that the data port on the ARM has been programmed already.

        Returns:
            None

        Side effects:
            Fills self.bytes_in
        """
        chunk_size = 256
        if self.num_bytes <= 0:
            self.bytes_in = array.array('B', [255] * 4)
            return None

        self.num_bytes = int(min(65536, self.num_bytes))  # 64KB is the maximum read size
        num_chunks = self.num_bytes // chunk_size
        frac_length = self.num_bytes % chunk_size
        self.bytes_in = array.array('B', [0] * self.num_bytes)  # Create a receive byte buffer

        for n in range(num_chunks):
            buffer_p = ctypes.cast(self.bytes_in.buffer_info()[0] + n * chunk_size, ctypes.c_char_p)
            ret = libusb0.usb_bulk_read(self.handle, self.read_ep, buffer_p, chunk_size, self.usb_read_timeout)
            #self.wait_100us(2)
            if ret != chunk_size:
                print("L309, read: ret=",ret, n, num_chunks, self.num_bytes, self.usb_read_timeout)

        if frac_length > 0:
            buffer_p = ctypes.cast(self.bytes_in.buffer_info()[0] + num_chunks * chunk_size, ctypes.c_char_p)
            ret = libusb0.usb_bulk_read(self.handle, self.read_ep, buffer_p, frac_length, self.usb_read_timeout)
            #self.wait_100us(2)
            if ret != frac_length:
                print("L313, read: ret=",ret, frac_length)
        
        return
        
    def wait_100us(self, us):
        us = int(2350*us)
        for n in range(us):
            us+=n

    def write_data(self):
        """
        Write data to the device in chunks of 256 bytes or less.  The ARM MCU only buffers data up to 256 bytes.
        Data to be written to the device are in self.bytes_out

        :return :
            None

        Side effects:
            None
        """

        chunk_size = 256
        if self.num_bytes <= 0:
            return 0
            
        num_bytes = self.num_bytes
        if self.write_ep == self.cmd_out_ep:  # The command out endpoint requires exactly 64 bytes.
            num_bytes = 64

        num_chunks = num_bytes // chunk_size
        frac_length = num_bytes % chunk_size
        
        ret = 0
        for n in range(num_chunks):
            buffer_p = ctypes.cast(self.bytes_out.buffer_info()[0] + n * chunk_size, ctypes.c_char_p)
            ret = 0
            #while ret == 0:
            ret = libusb0.usb_bulk_write(self.handle, self.write_ep, buffer_p, chunk_size, self.usb_write_timeout)
            if ret != chunk_size:
                print("L358, write: ret=",ret)

        if frac_length > 0:
            buffer_p = ctypes.cast(self.bytes_out.buffer_info()[0] + num_chunks * chunk_size, ctypes.c_char_p)
            ret = 0
            #while ret == 0:
            ret = libusb0.usb_bulk_write(self.handle, self.write_ep, buffer_p, frac_length, self.usb_write_timeout)
            if ret != frac_length:
                print("L366, write: ret=",ret) 
                
        return ret
        
    def get_adc_sr(self):
        if self.mca_id not in [0x103, 0x203, 0x104]:
            return
        # a) Prepare to read fpga_results
        num_bytes = 64
        header = (num_bytes << 16) + (2 << 4) + 2

        # Create command-out byte array
        self.write_ep = self.cmd_out_ep
        struct.pack_into("<1I", self.bytes_out, 0, header)  # cmd_out data, to be sent to the device
        struct.pack_into("<30H", self.bytes_out, 4, *([0]*30))  # cmd_out data, to be sent to the device
        self.num_bytes = 64
        self.write_data()  # Write to the command endpoint
        
        # b) Read the fpga_results
        self.num_bytes = 64
        self.read_data()
        self.data_in_list = struct.unpack_from("<32H", self.bytes_in)
        fpga_ctrl = self.data_in_list
        self.adc_sr = float(fpga_ctrl[6] & 0xFF)*1e6 # ADC speed


class emorpho:
    """
        Class for communicating with the eMorpho, which has an FT245RL ASIC USB interface.
    """
    def __init__(self):
        self.USB_ENDPOINT_OUT = 0x02
        self.USB_ENDPOINT_IN = 0x81
        self.SIO_SET_LATENCY_TIMER_REQUEST = 0x9
        self.SIO_RESET_REQUEST = 0x0
        self.SIO_RESET_PURGE_RX = 0x1
        self.SIO_RESET_PURGE_TX = 0x2
        self.SIO_RESET_PURGE_RX_TX = 0x3
    
        self.sn = "eRC0001"
        self.handle = None
        self.write_ep = self.USB_ENDPOINT_OUT  # The endpoint to write to
        self.read_ep = self.USB_ENDPOINT_IN  # # The endpoint to read from
        self.usb_read_timeout = 1000  # in ms
        self.usb_write_timeout = 1000  # in ms
        self.cmd = {}  # The command is a user-supplied dictionary
        self.bytes_out = array.array('B', [0]*64)
        self.bytes_in = array.array('B', [0]*256)
        self.num_bytes = None
        self.num_bytes_out = 64
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
        libusb0.usb_control_msg(self.handle, 64, self.SIO_SET_LATENCY_TIMER_REQUEST, latency, 0, ctypes.c_char_p(0), 0, self.usb_write_timeout)
                                
        return 0

    def purge_tx_buffer(self):
        return libusb0.usb_control_msg(self.handle, 64, self.SIO_RESET_REQUEST, self.SIO_RESET_PURGE_TX, 0, ctypes.c_char_p(0), 0, self.usb_write_timeout)

    # read byte data from device dev_num
    def read_data(self, bytes_per_datum):
        """
        Read data from the Morpho device to the host
        self.cmd['num_bytes']: number of bytes requested by the host
        bytes_per_datum: 2 or 4
        :return: data array with num_bytes/2 words or num_bytes/4 longs
        """
        depth = 0
        read_bytes = int(((self.num_bytes + depth)//62 + 1)*64)  # Each USB packet contains 2 status bytes
        self.purge_tx_buffer()  # This empties the transmit FIFO which has 256 bytes of old data.
        if bytes_per_datum == 1:
            byte_buf = array.array('B', [0]*(read_bytes))  # don't use a string; this ensures 4-byte alignment
            buffer_p = ctypes.cast(byte_buf.buffer_info()[0], ctypes.c_char_p)
            ret = libusb0.usb_bulk_read(self.handle, self.read_ep, buffer_p, read_bytes, self.usb_read_timeout)
            self.data_in_list = [d for n, d in zip(range(read_bytes), byte_buf) if n & 62]  # Remove modem status bytes
            return None
            
        # Fast conversion from C-array of bytes to python list of integers
        if sys.byteorder == "little":  # This works on little-endian machines
            
            word_buf = array.array('H', [0]*(read_bytes))  # don't use a string; this ensures 4-byte alignment
            buffer_p = ctypes.cast(word_buf.buffer_info()[0], ctypes.c_char_p)
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
            buffer_p = ctypes.cast(buffer.buffer_info()[0], ctypes.c_char_p)
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

    def write_data(self):
        """
        Write data to the eMorpho FPGA
        The host filled mca.bytes_out with data
        :return:
        """
        buffer_p = ctypes.cast(self.bytes_out.buffer_info()[0], ctypes.c_char_p)
        ret = libusb0.usb_bulk_write(self.handle, self.write_ep, buffer_p, len(self.bytes_out), self.usb_write_timeout)
        return ret
        
    def boot_from_nvmem(self):
        """
            The function first reads fpga_results to determine the ADC speed.  
            It then reads the nv-mem.  If the data in the nv-mem are valid, 
            it will write those fpga_ctrl data into the FPGA RAM.
            
            We avoid reaching to the API layer, and rather code this functionality
            with what is available in this limited class.
        """
        # Read fpga_results to set adc_sr
        self.num_bytes = 2
        self.bytes_out = array.array('B', [0] * 2)
        struct.pack_into("<1H", self.bytes_out, 0, 0x207)
        self.write_data()
        self.num_bytes = 32
        self.read_data(2)
        
        self.adc_sr = (self.data_in_list[6] & 0xFF)*1e6
        
        # Read fpga_ctrl from nv-mem
        # a) Read fpga_ctrl from FPGA 
        self.bytes_out = array.array('B', [0] * 2)
        struct.pack_into("<1H", self.bytes_out, 0, 0x007)
        self.write_data()
        self.num_bytes = 32
        self.read_data(2)
        fpga_ctrl_ram = [w for w in self.data_in_list[0:16]]
        fpga_ctrl_ram[13] &= ~0x100  # Clear the sel_lut bit
        fpga_ctrl_ram[15] |= 0x80  # Set the self-clearing read_nv bit
        
        # b) write the fpga_ctrl back to prepare read from nv_mem to user area
        self.bytes_out = array.array('B', [0] * 34)
        struct.pack_into("<1H", self.bytes_out, 0, 0x003)
        struct.pack_into("<16H", self.bytes_out, 2, *fpga_ctrl_ram)
        self.write_data()
        time.sleep(0.01) # Wait for nv-mem data to be copied into user area
        
        # c) Read data from user area
        self.bytes_out = array.array('B', [0] * 2)
        struct.pack_into("<1H", self.bytes_out, 0, 0x607)
        self.write_data()
        self.num_bytes = 34 # Check word + 16 fpga_ctrl data
        self.read_data(2)
        fpga_ctrl_nvmem = self.data_in_list[1:17]        
        
        # d) Check nv-mem for valid content and if valid, copy to fpga_ctrl on the device
        if self.data_in_list[0] == 0x8003:
            fpga_ctrl_nvmem[15] = 0x8000  # Set run bit, but not Program_HV bit
            self.bytes_out = array.array('B', [0] * 34)
            struct.pack_into("<1H", self.bytes_out, 0, 0x003)
            struct.pack_into("<16H", self.bytes_out, 2, *fpga_ctrl_nvmem)
            self.write_data()
            fpga_ctrl = fpga_ctrl_nvmem[0:16]
        else:
            fpga_ctrl = fpga_ctrl_ram[0:16]
        fpga_ctrl[13] &= ~0x100  # Clear the sel_lut bit
            
        # Now ramp up the high voltage slowly to avoid power surge        
        val = fpga_ctrl[7]
        dac_target = ((val & 0xFFF) << 4) + ((val >> 12) & 0xF)
        hv_target = dac_target * 3000/65536
        print("Target HV: ", hv_target)
        for n in range(1, 11):  # Increment HV in 10 steps
            fpga_ctrl[15] = 0x8010  # Set the self-clearing program_hv bit
            dac_val = int((n*dac_target)/10)
            fpga_ctrl[7] = ((dac_val & 0xFFF0) >> 4) + ((dac_val & 0xF) << 12)
            self.bytes_out = array.array('B', [0] * 34)
            struct.pack_into("<1H", self.bytes_out, 0, 0x003)
            struct.pack_into("<16H", self.bytes_out, 2, *fpga_ctrl)
            self.write_data()
            time.sleep(0.1) # Wait for HV to ramp up
            
            
    def get_adc_sr(self):
        # a) Read fpga_results 
        self.bytes_out = array.array('B', [0] * 2)
        struct.pack_into("<1H", self.bytes_out, 0, 0x207)
        self.write_data()
        self.num_bytes = 32
        self.read_data(2)
        fpga_results = self.data_in_list
        self.adc_sr = float(fpga_results[6] & 0xFF)*1e6 # ADC speed
