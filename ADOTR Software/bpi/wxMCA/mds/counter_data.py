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
            'op_voltage': self.registers[0],  # Current operating voltage
            'voltage_target': self.registers[1],  # Computed target voltage from request (directly or with correction applied)
            'set_voltage': self.registers[2],  # Current operating voltage set by the DAC (so that op_volt matches req_volt (directly or with correction applied)
            'dg_target': self.registers[3],  # Current operating voltage set by the DAC (so that op_volt matches req_volt (directly or with correction applied)
            'cpu_temperature': self.registers[4],  # Current ARM M0+ temperature
            'x_temperature': self.registers[5],  # Current temperature measured by the external temperature sensor.
            'avg_temperature': self.registers[6],  # Current temperature average
            'wall_clock_time': self.registers[7],  # wall_clock time
            'run_status': int(self.registers[8]),  # Run status bit field; bit_0-> counter_active, 1-> counter bank, 2-> alarm_active;
            'run_time_sample': self.registers[9],  # Run time of the foreground counter (resolution: 1.365333ms)
            'sample_events': self.registers[10],  # Number of sample events
            'count_rate': self.registers[11],  # Foreground count rate 
            'count_rate_err': self.registers[12],  # Foreground count rate 2-sigma error
            'run_time_bck': self.registers[13],  # Run time of the background counter (1LSB = 65536/48e6 = 1.365333ms)
            'bck_events': self.registers[14],  # Number of background events
            'count_rate_bck': self.registers[15],  # Background count rate
            'count_rate_bck_err': self.registers[16],  # Background count rate 2-sigma error
            'count_rate_diff': self.registers[17],  # Foreground - Background count rate
            'count_rate_diff_err': self.registers[18],  # Foreground - Background count rate, 2-sigma error
            'bck_probability': self.registers[19],  # Alarm probability, given foreground and background counts
            'bck_low_probability': self.registers[20],  # Most alarmist: P(counts > N+sigma(N) | mu-sigma(mu))
            'bck_high_probability': self.registers[21],  # Most cautious: P(counts > N-sigma(N) | mu+sigma(mu))
            'ts_ready': self.registers[22],  # Time slice alarming system is ready
            'ts_alarm': self.registers[23],  # 1 if there is an active alarm
            'ts_net': self.registers[24],  # Net counts above background during the last L time slices
            'ts_bck': self.registers[25],  # Background counts above background during the last L time slices
            'ts_prob': self.registers[26],  # Probability that net is caused by the accepted background rate.
            'ts_reset': self.registers[27], # Time slice counters were reset due to an extended alarm (longer than arm_ctrl[AC_TS_H])
            'real_time': self.registers[37], # Run time, not corrected for dead time
            'dead_time': self.registers[38] # dead time 
        }

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        """
            Convert some raw fields into more practical user data, using SI units:
            :return: None
        """
        self.user = {
            'wall_clock_time': self.fields['wall_clock_time']*65536/48.0e6,
            'counter_active': self.fields['run_status'] & 1, # 
            'active_bank': (self.fields['run_status'] >> 1) & 1 # The bank currently acquiring data
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
            'peltier': self.registers[1],  # Either fixed peltier power (0 to 100%) or maximum power; To allow a host control loop
            'temp_ctrl': self.registers[2],  # 0-> Use ARM temperature sensor; 1-> Use external LTC2997 sensor; [4:8]=> (0-> no peltier; 1-> constant; 2-> ctrl-loop)
            'temp_target': self.registers[3],  # Temperature target for cooled systems
            'temp_period': self.registers[4],  # Update period for temperature measurements
            'temp_weight': self.registers[5],  # Weight for geometric averaging: Purpose is noise reduction or matching thermal relaxation
            'cal_temp': self.registers[6],  # Temperature (in deg C) at which the detector was calibrated
            'cal_ov': self.registers[7],  # Operating voltage when the detector was calibrated
            'cal_dg': self.registers[8],  # Digital gain for compressing histograms
            'cal_target': self.registers[9],  # Target value for ROI or LED measured response; used with gain_stab=2,3
            'cal_roi_low': self.registers[10],  # [roi_low : roi_high] => Region of interest used when gain-stabilizing on ROI
            'cal_roi_high': self.registers[11],  # 

            'run_mode': int(self.registers[12]), # up to 24 control bits
            'run_action': int(self.registers[13]), # self-clearing action items
            'run_time_sample': self.registers[14],  # Requested run time for a counting acquisition; 0-> forever
            'run_time_bck': self.registers[15],  # Requested run time for a background counting acquisition; 0-> forever
            'alarm_thr': self.registers[16],  # Alarm threshold for foreground/bck;  If alarm_probability less than this, blink a light or send a pulse on digital out.
            'roi_low': self.registers[17],  # ROI for count rate and alarming purpose
            'roi_high': self.registers[18],  # ROI for count rate and alarming purpose
            'ts_period': self.registers[19],  # Time slice period in seconds.
            'ts_reset': self.registers[20],  # Reset time-slice alarm system
            'ts_L': self.registers[21],  # Summation length for alarm computation
            'ts_H': self.registers[22],  # History length for alarms; maximum length of alarm before resetting
            'ts_wait': self.registers[23],  # Minimum wait time until we will accept alarms, having sufficient background accuracy
            'ts_B': self.registers[24],  # Background averaging length
            'ts_eps': self.registers[25],  # Alarm threshold for time-slice system
            'trigger_width': self.registers[26],  # Output pulse width, for alarms 
            'trigger_threshold': self.registers[27],  # Trigger threshold in V; typically 0.020
            'integration_time': self.registers[28],  # Light pulse integration time; 0.458e-6 for NaI
            'led_width': self.registers[29],  # Width of the LED drive pulse
            'cal_events': self.registers[30],  # Number of events used with LED or ROI calibration
            'baud': self.registers[31],  # Baud rate for serial communication
            'holdoff': self.registers[32],  # Hold-off in micro-seconds (for ZnS(Ag) and other slow scintillators)
            'xctrl_0': self.registers[33],  # Reserved
            'xctrl_1': self.registers[34],  # Reserved
            'xctrl_2': self.registers[35],  # Reserved
            'xctrl_3': self.registers[36],  # Reserved
            'xctrl_4': self.registers[37],  # Reserved
            'xctrl_5': self.registers[38],  # Reserved
            'xctrl_6': self.registers[39],  # Reserved
            'xctrl_7': self.registers[40],  # Reserved
        }

    def fields_2_registers(self):
        """
            Copy ARM control fields into the register list
            :return: None
        """
        self.registers = [0]*64
        self.registers[0] = float(self.fields['gain_stabilization'])
        self.registers[1] = float(self.fields['peltier'])
        self.registers[2] = float(self.fields['temp_ctrl'])
        self.registers[3] = float(self.fields['temp_target'])
        self.registers[4] = float(self.fields['temp_period'])
        self.registers[5] = float(self.fields['temp_weight'])
        self.registers[6] = self.fields['cal_temp']
        self.registers[7] = self.fields['cal_ov']
        self.registers[8] = self.fields['cal_dg']
        self.registers[9] = self.fields['cal_target']
        self.registers[10] = self.fields['cal_roi_low']
        self.registers[11] = self.fields['cal_roi_high']
        self.registers[12] = float(self.fields['run_mode'])
        self.registers[13] = float(self.fields['run_action'])
        self.registers[14] = float(self.fields['run_time_sample'])
        self.registers[15] = float(self.fields['run_time_bck'])
        self.registers[16] = float(self.fields['alarm_thr'])
        self.registers[17] = float(self.fields['roi_low'])
        self.registers[18] = float(self.fields['roi_high'])
        self.registers[19] = float(self.fields['ts_period'])
        self.registers[20] = float(self.fields['ts_reset'])
        self.registers[21] = float(self.fields['ts_L'])
        self.registers[22] = float(self.fields['ts_H'])
        self.registers[23] = float(self.fields['ts_wait'])
        self.registers[24] = float(self.fields['ts_B'])
        self.registers[25] = float(self.fields['ts_eps'])
        self.registers[26] = float(self.fields['trigger_width'])
        self.registers[27] = float(self.fields['trigger_threshold'])
        self.registers[28] = float(self.fields['integration_time'])
        self.registers[29] = float(self.fields['led_width'])
        self.registers[30] = float(self.fields['cal_events'])
        self.registers[31] = float(self.fields['baud'])
        self.registers[32] = float(self.fields['holdoff'])
        self.registers[33] = float(self.fields['xctrl_0'])
        self.registers[34] = float(self.fields['xctrl_1'])
        self.registers[35] = float(self.fields['xctrl_2'])
        self.registers[36] = float(self.fields['xctrl_3'])
        self.registers[37] = float(self.fields['xctrl_4'])
        self.registers[38] = float(self.fields['xctrl_5'])
        self.registers[39] = float(self.fields['xctrl_6'])
        self.registers[40] = float(self.fields['xctrl_7'])


    def fields_2_user(self):
        self.user = {
            'gs_mode': int(self.fields['gain_stabilization']) & 0xF, # 0->OFF, 1->LUT, 2->LED, 3->ROI(reserved)
            'gs_events': (int(self.fields['gain_stabilization']) >> 4) & 0xF, # num_events = 2**n
            
            'histogram_run': int(self.fields['run_mode']) & 0x1,
            'acq_type': (int(self.fields['run_mode']) >> 1) & 0x7,
            'active_bank': (int(self.fields['run_mode']) >> 4) & 0x1,
            'read_clear': (int(self.fields['run_mode']) >> 5) & 0x1,  # Enable read_and_clear feature for counting
            'two_bank': (int(self.fields['run_mode']) >> 6) & 0x1,  # Enable automatic selection of the inactive bank for reading and clearing
            "histo_2k": (int(self.fields['run_mode']) >> 7) & 0x1,  # Use one 2Kx32 histogram
            'sample_alarm': (int(self.fields['run_mode']) >> 8) & 0x1,  # Compute alarm probability for foreground vs background 
            'time_slice': (int(self.fields['run_mode']) >> 9) & 0x1,  # Activate time slice system and dynamic alarming
            
            'clear_statistics': int(self.fields['run_action']) & 0x1,
            'clear_histogram': (int(self.fields['run_action']) >> 1) & 0x1,
            'clear_alarm': (int(self.fields['run_action']) >> 2) & 0x1,
            'clear_logger': (int(self.fields['run_action']) >> 3) & 0x1
        }
        

    def user_2_fields(self):
        self.fields['gain_stabilization'] = \
            (int(self.user['gs_mode']) & 0xF) + ((int(self.user['gs_events']) & 0xF)<<4)
        self.fields['run_mode'] = \
            (int(self.user['histogram_run']) & 0x1) + \
            (int(self.user['acq_type']) & 0x7)*2 + \
            (int(self.user['active_bank']) & 0x1)*0x10 + \
            (int(self.user['read_clear']) & 0x1)*0x20 + \
            (int(self.user['two_bank']) & 0x1)*0x40 + \
            (int(self.user['histo_2k']) & 0x1)*0x80 + \
            (int(self.user['sample_alarm']) & 0x1)*0x100 + \
            (int(self.user['time_slice']) & 0x1)*0x200 
            
        self.fields['run_action'] = \
            (int(self.user['clear_statistics']) & 0x1) + \
            (int(self.user['clear_histogram']) & 0x1)*2 + \
            (int(self.user['clear_alarm']) & 0x1)*4 + \
            (int(self.user['clear_logger']) & 0x1)*8

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

        
class arm_histogram:
    def __init__(self):
        self.registers = [0] * 1040
        self.fields = {}
        self.user = {}

        self.wr_type = ARM_WRITE
        self.rd_type = ARM_READ
        self.cmd_addr = ARM_HISTO
        self.data_type = 'I'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 4

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        """
            Copy ARM histogram registers into named fields
            :return: None
        """
        self.fields = {
            'run': self.registers[0] & 0x1,  # Histogram DAQ is active
            'run_time': self.registers[1],  # Run time measured by wall clock; 1LSB=1.365ms.
            'dead_time': self.registers[2],  # Dead time measured by wall clock; 1LSB=1.365ms.
            'events': self.registers[3],  # Number of acquired events
            'live_time': self.registers[4],  # Computed live time, in milliseconds
            'count_rate': self.registers[5],  # Computed count rate, dead-time corrected, in milli-cps
            'lt_ratio': self.registers[6],  # Life time ratio: 1.0e6*histo[STATS_LT]/bck[STATS_LT] (only used by ARM_DIFF)
            'xdead_time': self.registers[7],  # Extended dead time measured by wall clock; 1LSB=1.365ms.
            'wc_start': self.registers[14],  # Wall clock time at start; 1LSB = 65536/48e6=1.365ms
            'live_time_max': self.registers[15],  # Live time limit for data acquisition, in seconds
            'histogram': self.registers[16: ]  # The 1K×32-bit energy histogram.
        }

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        self.user = {
            'wc_start': self.fields['wc_start'] * 65536/48.0e6,
            'run_time': self.fields['run_time'] * 65536/48.0e6,
            'dead_time': self.fields['dead_time'] * 65536/48.0e6,
            'xdead_time': self.fields['xdead_time'] * 65536/48.0e6,
            'events': self.fields['events'],
            'live_time': self.fields['live_time'] / 1000.0,
            'count_rate': self.fields['count_rate'] / 1000.0
        }

    def user_2_fields(self):
        pass

       
class arm_histo_2k:
    def __init__(self):
        self.registers = [0] * 1864
        self.fields = {}
        self.user = {}

        self.wr_type = ARM_WRITE
        self.rd_type = ARM_READ
        self.cmd_addr = ARM_HISTO
        self.data_type = 'I'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 4

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        """
            Copy ARM histogram registers into named fields
            :return: None
        """
        self.fields = {
            'run': self.registers[0] & 0x1,  # Histogram DAQ is active
            'run_time': self.registers[1],  # Run time measured by wall clock; 1LSB=1.365ms.
            'events': self.registers[2],  # Number of acquired events
            'live_time': self.registers[3],  # Computed live time, in milliseconds
            'count_rate': self.registers[4],  # Computed count rate, dead-time corrected, in milli-cps
            'wc_start': self.registers[14],  # Wall clock time at start; 1LSB = 65536/48e6=1.365ms
            'live_time_max': self.registers[15],  # Live time limit for data acquisition, in seconds
            'histogram': self.registers[16: ]  # The 2K×32-bit energy histogram.
        }

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        self.user = {
            'wc_start': self.fields['wc_start'] * 65536/48.0e6,
            'run_time': self.fields['run_time'] * 65536/48.0e6,
            'events': self.fields['events'],
            'live_time': self.fields['live_time'] / 1000.0,
            'count_rate': self.fields['count_rate'] / 1000.0
        }

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