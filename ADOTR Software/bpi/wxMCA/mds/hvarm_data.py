#!/usr/bin/python
#
# version 1.0
from __future__ import division
import string
import json

# ARM command types
ARM_WRITE = 3
ARM_READ = 4

# ARM command addresses
ARM_VERSION = 0  # Read ARM software and hardware version
ARM_STATUS = 1  # Operational status of the slow-control system (R)
ARM_CTRL = 2  # Operational control of the slow-control system (R/W)
ARM_CAL = 3  # Calibration and LUT in RAM
ARM_HISTO = 4  # MCA data with statistics and histogram (foreground)
ARM_BCK = 5  # MCA data with statistics and histogram (background)
ARM_DIFF = 6  # MCA data with statistics and histogram (foreground-background)
ARM_LPSRAM = 7  # Read fom the up to 8kB low-power SRAM

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
        pass

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
        self.data_type = 'f'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 4
        
    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        """
            Copy ARM status registers into named fields
            :return: None
        """
        self.fields = {
            'op_voltage': self.registers[0],       # Current operating voltage
            'voltage_target': self.registers[1],   # Computed target voltage from request (directly or with correction applied)
            'hv_power': self.registers[2],         # Current operating voltage set by the DAC (so that op_volt matches req_volt (directly or with correction applied)
            'hv_demand': self.registers[3],        # Current operating voltage set by the DAC (so that op_volt matches req_volt (directly or with correction applied)
            'cpu_temperature': self.registers[4],  # Current ARM M0+ temperature
            'x_temperature': self.registers[5],    # Current temperature measured by the external temperature sensor.
            'avg_temperature': self.registers[6],  # Current temperature average
            'wall_clock_time': self.registers[7],  # wall_clock time
            'run_status': int(self.registers[8]),  # Run status bit field; bit_0-> counter_active, 1-> counter bank, 2-> alarm_active;
            'hv_period': self.registers[9],        # Period register of the timer
            'hv_width': self.registers[10]         # Duty cycle register of the timer
        }

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        """
            Convert some raw fields into more practical user data, using SI units:
            :return: None
        """
        self.user = {
            'hv_on': int(self.fields['run_status']) & 1, # 1-> High voltage is on
            'soft_start': (self.fields['run_status'] >> 1) & 1, # Bit is set during the soft start time
            'hv_locked': (self.fields['run_status'] >> 2) & 1,  # 1-> HV feedback loop is in lock
            'hv_frequency': 48.0e6/float(self.registers[9]) if self.registers[9]>0 else 0,
            'hv_width': float(self.registers[10])/48e6
        }

    def user_2_fields(self):
        pass


class arm_ctrl:
    def __init__(self):
        self.registers = [0.0] * 64
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.wr_type = ARM_WRITE
        self.rd_type = ARM_READ
        self.cmd_addr = ARM_CTRL
        self.cmd_ctrl = None
        self.data_type = 'f'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 4

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        """
            Copy ARM control registers into named fields
            :return: None
        """
        self.fields = {
            'gain_stabilization': self.registers[0],  # [0:4]:0-> Use cal_ov as is; 1-> Apply temperature correction; 2-> use ROI; [4:8]=> no. of roi/led events
            'soft_start': self.registers[1],  # Soft start time in seconds
            'temp_ctrl': self.registers[2],  # 0-> Use ARM temperature sensor; 1-> Use external LTC2997 sensor; [4:8]=> (0-> no peltier; 1-> constant; 2-> ctrl-loop)
            'temp_target': self.registers[3],  # Temperature target for cooled systems
            'temp_period': self.registers[4],  # Update period for temperature measurements
            'temp_weight': self.registers[5],  # Weight for geometric averaging: Purpose is noise reduction or matching thermal relaxation
            'cal_temp': self.registers[6],  # Temperature (in deg C) at which the detector was calibrated
            'cal_ov': self.registers[7],  # Operating voltage when the detector was calibrated
            'max_power': self.registers[8],  # hv_power=0 -> Power limit, hv_power=1 -> Apply this power, no control loop,            
            'baud': self.registers[9],  # Baud rate for serial communication           
            'run_mode': int(self.registers[10]), # up to 24 control bits
            'run_action': int(self.registers[11]), # self-clearing action items
            'logger': self.registers[12],  # Controls the one-shot logger
            'xctrl_1': self.registers[13],  # Reserved
            'xctrl_2': self.registers[14],  # Reserved
            'xctrl_3': self.registers[15],  # Reserved
            'xctrl_4': self.registers[16],  # Reserved
            'xctrl_5': self.registers[17],  # Reserved
            'xctrl_6': self.registers[18],  # Reserved
            'xctrl_7': self.registers[19],  # Reserved
        }

    def fields_2_registers(self):
        """
            Copy ARM control fields into the register list
            :return: None
        """
        self.registers = [0]*64
        self.registers[0] = float(self.fields['gain_stabilization'])
        self.registers[1] = float(self.fields['soft_start'])
        self.registers[2] = float(self.fields['temp_ctrl'])
        self.registers[3] = float(self.fields['temp_target'])
        self.registers[4] = float(self.fields['temp_period'])
        self.registers[5] = float(self.fields['temp_weight'])
        self.registers[6] = float(self.fields['cal_temp'])
        self.registers[7] = float(self.fields['cal_ov'])
        self.registers[8] = float(self.fields['max_power'])
        
        self.registers[9] = float(self.fields['baud'])
        self.registers[10] = float(self.fields['run_mode'])
        self.registers[11] = float(self.fields['run_action'])
        self.registers[12] = float(self.fields['logger'])

        self.registers[13] = float(self.fields['xctrl_1'])
        self.registers[14] = float(self.fields['xctrl_2'])
        self.registers[15] = float(self.fields['xctrl_3'])
        self.registers[16] = float(self.fields['xctrl_4'])
        self.registers[17] = float(self.fields['xctrl_5'])
        self.registers[18] = float(self.fields['xctrl_6'])
        self.registers[19] = float(self.fields['xctrl_7'])


    def fields_2_user(self):
        self.user = {
            'gs_mode': int(self.fields['gain_stabilization']) & 0xF, # 0->OFF, 1->LUT
            
            'hv_on': int(self.fields['run_mode']) & 0x1,  # 0-> HV off, 1-> HV on
            'hv_ctrl': (int(self.fields['run_mode']) >> 1) & 0x1,  # 0-> Analog control via V_ctrl; 1-> Digital control via arm_ctrl[AC_CAL_OV];
            'hv_power': (int(self.fields['run_mode']) >> 2) & 0x1,  # 0-> Normal operation, 1->apply fixed power, no control loop
            
            'clear_alarm': (int(self.fields['run_action']) ) & 0x1,
            'clear_logger': (int(self.fields['run_action']) >> 1 ) & 0x1,
            'clear_wallclock': (int(self.fields['run_action']) >> 2) & 0x1,
            
        }
        

    def user_2_fields(self):
        self.fields['gain_stabilization'] = (int(self.user['gs_mode']) & 0xF)
        self.fields['run_mode'] = \
            (int(self.user['hv_on']) & 0x1) + \
            (int(self.user['hv_ctrl']) & 0x1)*2  + \
            (int(self.user['hv_power']) & 0x1)*4
            
        self.fields['run_action'] = \
            (int(self.user['clear_alarm']) & 0x1) + \
            (int(self.user['clear_logger']) & 0x1)*2 + \
            (int(self.user['clear_wallclock']) & 0x1)*4 

class arm_cal:
    def __init__(self):
        self.registers = [0.0] * 64
        self.fields = {}
        self.user = {}

        self.wr_type = ARM_WRITE
        self.rd_type = ARM_READ
        self.cmd_addr = ARM_CAL
        self.data_type = 'f'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 4

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        """
            Copy ARM calibration registers into named fields
            :return: None
        """
        self.fields = {
            'lut_len': self.registers[0],  # Number of entries in the LUT; Last entry always is at offset 63
            'lut_tmin': self.registers[1],  # Minimum temperature in the lookup table; Typically -30°C
            'lut_dt': self.registers[2],  # Temperature step size in the lookup table; Typically 5°C
            'lut_ov': [d for d in self.registers[3:23]],  # Change of operating voltage vs temperature
            'lut_dg': [d for d in self.registers[23:43]],  # Change of digital gain vs temperature
            'lut_led': [d for d in self.registers[43:63]], # Change of LED target vs temperature
            'lut_mode': self.registers[63],  # bit 0 -> lock bit
        }

    def fields_2_registers(self):
        """
            Copy ARM calibration fields into the register list
            :return: None
        """
        self.registers = [0.0]*64
        self.registers[0] = self.fields['lut_len']
        self.registers[1] = self.fields['lut_tmin']
        self.registers[2] = self.fields['lut_dt']
        self.registers[3:23] = [d for d in self.fields['lut_ov']]  # Make a deep copy
        self.registers[23:43] = [d for d in self.fields['lut_dg']]  # Make a deep copy
        self.registers[43:63] = [d for d in self.fields['lut_led']]  # Make a deep copy
        self.registers[63] = self.fields['lut_mode']

    def fields_2_user(self):
        pass

    def user_2_fields(self):        
        pass


class arm_logger:
    def __init__(self):
        self.logger_length = 1024
        self.registers = [0.0] * (2 * self.logger_length)
        self.fields = {}
        self.user = {}

        self.wr_type = ARM_WRITE
        self.rd_type = ARM_READ
        self.cmd_addr = ARM_LPSRAM
        self.data_type = 'f'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 4

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        """
            Copy ARM histogram registers into named fields
            :return: None
        """
        length = int(self.registers[0]);
        self.fields = {
            'length': length,
            'idx': self.registers[1],
            'var_0': self.registers[2: length+2],  # Log of variable 0
            'var_1': self.registers[length+2: ]    # Log of variable 1
        }

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        idx = int(self.fields['idx'])        
        if idx == self.logger_length-1:
            var_0 = self.fields['var_0']
            var_1 = self.fields['var_1']
        else:
            var_0 = self.fields['var_0'][idx+1: ] + self.fields['var_0'][0: idx+1]
            var_1 = self.fields['var_1'][idx+1: ] + self.fields['var_1'][0: idx+1]
        self.user = {'var_0': var_0, 'var_1': var_1}


    def user_2_fields(self):
        pass