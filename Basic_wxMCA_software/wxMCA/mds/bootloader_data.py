#!/usr/bin/python
#
# version 1.0
from __future__ import division
import string
import json

# ARM command types
ARM_WRITE = 3
ARM_READ = 4
ARM_COMMAND = 5

# ARM command addresses
ARM_VERSION = 0  # Read ARM software and hardware version
ARM_STATUS = 1  # Operational status of the slow-control system (R)
ARM_CMD = 2  # Commands that do not need data block transfer
ARM_ROM = 3  # Access program memory; Reading is disabled in shipped code
ARM_BOOT = 4  # Access boot_ctrl in nvmem; Disabled in shipped code


class arm_ping:
    def __init__(self):
        self.registers = [0] * 16
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.wr_type = 0
        self.rd_type = 0
        self.cmd_addr = 0
        self.data_type = 'I'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 4

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        pass

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        pass

    def user_2_fields(self):
        pass

class arm_version:
    def __init__(self):
        self.registers = [0] * 16
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.wr_type = ARM_WRITE
        self.rd_type = ARM_READ
        self.cmd_addr = ARM_VERSION
        self.data_type = 'I'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 4

    def add_to_cmd_out_list(self, mca):
        add_cmd_par(mca)

    def registers_2_fields(self):
        """
            Copy ARM version registers into named fields
            :return: None
        """
        self.fields = {
            'mca_id': self.registers[0],  # byte 0: 0->preampBase, 1->arm-based MCA, 2->FPGA-based MCA, 3->with eMorpho FPGA; byte 1: 1 for PMT, 2 for SiPM
            'short_sn': self.registers[1],  # Optional 4-byte serial number, deprecated
            'unique_sn_0': self.registers[2],  # 1st 4 bytes of unique serial number
            'unique_sn_1': self.registers[3],  # 2nd 4 bytes of unique serial number
            'unique_sn_2': self.registers[4],  # 3rd 4 bytes of unique serial number
            'unique_sn_3': self.registers[5],  # 4th 4 bytes of unique serial number
            'arm_hw': self.registers[6],  # ARM/PCB hardware version 0x0100 => 1.0 (BCD)
            'arm_sw': self.registers[7],  # ARM software version 0x0100 => 1.0 (BCD)
            'arm_build': self.registers[8],  # ARM software build number
            'arm_custom_0': self.registers[9],  # ARM software customization code; 1st 4 bytes
            'arm_custom_1': self.registers[10]  # ARM software customization code; 2nd 4 bytes
        }

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        """
            Convert some raw fields into more practical user data:
            unique serial number becomes a 32-character hex-string
            fpga_speed is now expressed in Hz.

            :return: None
        """
        self.user = {
            'unique_sn': '{:X}'.format(self.fields['unique_sn_0']) + '{:X}'.format(self.fields['unique_sn_1']) +
                         '{:X}'.format(self.fields['unique_sn_2']) + '{:X}'.format(self.fields['unique_sn_3'])
        }

    def user_2_fields(self):
        pass


class arm_status:
    def __init__(self):
        self.registers = [0] * 64
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.wr_type = ARM_WRITE
        self.rd_type = ARM_READ
        self.cmd_addr = ARM_STATUS
        self.data_type = 'I'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 4

    def add_to_cmd_out_list(self, mca):
        add_cmd_par(mca)

    def registers_2_fields(self):
        """
            Copy ARM status registers into named fields
            :return: None
        """
        self.fields = {
            'rom_busy': self.registers[0]  # Current operating voltage
            
        }

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        """
            Convert some raw fields into more practical user data, using SI units:
            :return: None
        """
        self.user = {}

    def user_2_fields(self):
        pass


class arm_cmd:
    """
        This class is used to perform commands on the ARM processor that do not require bulk data transfers.
        Instead command and data are in the initial 64-byte block of data.
        Use this class only with "dir": "short_write" in the command.

    """
    def __init__(self):
        self.registers = [0] * 30  # There is room for 30 uint16_t data in the 64-byte command packet.
        self.fields = {}
        self.user = {}

        self.wr_type = ARM_COMMAND  # Writing a command using short write only.
        self.rd_type = ARM_READ
        self.cmd_addr = 0
        self.data_type = 'H'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 4

    def add_to_cmd_out_list(self, mca):
        add_cmd_par(mca)

    def registers_2_fields(self):
        pass

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        pass

    def user_2_fields(self):
        pass


class arm_rom:
    """
        This class is used to write application code to program flash memory.
        Use a dir='write" command to transfer 256 bytes at a time to usb_data_out.
        from where the ARM copies those data into the program-flash.
        Read back is disabled in shipped code.
    """
    def __init__(self):
        self.registers = [0] * 256
        self.fields = {}
        self.user = {}

        self.wr_type = ARM_WRITE
        self.rd_type = ARM_READ
        self.cmd_addr = ARM_ROM
        self.data_type = 'B'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items

    def add_to_cmd_out_list(self, mca):
        add_cmd_par(mca)

    def registers_2_fields(self):
        pass

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        pass

    def user_2_fields(self):
        pass

        
class arm_boot:
    """
        This class is used to access the boot_ctrl section in nvmem.
        Writing is disabled in shipped code.
    """
    def __init__(self):
        self.registers = [0] * 64
        self.fields = {}
        self.user = {}

        self.wr_type = ARM_WRITE
        self.rd_type = ARM_READ
        self.cmd_addr = ARM_BOOT
        self.data_type = 'I'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items

    def add_to_cmd_out_list(self, mca):
        add_cmd_par(mca)

    def registers_2_fields(self):
        self.fields = {
            "mca_id": self.registers[0],
            "stuffing": self.registers[1],
            "short_sn": self.registers[2],
            "hw_version": self.registers[3],
            "app_start": self.registers[4],
            "app_valid": self.registers[63]
        }
        

    def fields_2_registers(self):
        self.registers = list(self.registers)
        self.registers[0] = self.fields["mca_id"]
        self.registers[1] = self.fields["stuffing"]
        self.registers[2] = self.fields["short_sn"]
        self.registers[3] = self.fields["hw_version"]
        self.registers[4] = self.fields["app_start"]  # Will not be written back
        self.registers[63] = self.fields["app_valid"]  # For BPI programming only
        

    def fields_2_user(self):
        pass

    def user_2_fields(self):
        pass


def add_cmd_par(mca):
    if "ctrl" in mca.cmd:
        L = len(mca.cmd["ctrl"])
        for n in range(L):
            mca.cmd_out_list[n] = mca.cmd["ctrl"][n]
            
            