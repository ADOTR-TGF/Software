#!/usr/bin/python
#
# version 1.0
from __future__ import division

import math

# FPGA command types
FPGA_WRITE = 1
FPGA_READ = 2

# ARM command types
ARM_WRITE = 3
ARM_READ = 4

# ARM command addresses
ARM_VERSION = 0  # Read ARM software and hardware version
ARM_STATUS = 1  # Operational control of the slow-control system (R/W)
ARM_CTRL = 2  # Operational control of the slow-control system (R/W)
ARM_CAL = 3  # Calibration and LUT in RAM
ARM_LPSRAM = 7  # Read from the up to 8kB low-power SRAM

# FPGA module addresses
MA_CONTROLS = 0  # Access FPGA control registers
MA_STATISTICS = 1  # Access FPGA statistics registers
MA_RESULTS = 2  # Access FPGA results registers (version, telemetry, calibration)
MA_HISTOGRAM = 3  # Access FPGA histogram memory
MA_TRACE = 4  # Access FPGA trace memory
MA_LISTMODE = 5  # Access FPGA list mode memory
MA_WEIGHTS = 6  # Access FPGA weights memory
MA_ACTIONS = 7  # Access FPGA action registers, eg to start DAQ
MA_TIME_SLICE = 8  # Access FPGA time slice registers

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

class fpga_ctrl:
    """
        Note that the fpga_ctrl total data size for USB transfer must be 64 bytes.  The ARM in the MCA_3K then only writes as many data as necessary.
    """
    def __init__(self):
        self.registers = [0]*16
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6
        
        self.wr_type = FPGA_WRITE
        self.rd_type = FPGA_READ
        self.cmd_addr = MA_CONTROLS
        self.data_type = 'H'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 2

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        """
            Convert FPGA control register values into a control register dictionary which has names for the bit fields.
            This function defines the keys for self.fields.  The fields are a complete description of all registers.
            :return: None
        """
        self.fields = dict()  # We make self.fields a dictionary
        self.fields['fine_gain'] = int(self.registers[0])
        self.fields['baseline_threshold'] = int(self.registers[1]) & 0x03FF
        self.fields['cr1_upper'] = (int(self.registers[1]) >> 10) & 0x003F
        self.fields['pulse_threshold'] = int(self.registers[2]) & 0x03FF
        self.fields['cr2_upper'] = (int(self.registers[2]) >> 10) & 0x003F
        self.fields['hold_off_time'] = int(self.registers[3])
        self.fields['integration_time'] = int(self.registers[4])
        self.fields['roi_bounds'] = int(self.registers[5])
        self.fields['trigger_delay'] = int(self.registers[6]) & 0x03FF
        self.fields['cr6_upper'] = (int(self.registers[6]) >> 10) & 0x003F

        self.fields['ctrl_7'] = self.registers[7]

        self.fields['run_time_0'] = self.registers[8]
        self.fields['run_time_1'] = self.registers[9]

        self.fields['short_it'] = int(self.registers[10])
        self.fields['put'] = int(self.registers[11])

        # CR12
        val = int(self.registers[12])
        self.fields['ecomp'] = val & 0xF
        self.fields['pcomp'] = (val & 0xF0) >> 4
        self.fields['gain_select'] = (val & 0xF00) >> 8
        self.fields['cr12_upper'] = (val & 0xF000) >> 12

        # CR13
        self.fields['ctrl_13'] = self.registers[13]

        # CR14
        val = int(self.registers[14])
        self.fields['led_repeat_time'] = val & 0xFF
        self.fields['led_pulse_width'] = (val >> 8) & 0xFF
        

        # CR15
        val = int(self.registers[15])
        self.fields['ha_mode'] = int((val & 0x1))  # 0-> energy, 1->amplitude
        self.fields['trace_mode'] = int((val & 0x2) >> 1)  # 0-> triggered, 1->validated
        # List mode: 0-> 16-bit energy + 32-bit time, 1->16-bit energy + 16-bit PSD + 16-bit time
        self.fields['lm_mode'] = int((val & 0x4) >> 2)
        self.fields['led_on'] = int((val & 0x8) >> 3)
        self.fields['rtlt'] = int((val & 0x30) >> 4)
        self.fields['sel_led'] = int((val & 0x40) >> 6)
        self.fields['daq_mode'] = int((val & 0x80) >> 7)
        self.fields['nai_mode'] = int((val & 0x100) >> 8)
        self.fields['psd_on'] = int((val & 0x200) >> 9)
        self.fields['psd_select'] = int((val & 0x400) >> 10)
        self.fields['cr15_upper'] = int((val & 0xF800) >> 11)

    def fields_2_registers(self):
        """
            Compute the values of the control registers from the fields dictionary.
            :return: None
        """
        self.registers = [0] * 16
        self.registers[0] = int(self.fields['fine_gain'])
        self.registers[1] = (int(self.fields['baseline_threshold']) & 0x03FF) + (int(self.fields['cr1_upper']) << 10)
        self.registers[2] = (int(self.fields['pulse_threshold']) & 0x03FF) + (int(self.fields['cr2_upper']) << 10)
        self.registers[3] = int(self.fields['hold_off_time'])
        self.registers[4] = int(self.fields['integration_time'])
        self.registers[5] = int(self.fields['roi_bounds'])
        self.registers[6] = (int(self.fields['trigger_delay']) & 0x03FF) + (int(self.fields['cr6_upper']) << 10)

        self.registers[7] = int(self.fields['ctrl_7'])

        self.registers[8] = int(self.fields['run_time_0'])  # lower 16-bit word
        self.registers[9] = int(self.fields['run_time_1'])  # upper 16-bit word

        self.registers[10] = int(self.fields['short_it'])
        self.registers[11] = int(self.fields['put'])

        self.registers[12] = (int(self.fields['ecomp']) & 0xF) + ((int(self.fields['pcomp']) & 0xF) << 4) + \
                             ((int(self.fields['gain_select']) & 0xF) << 8) + \
                             ((int(self.fields['cr12_upper']) & 0xF) << 12)

        self.registers[13] = int(self.fields['ctrl_13'])

        self.registers[14] = (int(self.fields['led_repeat_time']) & 0xFF) + \
                     ((int(self.fields['led_pulse_width']) & 0xFF) << 8) 
        

        # Specific data acquisition modes for histogram, list mode and trace
        self.registers[15] = (int(self.fields['ha_mode']) & 1) + (int(self.fields['trace_mode']) & 1) * 0x2 + \
                             (int(self.fields['lm_mode']) & 1) * 0x4 + (int(self.fields['led_on']) & 1) * 0x8 + \
                             (int(self.fields['rtlt']) & 3) * 0x10 + (int(self.fields['sel_led']) & 1) * 0x40 + \
                             (int(self.fields['daq_mode']) & 1) * 0x80 + (int(self.fields['nai_mode']) & 1) * 0x100 + \
                             (int(self.fields['psd_on']) & 1) * 0x200 + (int(self.fields['psd_select']) & 1) * 0x400 + \
                             (int(self.fields['cr15_upper']) & 0x1F) * 0x800

    def fields_2_user(self):
        """
            Convert a few field values into physical quantities in SI units; times are in seconds, thresholds are in V.
            :return: None
        """
        self.user = {
            'digital_gain': self.fields['fine_gain'] / 2**self.fields['ecomp'] * 40.0e6/self.adc_sr,
            'integration_time': self.fields['integration_time']/self.adc_sr,
            'hold_off_time': self.fields['hold_off_time']/self.adc_sr,
            'short_it': self.fields['short_it']/self.adc_sr,
            'baseline_threshold': self.fields['baseline_threshold']/1000.0,
            'pulse_threshold': self.fields['pulse_threshold']/1000.0,
            'trigger_delay': self.fields['trigger_delay']/self.adc_sr,
            'roi_low': (int(self.fields['roi_bounds']) & 0xFF)*16,  # Unit is MCA bins
            'roi_high': (int(self.fields['roi_bounds']) & 0xFF00)//16,  # Unit is MCA bins
            'run_time': (self.fields['run_time_1']*0x10000 + self.fields['run_time_0'])*0x10000/self.adc_sr
        }

    def user_2_fields(self):
        """
            Convert user values from physical quantities in SI units into numerical fields
            :return: None
        """
        fg = int(self.user['digital_gain'] * self.adc_sr / 40.0e6)
        if fg > 0:
            ecomp = 0
            while fg < 16384:
                fg *= 2
                ecomp += 1
        else:  # Avoid infinite loop if fg==0
            fg = 16384
            ecomp = 2
            
        self.fields['fine_gain'] = fg
        self.fields['ecomp'] = ecomp
        self.fields['integration_time'] = int(self.user['integration_time'] * self.adc_sr + 0.5)
        self.fields['hold_off_time'] = int(self.user['hold_off_time'] * self.adc_sr + 0.5)
        self.fields['short_it'] = int(self.user['short_it'] * self.adc_sr + 0.5)
        self.fields['trigger_delay'] = int(self.user['trigger_delay'] * self.adc_sr + 0.5)
        self.fields['baseline_threshold'] = int(self.user['baseline_threshold'] * 1000.0 + 0.5) & 0x3FF
        self.fields['pulse_threshold'] = int(self.user['pulse_threshold'] * 1000.0 + 0.5) & 0x3FF
        self.fields['roi_bounds'] = self.user['roi_low'] // 16 + self.user['roi_high'] * 16
        rt = int(self.user['run_time']*self.adc_sr/0x10000)
        self.fields['run_time_0'] = rt & 0xFFFF
        self.fields['run_time_1'] = (rt & 0xFFFF0000) >> 16


class fpga_action:
    """
        Note that the fpga_action total data size for USB transfer must be 64 bytes.  The ARM in the MCA_3K then only writes as many data as necessary.
    """

    def __init__(self):
        self.registers = [0] * 4
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.wr_type = FPGA_WRITE
        self.rd_type = FPGA_READ
        self.cmd_addr = MA_ACTIONS
        self.data_type = 'H'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 2

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        """
            Convert FPGA action register values into a control register dictionary which has names for the bit fields.
            This function defines the keys for self.fields.  The fields are a complete description of all registers.
            :return: None
        """

        self.fields = dict()  # We make act_d a dictionary

        # AR0
        val = int(self.registers[0])
        self.fields['clear_histogram'] = val & 0x1
        self.fields['clear_statistics'] = (val & 0x2) >> 1
        self.fields['clear_trace'] = (val & 0x4) >> 2
        self.fields['clear_list_mode'] = (val & 0x8) >> 3
        self.fields['clear_led'] = (val & 0x10) >> 4
        self.fields['ut_run'] = (val & 0x20) >> 5
        self.fields['clear_roi'] = (val & 0x40) >> 6
        self.fields['ar0_upper'] = (val & 0xFF80) >> 7

        # AR1
        self.fields['ar1'] = int(self.registers[1]) & 0xFFFF

        # AR2
        val = int(self.registers[2])
        self.fields['histo_run'] = (val & 0x1)
        self.fields['trace_run'] = (val & 0x2) >> 1
        self.fields['lm_run'] = (val & 0x4) >> 2
        self.fields['suspend'] = (val & 0x8) >> 3
        self.fields['segment_enable'] = (val & 0x10) >> 4
        self.fields['segment'] = (val & 0x20) >> 5
        self.fields['x_alarm'] = (val & 0x40) >> 6
        self.fields['x_alarm_enable'] = (val & 0x80) >> 7
        self.fields['ar2_upper'] = (val & 0xFF00) >> 8

        # AR3
        self.fields['ar3'] = int(self.registers[3]) & 0xFFFF

        
    def fields_2_registers(self):
        """
            Compute the values of the control registers from the fields dictionary.
            :return: None
        """
        for key in self.fields:
            self.fields[key] = int(self.fields[key])
            
        self.registers = [0]*4
        
        # AR0
        self.registers[0] = (self.fields['clear_histogram'] & 0x1) + (self.fields['clear_statistics'] & 0x1)*0x2 + \
                            (self.fields['clear_trace'] & 0x1)*0x4 + (self.fields['clear_list_mode'] & 0x1)*0x8 + \
                            (self.fields['clear_led'] & 0x1)*0x10 + (self.fields['ut_run'] & 0x1)*0x20 + \
                            (self.fields['clear_roi'] & 0x1)*0x40 + (self.fields['ar0_upper'] & 0x1FF)*0x80
        
        # AR1
        self.registers[1] = self.fields['ar1'] & 0xFFFF

        # AR2
        self.registers[2] = (self.fields['histo_run'] & 0x1) + (self.fields['trace_run'] & 0x1)*0x2 + \
                            (self.fields['lm_run'] & 0x1)*0x4 + (self.fields['segment'] & 0x1)*0x8 + \
                            (self.fields['segment_enable'] & 0x1)*0x10 + (self.fields['suspend'] & 0x1)*0x20 + \
                            (self.fields['x_alarm'] & 0x1)*0x40 + (self.fields['x_alarm_enable'] & 0x1)*0x80 + \
                            (self.fields['ar2_upper'] & 0xFF)*0x100

        # AR3
        self.registers[3] = self.fields['ar3'] & 0xFFFF
        
    def fields_2_user(self):
        self.user = {}

    def user_2_fields(self):
        pass


class fpga_statistics:
    def __init__(self):
        self.registers = [0] * 16
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.wr_type = FPGA_WRITE
        self.rd_type = FPGA_READ
        self.cmd_addr = MA_STATISTICS
        self.data_type = 'I'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 4

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        """
            Convert raw statistics register values into named fields for events, counts, and dead time.
            All are uint32_t numbers. This function defines the keys for self.fields.
            :return: None
        """
        self.fields = {
            'bank_0': {
                'ct': self.registers[0],  # Clock counts (1LSB = 65536 ADC sampling clock cycles)
                'ev': self.registers[1],  # Accepted events
                'ts': self.registers[2],  # Recognized triggers
                'dt': self.registers[3],  # Dead time in clock counts (1LSB = 65536 ADC sampling clock cycles)
                'xev0': self.registers[8],    # Number of external counts by x_counter 0
                'xev1': self.registers[9],    # Number of external counts by x_counter 1
                'xev2': self.registers[10],   # Number of external counts by x_counter 2
                'xev3': self.registers[11]    # Number of external counts by x_counter 3
            },
            'bank_1': {
                'ct': self.registers[4],  # Clock counts (1LSB = 65536 ADC sampling clock cycles)
                'ev': self.registers[5],  # Accepted events
                'ts': self.registers[6],  # Recognized triggers
                'dt': self.registers[7],  # Dead time in clock counts (1LSB = 65536 ADC sampling clock cycles)
                'xev0': self.registers[12],   # Number of external counts by x_counter 0
                'xev1': self.registers[13],   # Number of external counts by x_counter 1
                'xev2': self.registers[14],   # Number of external counts by x_counter 2
                'xev3': self.registers[15]    # Number of external counts by x_counter 3
            }
        }

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        """
            Convert the events, counts, and dead time fields in to physical quantities: s, and cps
            All values are double floats. This function defines the keys for self.fields.
            :return: None
        """
        self.user = {'bank_0': {}, 'bank_1': {}}
        for bank in ['bank_0', 'bank_1']:
            if self.fields[bank]['ct'] > 0:
                rt = self.fields[bank]['ct']*65536/self.adc_sr
                dt = self.fields[bank]['dt']*65536/self.adc_sr
                self.user.update({
                    bank: {
                        'run_time': rt,
                        'dead_time': dt,
                        'event_rate': self.fields[bank]['ev']/rt,
                        'trigger_rate': self.fields[bank]['ts']/rt,
                        'pulse_rate': self.fields[bank]['ts']/(rt-dt) if rt > dt else 0,
                        'xev0_rate': self.fields[bank]['xev0'] / rt,
                        'xev1_rate': self.fields[bank]['xev1'] / rt,
                        'xev2_rate': self.fields[bank]['xev2'] / rt,
                        'xev3_rate': self.fields[bank]['xev3'] / rt,
                        'event_rate_err': 2.0*math.sqrt(self.fields[bank]['ev'])/rt,  # 2-sigma error
                        'trigger_rate_err': 2.0*math.sqrt(self.fields[bank]['ts'])/rt,
                        'pulse_rate_err': 2.0*math.sqrt(self.fields[bank]['ts'])/(rt-dt) if rt > dt else 0,
                        'xev0_rate_err': 2.0*math.sqrt(self.fields[bank]['xev0']) / rt,
                        'xev1_rate_err': 2.0*math.sqrt(self.fields[bank]['xev1']) / rt,
                        'xev2_rate_err': 2.0*math.sqrt(self.fields[bank]['xev2']) / rt,
                        'xev3_rate_err': 2.0*math.sqrt(self.fields[bank]['xev3']) / rt
                    }
                })
            else:
                self.user.update({
                    bank: {
                        'run_time': 0,
                        'dead_time': 0,
                        'event_rate': 0,
                        'trigger_rate': 0,
                        'pulse_rate': 0,
                        'xev0_rate': 0,
                        'xev1_rate': 0,
                        'xev2_rate': 0,
                        'xev3_rate': 0,
                        'event_rate_err': 0,
                        'trigger_rate_err': 0,
                        'pulse_rate_err': 0,
                        'xev0_rate_err': 0,
                        'xev1_rate_err': 0,
                        'xev2_rate_err': 0,
                        'xev3_rate_err': 0
                    }
                })

    def user_2_fields(self):
        pass


class fpga_results:
    def __init__(self):
        self.registers = [0] * 16
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.wr_type = FPGA_WRITE
        self.rd_type = FPGA_READ
        self.cmd_addr = MA_RESULTS
        self.data_type = 'H'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 2

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        """
            Convert raw results register values into named fields for events, counts, and dead time.
            All are uint32_t numbers. This function defines the keys for self.fields.
            :return: None
        """
        self.fields = {
            'temperature': self.registers[0],  # 13-bit 2's complement no.; 1LSB = 1/16 K
            'dc_offset': self.registers[1],  # 16-bit DC offset; 1LSB = 1/64 mV
            'status': self.registers[2],  # DAQ status register
            'anode_current': self.registers[3] + 0x10000*self.registers[4],  # uint32_t anode current
            'roi_avg': self.registers[5],  # uint16_t average energy deposited in ROI (16x average mca bin)
            'version': self.registers[7] & 0xFF,  # Firmware version
            'adc_bits': (self.registers[7] // 256) & 0xF,  # Number of ADC bits
            'adc_sr': self.registers[6] & 0xFF,  # ADC sampling rate in mega-samples per second (MHz)
            'sensor': (self.registers[6] & 0x0F00)//256,  # 0,1-> PMT, 2->SiPM
            'sys_clk': (self.registers[6] & 0xF000)//2048,  # 0-> 24MHz, 1->12MHz
            'custom': self.registers[8],  # Customization number
            'build': self.registers[9],  # Build number increases with every release
            'rr_10': self.registers[10],  # Results register 10, uint16_t
            'rr_11': self.registers[11],  # Results register 11, uint16_t
            'rr_12': self.registers[12],  # Results register 12, uint16_t
        }

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        """
            Convert the results fields into physical quantities in SI units.  DAQ_done values are 0 or 1.
            All values are double floats. This function defines the keys for self.fields.
            :return: None
        """
        val = self.fields['temperature']
        if val & 0x1000:  # temperature is negative
            degc = ((val & 0x01FFF) - 8192) / 16.0
        else:
            degc = (val & 0x07FF) / 16.0
        gs = (self.fields['status'] & 0xF0)>>4  # status[7:4]=gain_select
        impedance = 1000
        if self.fields['sensor'] == 1: # PMT-3K
            impedance = 100 + (gs & 1) * 330.0 + (gs & 2) / 2 * 1000 + \
                        (gs & 4) / 4 * 3300.0 + (gs & 8) / 8 * 10000
        if self.fields['sensor'] == 2:  # SiPM-3K
            impedance = 10 + (gs & 1) * 15.0 + (gs & 2) / 2 * 49.9 + \
                        (gs & 4) / 4 * 150.0 + (gs & 8) / 8 * 499.9
            
        adc_voltage_range = 1.0  # in Volt
        dc_offset = self.fields['dc_offset']/64000  # DC-offset in Volt
        anode_current = 0
        # Test for sign bit: Negative numbers mean zero current (just noise)
        if self.fields['anode_current'] & 0x80000000 == 0:
            anode_current = self.fields['anode_current'] * adc_voltage_range / impedance * pow(2.0, -25.0)

        self.user = {
            'temperature': degc,  # Temperature in degree Celsius
            'dc_offset': dc_offset,  # DC-offset in Volt
            'histo_done': self.fields['status'] & 0x1,  # Histogram done
            'lm_done': (self.fields['status'] & 0x2)//0x2,  # List mode acquisition complete
            'trace_done': (self.fields['status'] & 0x4)//0x4,  # Trace acquisition complete
            'led_valid': (self.fields['status'] & 0x8)//0x8,  # Valid LED average in RR[10]
            'impedance': impedance,  # Transimpedance of the input amplifier in Ohms
            'max_volt': adc_voltage_range - dc_offset,  # Maximum pulse height in V
            'max_current': (adc_voltage_range - dc_offset) / impedance,  # Maximum anode pulse current in A
            'anode_current': anode_current,
            'adc_sr': self.fields['adc_sr'] * 1.0e6
        }

    def user_2_fields(self):
        pass


class fpga_histogram:
    def __init__(self):
        self.registers = [0] * 4096
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.wr_type = FPGA_WRITE
        self.rd_type = FPGA_READ
        self.cmd_addr = MA_HISTOGRAM
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


class fpga_list_mode:
    def __init__(self):
        self.registers = [0] * 1024
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.wr_type = FPGA_WRITE
        self.rd_type = FPGA_READ
        self.cmd_addr = MA_LISTMODE
        self.data_type = 'H'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 2

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        """
            Unpack the list mode data buffer into energy and time lists
            :return: None
        """
        mode = (self.registers[0] & 0x8000) // 0x8000
        num_events = self.registers[0] & 0xFFF

        self.fields = {
            'mode': mode,
            'num_events': num_events,
            'energies': self.registers[4::3]
        }
        if mode == 0:
            self.fields['times'] = [ t0 + (t1 << 16) for t0, t1 in zip(self.registers[5::3], self.registers[6::3])]
            self.fields['short_sums'] = []
        else:
            self.fields['times'] = self.registers[6::3]
            self.fields['short_sums'] = self.registers[5::3]

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        """
            Convert energy and time lists into seconds and mca_bins
            :return: None
        """
        self.user = {
            'energies': [e/16.0 for e in self.fields['energies']]
        }
        if self.fields['mode'] == 0:
            self.user['times'] = [t/self.adc_sr for t in self.fields['times']]
        else:
            self.user['times'] = [t*512.0/self.adc_sr for t in self.registers[3::3]]
            self.user['short_sums'] = [e/16.0 for e in self.fields['short_sums']]

    def user_2_fields(self):
        pass


class fpga_trace:
    def __init__(self):
        self.registers = [0]*1024
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.wr_type = FPGA_WRITE
        self.rd_type = FPGA_READ
        self.cmd_addr = MA_TRACE
        self.data_type = 'H'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 2

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        self.fields = {"trace": [t/32 if t < 32768 else (t-65536)/32 for t in self.registers]}

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        pass

    def user_2_fields(self):
        pass

    def trace_summary(self):
        self.user = {'pulse_found': -1}
        trace = self.registers
        adc_sr = self.adc_sr
        thr = 10*32
        b_thr = 3*32
        dc_val = trace[0]
        n0 = 0
        n1 = 0
        for n0, t in enumerate(trace[1:]):
            if abs(t - dc_val) < b_thr:
                dc_val = 7 / 8 * dc_val + t / 8
            elif (t - dc_val) > thr:
                break
        else:  # no pulse found
            tlen = len(trace)
            avg = sum(trace) / tlen
            std_dev = math.sqrt(sum([(t - avg) ** 2 / (tlen - 1) for t in trace]))
            mini = min(trace)
            maxi = max(trace)
            self.user = {'pulse_found': 0, 'mini': mini, 'maxi': maxi, 'std_dev': std_dev, 'avg': avg}

        if n0 > 3:
            avg = sum(trace[1:n0-1]) / (n0-2)
            std_dev = math.sqrt(sum([(t - avg) ** 2 / (n0-3) for t in trace]))
        else:
            std_dev = 0
            
        energy = 0
        for n1, t in enumerate(trace[n0:]):
            energy += trace[n1]
            if trace[n1] - dc_val < b_thr:
                break
        n1 += n0
        pulse = trace[n0:n1]
        mca_bin = energy  # Check how to map this into MCA bins (assuming some fixed digital gain)

        ymax = max(pulse)
        xmax = pulse.index(ymax)

        y10 = 0.1 * ymax
        y50 = 0.5 * ymax
        y90 = 0.9 * ymax

        p10 = [idx for idx, p in enumerate(pulse) if p > y10]
        xrise10 = p10[0]
        xfall10 = p10[-1]

        p90 = [idx for idx, p in enumerate(pulse) if p > y90]
        xrise90 = p90[0]
        xfall90 = p90[-1]

        rise_time = (xrise90 - xrise10) / adc_sr
        fall_time = (xfall10 - xfall90) / adc_sr
        peaking_time = (xmax - n0) / adc_sr

        p50 = [idx for idx, p in enumerate(pulse) if p > y50]
        fwhm = (p50[-1] - p50[0]) / adc_sr

        self.user = {'pulse_found': 1, 'mca_bin': mca_bin, 'ymax': ymax, 'rise_time': rise_time,
                     'peaking_time': peaking_time, 'fall_time': fall_time,
                     'fwhm': fwhm, 'dc_val': dc_val, 'std_dev': std_dev}

        return None


class fpga_weights:
    def __init__(self):
        self.registers = [0] * 1024
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.wr_type = FPGA_WRITE
        self.rd_type = FPGA_READ
        self.cmd_addr = MA_WEIGHTS
        self.data_type = 'H'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 2

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
            # mca_id byte 0: 0->preampBase, 1->arm-based MCA, 2->FPGA-based MCA, 3->with eMorpho FPGA;
            # mca_id byte 1: 1 for PMT, 2 for SiPM
            'mca_id': self.registers[0],
            'short_sn': self.registers[1],  # Optional 4-byte serial number, deprecated
            'unique_sn_0': self.registers[2],  # 1st 4 bytes of unique serial number
            'unique_sn_1': self.registers[3],  # 2nd 4 bytes of unique serial number
            'unique_sn_2': self.registers[4],  # 3rd 4 bytes of unique serial number
            'unique_sn_3': self.registers[5],  # 4th 4 bytes of unique serial number
            'arm_hw': self.registers[6],  # ARM/PCB hardware version 0x0100 => 1.0 (BCD)
            'arm_sw': self.registers[7],  # ARM software version 0x0100 => 1.0 (BCD)
            'arm_build': self.registers[8],  # ARM software build number
            'arm_custom_0': self.registers[9],  # ARM software customization code; 1st 4 bytes
            'arm_custom_1': self.registers[10],  # ARM software customization code; 2nd 4 bytes
            'fpga_version': self.registers[11],  # FPGA firmware version
            'fpga_build': self.registers[12],  # FPGA build number
            'fpga_custom_0': self.registers[13],  # FPGA customization number, 1st 4 bytes
            'fpga_custom_1': self.registers[14],  # FPGA customization number, 2nd 4 bytes
            'fpga_speed': self.registers[15]  # FPGA ADC sampling clock speed, in MHZ
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
                         '{:X}'.format(self.fields['unique_sn_2']) + '{:X}'.format(self.fields['unique_sn_3']),
            'fpga_speed': self.fields['fpga_speed']*1.0e6
        }

    def user_2_fields(self):
        pass


class arm_status:
    def __init__(self):
        self.registers = [0]*64
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
            'op_voltage': self.registers[0],  # Current SiPM operating voltage
            'voltage_target': self.registers[1],  # Computed target voltage from request, directly or with correction applied.
            'set_voltage': self.registers[2],  # Current operating voltage set by the DAC so that op_voltage == target_voltage
            'cpu_temperature': self.registers[3],  # Current ARM M0+ processor core temperature
            'x_temperature': self.registers[4],  # Current temperature measured by the external temperature sensor.
            'avg_temperature': self.registers[5],  # Current temperature average (from selected sensor)
            'dg_target': self.registers[6],  # Target digital gain from LUT
            'led_target': self.registers[7],  # Target LED value from LUT
            'wall_clock_time': self.registers[8],  # wall_clock time
            'op_status': self.registers[9],  # Operating status
            'supply_voltage': self.registers[10],  # Measured supply voltage
            'fpga_count': self.registers[11],  # Number of FPGA reboots since power on
            'led_value': self.registers[12],  # Actual LED value from FPGA
            'dc_offset': self.registers[13],  # DC-offset in mV (90<dc<130)
            'anode_current': self.registers[14],  # Anode current 
            'run_time_sample': self.registers[15],  # Run time of the foreground counter (resolution: 1.365333ms)
            'events': self.registers[16],  # Number of sample events
            'trigger_rate': self.registers[17],  # Number of sample triggers
            'dead_time': self.registers[18],  # Sample dead time
            'count_rate': self.registers[19],  # Foreground count rate 
            'count_rate_err': self.registers[20],  # Foreground count rate 2-sigma error
            'run_time_bck': self.registers[21],  # Run time of the background counter (1LSB = 65536/48e6 = 1.365333ms)
            'events_bck': self.registers[22],  # Number of sample events
            'trigger_rate_bck': self.registers[23],  # Number of sample triggers
            'dead_time_bck': self.registers[24],  # Sample dead time
            'count_rate_bck': self.registers[25],  # Background count rate
            'count_rate_bck_err': self.registers[26],  # Background count rate 2-sigma error
            'count_rate_diff': self.registers[27],  # Foreground - Background count rate
            'count_rate_diff_err': self.registers[28],  # Foreground - Background count rate, 2-sigma error
            'bck_probability': self.registers[29],  # Alarm probability, given foreground and background counts
            'bck_low_probability': self.registers[30],  # Most alarmist: P(counts > N+sigma(N) | mu-sigma(mu))
            'bck_high_probability': self.registers[31],  # Most cautious: P(counts > N-sigma(N) | mu+sigma(mu))
            'alarm_time': self.registers[32],  # Alarm count down until it turns off when alarm = 0_seconds
            'ts_ready': self.registers[33],  # Time slice alarming system is ready
            'ts_alarm': self.registers[34],  # 1 if there is an active alarm
            'ts_net': self.registers[35],  # Net counts above background during the last L time slices
            'ts_bck': self.registers[36],  # Background counts above background during the last L time slices
            'ts_prob': self.registers[37],  # Probability that net is caused by the accepted background rate.
            'ts_reset': self.registers[38]  # Time slice counters were reset due to an extended alarm (longer than arm_ctrl[AC_TS_H])
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
            'fpga_status': int(self.fields['op_status']) & 0x1,
            'alarm_status': (int(self.fields['op_status']) & 0x2)>>1
        }

    def user_2_fields(self):
        pass


class arm_ctrl:
    def __init__(self):
        self.registers = [0.0]*64
        self.fields = {}
        self.user = {}

        self.wr_type = ARM_WRITE
        self.rd_type = ARM_READ
        self.cmd_addr = ARM_CTRL
        self.data_type = 'f'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 4
        self.scintillators = {
            "NaI_Tl": 0, "Generic": 1
        }

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        """
            Copy ARM control registers into named fields
            :return: None
        """
        self.fields = {
            'gain_stabilization': self.registers[0],  # 0-> Use req_volt as is, else use: 1-> LUT, 2-> LED, 3-> ROI (reserved)
            'peltier': self.registers[1],  # Peltier cooling power or the maximum allowed power; ranging from 0% to 100%.
            'temp_ctrl': self.registers[2],  # 0-> Use ARM temperature sensor; 1-> Use external LTC2997 sensor; 2-> Use value in the temp_target field
            'temp_target': self.registers[3],  # Temperature target for Peltier cooling
            'temp_period': self.registers[4],  # Update period for temperature measurements
            'temp_weight': self.registers[5],  # Weight for geometric averaging:
                                              # Purpose is noise reduction or matching thermal relaxation
            'cal_temp': self.registers[6],  # Temperature (in deg C) at which the detector was calibrated
            'cal_ov': self.registers[7],  # Operating voltage when the detector was calibrated
            'cal_dg': self.registers[8],  # Digital gain in the FPGA when the detector was calibrated
            'cal_target': self.registers[9],  # Target value for ROI or LED measured response; used with gain_stabilization=2,3
            'cal_scint': self.registers[10],  # Scintillator type (eg NaI_Tl adjusts hold-off time vs temperature)
            'cal_par_0': self.registers[11],  # A control parameter for gain stabilization with implementation-dependent meaning.
            'fpga_reboot': self.registers[12],  # Time between forced FPGA reboots, in seconds; Set to 0 to turn this off.
            'run_mode': int(self.registers[13]), # up to 24 control bits
            'run_action': int(self.registers[14]), # self-clearing action items
            'run_time_sample': self.registers[15],  # Requested run time for a counting acquisition; 0-> forever
            'run_time_bck': self.registers[16],  # Requested run time for a background counting acquisition; 0-> forever
            'alarm_thr': self.registers[17],  # Alarm threshold for foreground/bck;  If alarm_probability less than this, blink a light or send a pulse on digital out.
            'ts_period': self.registers[18],  # Time slice period in seconds.
            'ts_reset': self.registers[19],  # Reset time-slice alarm system
            'ts_L': self.registers[20],  # Summation length for alarm computation
            'ts_H': self.registers[21],  # History length for alarms; maximum length of alarm before resetting
            'ts_wait': self.registers[22],  # Minimum wait time until we will accept alarms, having sufficient background accuracy
            'ts_B': self.registers[23],  # Background averaging length
            'ts_eps': self.registers[24],  # Alarm threshold for time-slice system
            'alarm_width': self.registers[25],  # Output pulse width, for alarms
            'baud': self.registers[26],  # Baud rate for serial communication
            'xctrl_0': self.registers[27],  # Used for logger control
        }

    def fields_2_registers(self):
        """
            Copy ARM control fields into the register list
            :return: None
        """
        self.registers = [0.0]*64
        self.registers[0] = self.fields['gain_stabilization']
        self.registers[1] = self.fields['peltier']
        self.registers[2] = self.fields['temp_ctrl']
        self.registers[3] = self.fields['temp_target']
        self.registers[4] = self.fields['temp_period']
        self.registers[5] = self.fields['temp_weight']
        self.registers[6] = self.fields['cal_temp']
        self.registers[7] = self.fields['cal_ov']
        self.registers[8] = self.fields['cal_dg']
        self.registers[9] = self.fields['cal_target']
        self.registers[10] = self.fields['cal_scint']
        self.registers[11] = self.fields['cal_par_0']
        self.registers[12] = self.fields['fpga_reboot']
        self.registers[13] = self.fields['run_mode']
        self.registers[14] = self.fields['run_action']
        self.registers[15] = float(self.fields['run_time_sample'])
        self.registers[16] = float(self.fields['run_time_bck'])
        self.registers[17] = self.fields['alarm_thr']
        self.registers[18] = self.fields['ts_period']
        self.registers[19] = self.fields['ts_reset']
        self.registers[20] = self.fields['ts_L']
        self.registers[21] = self.fields['ts_H']
        self.registers[22] = self.fields['ts_wait']
        self.registers[23] = self.fields['ts_B']
        self.registers[24] = self.fields['ts_eps']
        self.registers[25] = self.fields['alarm_width']
        self.registers[26] = self.fields['baud']
        self.registers[27] = self.fields['xctrl_0']
        
        
    def fields_2_user(self):
        self.user = {
            'gs_mode': int(self.fields['gain_stabilization']) & 0xF, # 0->OFF, 1->LUT, 2->LED, 3->ROI(reserved)
            
            'active_bank': (int(self.fields['run_mode'])) & 0x1,  # 0->sample, 1->background
            'sample_alarm': (int(self.fields['run_mode']) >> 1) & 0x1,  # Compute alarm probability for foreground vs background 
            'time_slice': (int(self.fields['run_mode']) >> 2) & 0x1,  # Activate time slice system and dynamic alarming
            
            'clear_statistics': (int(self.fields['run_action'])) & 0x1,
            'clear_alarm': (int(self.fields['run_action']) >> 1) & 0x1,
            'clear_logger': (int(self.fields['run_action']) >> 2) & 0x1,
            'clear_wall_clock': (int(self.fields['run_action']) >> 3) & 0x1
        }

    def user_2_fields(self):
        self.fields['gain_stabilization'] = \
            (int(self.user['gs_mode']) & 0xF) 
        self.fields['run_mode'] = \
            (int(self.user['active_bank']) & 0x1) + \
            (int(self.user['sample_alarm']) & 0x1)*0x2 + \
            (int(self.user['time_slice']) & 0x1)*0x4
            
        self.fields['run_action'] = \
            (int(self.user['clear_statistics']) & 0x1) + \
            (int(self.user['clear_alarm']) & 0x1)*2 + \
            (int(self.user['clear_logger']) & 0x1)*4 + \
            (int(self.user['clear_wall_clock']) & 0x1)*8


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
            'lut_ov': list(self.registers[3:23]),  # Change of operating voltage vs temperature
            'lut_dg': list(self.registers[23:43]),  # Change of digital gain vs temperature
            'lut_led': list(self.registers[43:63]), # Change of LED target vs temperature
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
        self.registers[3:23] = list(self.fields['lut_ov'])  # Make a deep copy
        self.registers[23:43] = list(self.fields['lut_dg'])  # Make a deep copy
        self.registers[43:63] = list(self.fields['lut_led'])  # Make a deep copy
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
            'dt': (int(self.registers[1]) & 0xFF)*0.050,  # dwell time in seconds
            'ch_0': (int(self.registers[1]) & 0xFF00) >> 8,
            'ch_1': (int(self.registers[1]) & 0xFF0000) >> 16,
            'idx': int(self.registers[2]),  # Last index written
            'count': int(self.registers[3]),  # Rollover counter
            'var_0': self.registers[4: length+2],  # Log of variable 0
            'var_1': self.registers[length+2: 2*length],    # Log of variable 1
        }

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        idx = self.fields['idx']
        if self.fields['count'] == 0:  # Logger arrays are filled incompletely
            var_0 = self.fields['var_0'][0: idx]
            var_1 = self.fields['var_1'][0: idx]
        else:
            if idx == self.logger_length-3:
                var_0 = self.fields['var_0']
                var_1 = self.fields['var_1']
            else:
                var_0 = self.fields['var_0'][idx+1: ] + self.fields['var_0'][0: idx+1]
                var_1 = self.fields['var_1'][idx+1: ] + self.fields['var_1'][0: idx+1]
        self.user = {'var_0': var_0, 'var_1': var_1}


    def user_2_fields(self):
        pass
        
        