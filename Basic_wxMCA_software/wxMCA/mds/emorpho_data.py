# version 1.0
# last edited: 2020-02-26
import math

# FPGA module addresses
MA_CONTROLS = 0  # Access eMorpho control registers
MA_STATISTICS = 1  # Access eMorpho statistics registers
MA_RESULTS = 2  # Access eMorpho results registers (version, telemetry, calibration)
MA_HISTOGRAM = 3  # Access eMorpho histogram memory
MA_TRACE = 4  # Access eMorpho trace memory
MA_LISTMODE = 5  # Access eMorpho list mode memory
MA_USER = 6  # Access eMorpho weights memory
MA_WEIGHTS = 7  # Access eMorpho action registers, eg to start DAQ
MA_7 = 7  # Generic module-7 address
MA_TIME_SLICE = MA_7  # A virtual address for the time slice memory
MA_LM_2B = MA_LISTMODE  # A virtual address for the two-bank list mode memory

class arm_ping:
    def __init__(self):
        self.registers = [0] * 16
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.cmd_addr = 0x80
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
    def __init__(self):
        self.registers = [0]*16
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6
        
        self.cmd_addr = MA_CONTROLS
        self.offset = 0
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

        val = int(self.registers[7])
        self.fields['dac_data'] = ((val & 0xFFF) << 4) + ((val >> 12) & 0xF)

        self.fields['run_time_0'] = self.registers[8]
        self.fields['run_time_1'] = self.registers[9]

        self.fields['short_it'] = int(self.registers[10])
        self.fields['put'] = int(self.registers[11])

        # CR12
        val = int(self.registers[12])
        self.fields['ecomp'] = val & 0xF
        self.fields['pcomp'] = (val >> 4) & 0xF
        self.fields['gain_select'] = (val >> 8) & 0xF
        self.fields['lm_mode'] = (val >> 12) & 0x1
        self.fields['cr12_upper'] = (val >> 13) & 0x7

        # CR13
        val = int(self.registers[13])
        self.fields['sel_led'] = val & 1
        self.fields['gain_stab'] = (val >> 1) & 0x1
        self.fields['suspend'] = (val >> 2) & 0x1
        self.fields['segment'] = (val >> 3) & 0x1
        self.fields['segment_enable'] = (val >> 4) & 0x1
        self.fields['daq_mode'] = (val >> 5) & 0x1
        self.fields['nai_mode'] = (val >> 6) & 0x1
        self.fields['temperature_disable'] = (val >> 7) & 0x1
        self.fields['sel_lut'] = (val >> 8) & 0x1
        self.fields['cr13_upper'] = (val >> 9) & 0x7F

        # CR14
        val = int(self.registers[14])
        self.fields['opto_repeat_time'] = val & 0x1F
        self.fields['opto_pulse_width'] = (val >> 5) & 0xF
        self.fields['opto_pulse_sep'] = (val >> 9) & 0xF
        self.fields['cr14_b13'] = (val >> 13) & 0x1
        self.fields['opto_trigger'] = (val >> 14) & 0x1
        self.fields['opto_enable'] = (val >> 15) & 0x1

        # CR15
        val = int(self.registers[15])
        self.fields['clear_histogram'] = val & 1
        self.fields['clear_statistics'] = (val >> 1) & 0x1
        self.fields['clear_trace'] = (val >> 2) & 0x1
        self.fields['clear_list_mode'] = (val >> 3) & 0x1
        self.fields['program_hv'] = (val >> 4) & 0x1
        self.fields['ut_run'] = (val >> 5) & 0x1
        self.fields['write_nv'] = (val >> 6) & 0x1
        self.fields['read_nv'] = (val >> 7) & 0x1

        self.fields['cr15_b8'] = (val >> 8) & 0x1
        self.fields['ha_run'] = (val >> 9) & 0x1
        self.fields['vt_run'] = (val >> 10) & 0x1
        self.fields['trace_run'] = (val >> 11) & 0x1
        self.fields['lm_run'] = (val >> 12) & 0x1
        self.fields['rtlt'] = (val >> 13) & 0x3
        self.fields['run'] = (val >> 15) & 0x1

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

        dac_data = int(self.fields['dac_data'])
        self.registers[7] = ((dac_data & 0xFFF0) >> 4) + ((dac_data & 0xF) << 12)

        self.registers[8] = int(self.fields['run_time_0'])  # lower 16-bit word
        self.registers[9] = int(self.fields['run_time_1'])  # upper 16-bit word

        self.registers[10] = int(self.fields['short_it'])
        self.registers[11] = int(self.fields['put'])

        self.registers[12] = (int(self.fields['ecomp']) & 0xF) + ((int(self.fields['pcomp']) & 0xF) << 4) + \
                             ((int(self.fields['gain_select']) & 0xF) << 8) + \
                             ((int(self.fields['lm_mode']) & 0x1) << 12) + \
                             ((int(self.fields['cr12_upper']) & 0x7) << 13)

        self.registers[13] = (int(self.fields['sel_led']) & 1) + (int(self.fields['gain_stab']) & 1) * 0x2 + \
                             (int(self.fields['suspend']) & 1) * 0x4 + (int(self.fields['segment']) & 1) * 0x8 + \
                             (int(self.fields['segment_enable']) & 1) * 0x10 + \
                             (int(self.fields['daq_mode']) & 1) * 0x20 + (int(self.fields['nai_mode']) & 1) * 0x40 + \
                             (int(self.fields['temperature_disable']) & 1) * 0x80 + \
                             (int(self.fields['sel_lut']) & 1) * 0x100 + \
                             (int(self.fields['cr13_upper']) & 0x7F) * 0x200

        self.registers[14] = (int(self.fields['opto_repeat_time']) & 0x1F) + \
                             ((int(self.fields['opto_pulse_width']) & 0xF) << 5) + \
                             ((int(self.fields['opto_pulse_sep']) & 0xF) << 9) + \
                             ((int(self.fields['cr14_b13']) & 1) << 13) + \
                             ((int(self.fields['opto_trigger']) & 1) << 14) + \
                             ((int(self.fields['opto_enable']) & 1) << 15)

        # Specific data acquisition modes for histogram, list mode and trace
        self.registers[15] = ((int(self.fields['clear_histogram']) & 1) + \
                             (int(self.fields['clear_statistics']) & 1) * 0x2 + \
                             (int(self.fields['clear_trace']) & 1) * 0x4 + \
                             (int(self.fields['clear_list_mode']) & 1) * 0x8 + \
                             (int(self.fields['program_hv']) & 1) * 0x10 + (int(self.fields['ut_run']) & 1) * 0x20 + \
                             (int(self.fields['write_nv']) & 1) * 0x40 + (int(self.fields['read_nv']) & 1) * 0x80 + \
                             (int(self.fields['cr15_b8']) & 1) * 0x100 +\
                             (int(self.fields['ha_run']) & 1) * 0x200 + (int(self.fields['vt_run']) & 1) * 0x400 + \
                             (int(self.fields['trace_run']) & 1) * 0x800 + (int(self.fields['lm_run']) & 1) * 0x1000 + \
                             (int(self.fields['rtlt']) & 3) * 0x2000 + (int(self.fields['run']) & 1) * 0x8000)

    def fields_2_user(self):
        """
            Convert a few field values into physical quantities in SI units; times are in seconds, thresholds are in V.
            :return: None
        """
        self.user = {
            'high_voltage': float(self.fields['dac_data'])*3000.0/65536.0,
            'digital_gain': self.fields['fine_gain'] / 2**self.fields['ecomp'] * self.adc_sr/40.0e6,
            'integration_time': self.fields['integration_time']/self.adc_sr,
            'hold_off_time': self.fields['hold_off_time']/self.adc_sr,
            'short_it': self.fields['short_it']/self.adc_sr,
            'baseline_threshold': self.fields['baseline_threshold']/1000.0,
            'pulse_threshold': self.fields['pulse_threshold']/1000.0,
            'trigger_delay': self.fields['trigger_delay']/self.adc_sr,
            'roi_low': (int(self.fields['roi_bounds']) & 0xFF)*16,  # Unit is MCA bins
            'roi_high': (int(self.fields['roi_bounds']) >> 4) & 0xFF0,  # Unit is MCA bins
            'run_time': (self.fields['run_time_1']*0x10000 + self.fields['run_time_0'])*0x10000/self.adc_sr
        }

    def user_2_fields(self):
        """
            Convert user values from physical quantities in SI units into numerical fields
            :return: None
        """
        fg = self.user['digital_gain'] * 40.0e6 / self.adc_sr
        fg = max(1, fg)
        ecomp = 0            
        while fg < 16384:
            fg *= 2
            ecomp += 1
            
        self.fields['fine_gain'] = int(fg)
        self.fields['ecomp'] = ecomp
        self.fields['integration_time'] = int(self.user['integration_time'] * self.adc_sr + 0.5)
        self.fields['hold_off_time'] = int(self.user['hold_off_time'] * self.adc_sr + 0.5)
        self.fields['short_it'] = int(self.user['short_it'] * self.adc_sr + 0.5)
        self.fields['trigger_delay'] = int(self.user['trigger_delay'] * self.adc_sr + 0.5)
        self.fields['baseline_threshold'] = int(self.user['baseline_threshold'] * 1000.0 + 0.5) & 0x3FF
        self.fields['pulse_threshold'] = int(self.user['pulse_threshold'] * 1000.0 + 0.5) & 0x3FF
        self.fields['roi_bounds'] = (int(self.user['roi_low']) >> 4) + int(self.user['roi_high']) * 16
        rt = int(self.user['run_time']*self.adc_sr/0x10000)
        self.fields['run_time_0'] = rt & 0xFFFF
        self.fields['run_time_1'] = (rt & 0xFFFF0000) >> 16
        self.fields['dac_data'] = self.user['high_voltage']*65536.0/3000.0


class fpga_statistics:
    def __init__(self):
        self.registers = [0] * 16
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

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
            'sensor': (self.registers[6] & 0xFF00)//256,  # 0,1-> PMT, 2->SiPM
            'custom': self.registers[8],  # Customization number
            'build': self.registers[9],  # Build number increases with every release
            'rr_10': self.registers[10],  # Results register 10, uint16_t
            'rr_11': self.registers[11],  # Results register 10, uint16_t
            'rr_12': self.registers[12],  # Results register 10, uint16_t
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
        #gs = self.fields['status'] & 0xF00  # status[11:8]=gain_select
        gs = 2
        impedance = 100.0 + (gs & 1) * 330.0 + (gs & 2) / 2.0 * 1000.0
        impedance += (gs & 4) / 4.0 * 3300.0 + (gs & 8) / 8.0 * 10000.0
        adc_voltage_range = 1.0  # in Volt
        dc_offset = self.fields['dc_offset']/65536.0  # DC-offset in Volt
        anode_current = 0
        # Test for sign bit: Negative numbers mean zero current (just noise)
        if self.fields['anode_current'] & 0x80000000 == 0:
            anode_current = self.fields['anode_current'] * adc_voltage_range / impedance * pow(2.0, -26.0)
            
        self.user = {
            'temperature': degc,  # Temperature in degree Celsius
            'dc_offset': dc_offset,  # DC-offset in Volt
            'histo_done': self.fields['status'] & 0x1,  # Histogram done
            'lm_done': (self.fields['status'] & 0x2)//0x2,  # List mode acquisition complete
            'trace_done': (self.fields['status'] & 0x4)//0x4,  # Trace acquisition complete
            'nvmem_busy': (self.fields['status'] & 0x80)//0x80,  # Non-volatile memory is busy
            'impedance': impedance,
            'max_volt': adc_voltage_range - dc_offset,  # Maximum pulse height in V
            'max_current': (adc_voltage_range - dc_offset) / impedance,  # Maximum anode current in A
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

        self.cmd_addr = MA_LISTMODE
        self.data_type = 'H'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 2

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        """
            Unpack the list mode data buffer into energy and time lists
            In 'registers' all raw data are returned.
            In 'fields' the list length is limited to the number of events, same as in 'user'
            :return: None
        """
        mode = (self.registers[1023] & 0x8000) // 0x8000
        num_events = self.registers[1023] & 0xFFF

        self.fields = {
            'mode': mode,
            'num_events': num_events,
            'energies': self.registers[0::3]
        }
        if mode == 0:
            self.fields['times'] = [t0 + (t1 << 16) for t0, t1 in zip(self.registers[1::3], self.registers[2::3])]
            self.fields['short_sums'] = []
        else:
            self.fields['times'] = self.registers[2::3]
            self.fields['short_sums'] = self.registers[1::3]
            self.fields['short_sums'] = self.fields['short_sums'][0:num_events]
        self.fields['energies'] = self.fields['energies'][0:num_events]
        self.fields['times'] = self.fields['times'][0:num_events]

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        """
            Convert energy and time lists into seconds and mca_bins
            :return: None
        """
        self.user = {
            'mode': self.fields['mode'],
            'num_events': self.fields['num_events'],
            'energies': [e/16.0 for e in self.fields['energies']]
        }
        if self.fields['mode'] == 0:
            self.user['times'] = [t/self.adc_sr for t in self.fields['times']]
        else:
            self.user['times'] = [t*64.0/self.adc_sr for t in self.fields['times']]
            self.user['short_sums'] = [e/16.0 for e in self.fields['short_sums']]

    def user_2_fields(self):
        pass


class fpga_trace:
    def __init__(self):
        self.registers = [0]*1024
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

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
                     'fwhm': fwhm, 'dc_val': dc_val}

        return None


class fpga_user:
    def __init__(self):
        self.registers = [0] * 1024
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.cmd_addr = MA_USER
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

"""
    The classes below support non-standard features that are not present
    in the common firmware.
"""

class fpga_lut:
    """ eMorpho MCA on slimMorpho. usbBase and oemBase, build 64 and later
        A set of temperature lookup tables (64 float_32 parameters) can
        be stored in the onboard SPI flash memory.
        The object communicates via the FPGA user area; hence cmd_addr = MA_USER 
    """
    def __init__(self):
        self.registers = [0.0] * 64
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.cmd_addr = MA_USER
        self.data_type = 'f'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 2

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        self.fields = {
            "tmin": float(self.registers[0]),
            "dt": float(self.registers[1]),
            "len": float(self.registers[2]),
            "ov": [float(x) for x in self.registers[3:23]],
            "dg": [float(x) for x in self.registers[23:43]],
            "led": [float(x) for x in self.registers[43:63]],
            "mode": float(self.registers[63])
        }

    def fields_2_registers(self):
        self.registers[0] = float(self.fields["tmin"])
        self.registers[1] = float(self.fields["dt"])
        self.registers[2] = float(self.fields["len"])
        self.registers[3:23] = [float(x) for x in self.fields["ov"]]
        self.registers[23:43] = [float(x) for x in self.fields["dg"]]
        self.registers[43:63] = [float(x) for x in self.fields["led"]]
        self.registers[63] = float(self.fields["mode"])

    def fields_2_user(self):
        pass

    def user_2_fields(self):
        pass 

class fpga_weights:
    def __init__(self):
        self.registers = [0] * 1024
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

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

        
class fpga_time_slice:
    def __init__(self):
        self.registers = [0] * 1024
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.cmd_addr = MA_TIME_SLICE
        self.data_type = 'H'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 2

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        self.fields = {
            "dwell_time": 0.1048576,  # 64*65536/40e6
            "buffer_number": self.registers[0],
            "temperature": self.registers[1]/16.0,
            "gamma_events": self.registers[8],
            "gamma_triggers": self.registers[10],
            "dead_time": (self.registers[12] + self.registers[13]*65536.0)/self.adc_sr,
            "neutron_counts": self.registers[14],
            "gm_counts": self.registers[16],  # GM dosimeter counts
            "histogram": self.registers[18: 1024]
        }

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        pass

    def user_2_fields(self):
        pass
        

class fpga_lm_2b:
    def __init__(self):
        self.registers = [0] * 8192
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.cmd_addr = MA_LM_2B
        self.data_type = 'H'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 2

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        """
            Unpack the list mode data buffer into energy and time lists
            In 'registers' all raw data are returned.
            In 'fields' the list length is limited to the number of events, same as in 'user'
            :return: None
        """
        mode = (self.registers[0] & 0x2000) // 0x2000
        num_events = self.registers[0] & 0xFFF

        self.fields = {
            'mode': mode,
            'num_events': num_events,
            'energies': self.registers[2::3]
        }
        if mode == 0:
            self.fields['times'] = [t0 + (t1 << 16) for t0, t1 in zip(self.registers[3::3], self.registers[4::3])]
            self.fields['short_sums'] = []
        else:
            self.fields['times'] = self.registers[4::3]
            self.fields['short_sums'] = self.registers[3::3]
            self.fields['short_sums'] = self.fields['short_sums'][0:num_events]
        self.fields['energies'] = self.fields['energies'][0:num_events]
        self.fields['times'] = self.fields['times'][0:num_events]

    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        """
            Convert energy and time lists into seconds and mca_bins
            :return: None
        """
        self.user = {
            'mode': self.fields['mode'],
            'num_events': self.fields['num_events'],
            'energies': [e/16.0 for e in self.fields['energies']]
        }
        if self.fields['mode'] == 0:
            self.user['times'] = [t/self.adc_sr for t in self.fields['times']]
        else:
            self.user['times'] = [t*64.0/self.adc_sr for t in self.fields['times']]
            self.user['short_sums'] = [e/16.0 for e in self.fields['short_sums']]

    def user_2_fields(self):
        pass

# Class for NRL-1 firmware - requires non-standard firmware
class fpga_lm_nrl1:
    def __init__(self):
        self.registers = [0] * (6*2048)
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6
        
        self.cmd_addr = MA_LISTMODE
        self.offset = 0
        self.data_type = 'H'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 2

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        """
            Unpack the list mode data buffer into energy and time lists
            In 'registers' all raw data are returned.
            In 'fields' the list length is limited to the number of events, same as in 'user'
            :return: None
        """
        L=2048
        E0 = 6*(self.registers[0] & 0xFFF)

        self.fields = {
            'num_events': self.registers[0] & 0xFFF,
            'energies': self.registers[7:E0:6],
            'psd': self.registers[6:E0:6],
            'wc': [w0 + w1*0x10000 + w2*0x10000*0x10000 + (w3 & 0x7)*0x10000*0x10000*0x10000 \
                   for w0,w1,w2,w3 in zip(self.registers[8:E0:6], self.registers[9:E0:6],\
                       self.registers[10:E0:6], self.registers[11:E0:6])],
            'xt': [(x & 0x8)//8 for x in self.registers[11:E0:6]],
            'pu': [(p & 0x10)//0x10 for p in self.registers[11:E0:6]],
            'ov': [(p & 0x20)//0x20 for p in self.registers[11:E0:6]],
            'or': [(p & 0x40)//0x40 for p in self.registers[11:E0:6]],
            'pps': [(p & 0x80)//0x80 for p in self.registers[11:E0:6]]
        }
        
    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        """
            Convert energy and time lists into seconds and mca_bins
            :return: None
        """
        self.user = {
            'energies': [e/16.0 for e in self.fields['energies']],
            'wc': [w/40e6 for w in self.fields["wc"]]      
        }
        

    def user_2_fields(self):
        pass

# Classes for TGF firmware - requires non-standard firmware and hardware  
class fpga_tgf_ctrl:
    def __init__(self):
        self.registers = [0]*32
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6
        
        self.cmd_addr = MA_CONTROLS
        self.offset = 0
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

        val = int(self.registers[7])
        self.fields['dac_data'] = ((val & 0xFFF) << 4) + ((val >> 12) & 0xF)

        self.fields['run_time_0'] = self.registers[8]
        self.fields['run_time_1'] = self.registers[9]

        self.fields['short_it'] = int(self.registers[10])
        self.fields['put'] = int(self.registers[11])

        # CR12
        val = int(self.registers[12])
        self.fields['ecomp'] = val & 0xF
        self.fields['pcomp'] = (val >> 4) & 0xF
        self.fields['gain_select'] = (val >> 8) & 0xF
        self.fields['lm_mode'] = (val >> 12) & 0x1
        self.fields['cr12_upper'] = (val >> 13) & 0x7

        # CR13
        val = int(self.registers[13])
        self.fields['sel_led'] = val & 1
        self.fields['gain_stab'] = (val >> 1) & 0x1
        self.fields['suspend'] = (val >> 2) & 0x1
        self.fields['segment'] = (val >> 3) & 0x1
        self.fields['segment_enable'] = (val >> 4) & 0x1
        self.fields['daq_mode'] = (val >> 5) & 0x1
        self.fields['nai_mode'] = (val >> 6) & 0x1
        self.fields['temperature_disable'] = (val >> 7) & 0x1
        self.fields['cr13_upper'] = (val >> 8) & 0xFF

        # CR14
        val = int(self.registers[14])
        self.fields['opto_repeat_time'] = val & 0x1F
        self.fields['opto_pulse_width'] = (val >> 5) & 0xF
        self.fields['opto_pulse_sep'] = (val >> 9) & 0xF
        self.fields['cr14_b13'] = (val >> 13) & 0x1
        self.fields['opto_trigger'] = (val >> 14) & 0x1
        self.fields['opto_enable'] = (val >> 15) & 0x1

        # CR15
        val = int(self.registers[15])
        self.fields['clear_histogram'] = val & 1
        self.fields['clear_statistics'] = (val >> 1) & 0x1
        self.fields['clear_trace'] = (val >> 2) & 0x1
        self.fields['clear_list_mode'] = (val >> 3) & 0x1
        self.fields['program_hv'] = (val >> 4) & 0x1
        self.fields['ut_run'] = (val >> 5) & 0x1
        self.fields['write_nv'] = (val >> 6) & 0x1
        self.fields['read_nv'] = (val >> 7) & 0x1

        self.fields['cr15_b8'] = (val >> 8) & 0x1
        self.fields['ha_run'] = (val >> 9) & 0x1
        self.fields['vt_run'] = (val >> 10) & 0x1
        self.fields['trace_run'] = (val >> 11) & 0x1
        self.fields['lm_run'] = (val >> 12) & 0x1
        self.fields['rtlt'] = (val >> 13) & 0x3
        self.fields['run'] = (val >> 15) & 0x1
        
        # CR16 - CR20
        for n in range(5):
            self.fields['xtrn{}'.format(n)] = int(self.registers[n+16]) & 0xFFFF
            self.fields['xtrm{}'.format(n)] = int(self.registers[n+21]) & 0xFFFF
            self.fields['xtrc{}'.format(n)] = int(self.registers[n+26]) & 0xFFFF
         
        # CR31
        self.fields['xwait'] = int(self.registers[31]) & 0xFFFF

    def fields_2_registers(self):
        """
            Compute the values of the control registers from the fields dictionary.
            :return: None
        """
        self.registers = [0] * 32
        self.registers[0] = int(self.fields['fine_gain'])
        self.registers[1] = (int(self.fields['baseline_threshold']) & 0x03FF) + (int(self.fields['cr1_upper']) << 10)
        self.registers[2] = (int(self.fields['pulse_threshold']) & 0x03FF) + (int(self.fields['cr2_upper']) << 10)
        self.registers[3] = int(self.fields['hold_off_time'])
        self.registers[4] = int(self.fields['integration_time'])
        self.registers[5] = int(self.fields['roi_bounds'])
        self.registers[6] = (int(self.fields['trigger_delay']) & 0x03FF) + (int(self.fields['cr6_upper']) << 10)

        dac_data = int(self.fields['dac_data'])
        self.registers[7] = ((dac_data & 0xFFF0) >> 4) + ((dac_data & 0xF) << 12)

        self.registers[8] = int(self.fields['run_time_0'])  # lower 16-bit word
        self.registers[9] = int(self.fields['run_time_1'])  # upper 16-bit word

        self.registers[10] = int(self.fields['short_it'])
        self.registers[11] = int(self.fields['put'])

        self.registers[12] = (int(self.fields['ecomp']) & 0xF) + ((int(self.fields['pcomp']) & 0xF) << 4) + \
                             ((int(self.fields['gain_select']) & 0xF) << 8) + \
                             ((int(self.fields['lm_mode']) & 0x1) << 12) + \
                             ((int(self.fields['cr12_upper']) & 0x7) << 13)

        self.registers[13] = (int(self.fields['sel_led']) & 1) + (int(self.fields['gain_stab']) & 1) * 0x2 + \
                             (int(self.fields['suspend']) & 1) * 0x4 + (int(self.fields['segment']) & 1) * 0x8 + \
                             (int(self.fields['segment_enable']) & 1) * 0x10 + \
                             (int(self.fields['daq_mode']) & 1) * 0x20 + (int(self.fields['nai_mode']) & 1) * 0x40 + \
                             (int(self.fields['temperature_disable']) & 1) * 0x80 + \
                             (int(self.fields['cr13_upper']) & 0xFF) * 0x100

        self.registers[14] = (int(self.fields['opto_repeat_time']) & 0x1F) + \
                             ((int(self.fields['opto_pulse_width']) & 0xF) << 5) + \
                             ((int(self.fields['opto_pulse_sep']) & 0xF) << 9) + \
                             ((int(self.fields['cr14_b13']) & 1) << 13) + \
                             ((int(self.fields['opto_trigger']) & 1) << 14) + \
                             ((int(self.fields['opto_enable']) & 1) << 15)

        # Specific data acquisition modes for histogram, list mode and trace
        self.registers[15] = ((int(self.fields['clear_histogram']) & 1) + \
                             (int(self.fields['clear_statistics']) & 1) * 0x2 + \
                             (int(self.fields['clear_trace']) & 1) * 0x4 + \
                             (int(self.fields['clear_list_mode']) & 1) * 0x8 + \
                             (int(self.fields['program_hv']) & 1) * 0x10 + (int(self.fields['ut_run']) & 1) * 0x20 + \
                             (int(self.fields['write_nv']) & 1) * 0x40 + (int(self.fields['read_nv']) & 1) * 0x80 + \
                             (int(self.fields['cr15_b8']) & 1) * 0x100 +\
                             (int(self.fields['ha_run']) & 1) * 0x200 + (int(self.fields['vt_run']) & 1) * 0x400 + \
                             (int(self.fields['trace_run']) & 1) * 0x800 + (int(self.fields['lm_run']) & 1) * 0x1000 + \
                             (int(self.fields['rtlt']) & 3) * 0x2000 + (int(self.fields['run']) & 1) * 0x8000)\
                             | 0x10  # Always set the program_hv bit.
        
        for n in range(5):
            self.registers[n+16] = int(self.fields['xtrn{}'.format(n)]) & 0xFFFF
            self.registers[n+21] = int(self.fields['xtrm{}'.format(n)]) & 0xFFFF
            self.registers[n+26] = int(self.fields['xtrc{}'.format(n)]) & 0xFFFF
        
        self.registers[31] = self.fields['xwait'] & 0xFFFF


    def fields_2_user(self):
        """
            Convert a few field values into physical quantities in SI units; times are in seconds, thresholds are in V.
            :return: None
        """
        self.user = {
            'high_voltage': float(self.fields['dac_data'])*3000.0/65536.0,
            'digital_gain': self.fields['fine_gain'] / 2**self.fields['ecomp'] * self.adc_sr/40.0e6,
            'integration_time': self.fields['integration_time']/self.adc_sr,
            'hold_off_time': self.fields['hold_off_time']/self.adc_sr,
            'short_it': self.fields['short_it']/self.adc_sr,
            'baseline_threshold': self.fields['baseline_threshold']/1000.0,
            'pulse_threshold': self.fields['pulse_threshold']/1000.0,
            'trigger_delay': self.fields['trigger_delay']/self.adc_sr,
            'roi_low': (int(self.fields['roi_bounds']) & 0xFF)*16,  # Unit is MCA bins
            'roi_high': (int(self.fields['roi_bounds']) >> 4) & 0xFF0,  # Unit is MCA bins
            'run_time': (self.fields['run_time_1']*0x10000 + self.fields['run_time_0'])*0x10000/self.adc_sr
        }

    def user_2_fields(self):
        """
            Convert user values from physical quantities in SI units into numerical fields
            :return: None
        """
        fg = self.user['digital_gain'] * 40.0e6 / self.adc_sr 
        fg = max(1, fg)
        ecomp = 0            
        while fg < 16384:
            fg *= 2
            ecomp += 1
            
        self.fields['fine_gain'] = int(fg)
        self.fields['ecomp'] = ecomp
        self.fields['integration_time'] = int(self.user['integration_time'] * self.adc_sr + 0.5)
        self.fields['hold_off_time'] = int(self.user['hold_off_time'] * self.adc_sr + 0.5)
        self.fields['short_it'] = int(self.user['short_it'] * self.adc_sr + 0.5)
        self.fields['trigger_delay'] = int(self.user['trigger_delay'] * self.adc_sr + 0.5)
        self.fields['baseline_threshold'] = int(self.user['baseline_threshold'] * 1000.0 + 0.5) & 0x3FF
        self.fields['pulse_threshold'] = int(self.user['pulse_threshold'] * 1000.0 + 0.5) & 0x3FF
        self.fields['roi_bounds'] = (int(self.user['roi_low']) >> 4) + int(self.user['roi_high']) * 16
        rt = int(self.user['run_time']*self.adc_sr/0x10000)
        self.fields['run_time_0'] = rt & 0xFFFF
        self.fields['run_time_1'] = (rt & 0xFFFF0000) >> 16
        self.fields['dac_data'] = self.user['high_voltage']*65536.0/3000.0


class fpga_tgf_results:
    def __init__(self):
        self.registers = [0] * 32
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

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
            'sensor': (self.registers[6] & 0xFF00)//256,  # 0,1-> PMT, 2->SiPM
            'custom': self.registers[8],  # Customization number
            'build': self.registers[9],  # Build number increases with every release

            'tgf_status': self.registers[10],  # Extended trace acquisition status
            'xtwc0': self.registers[11] + self.registers[12]*0x10000,  # XTrace 0, freeze time
            'xtwc1': self.registers[13] + self.registers[14]*0x10000,  # XTrace 1, freeze time
            'xtwc2': self.registers[15] + self.registers[16]*0x10000,  # XTrace 2, freeze time
            'xtwc3': self.registers[17] + self.registers[18]*0x10000,  # XTrace 3, freeze time
            'xtwc4': self.registers[19] + self.registers[20]*0x10000   # XTrace 4, freeze time
            
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
        # gs = self.fields['status'] & 0xF00  # status[11:8]=gain_select
        gs = 2
        impedance = 100.0 + (gs & 1) * 330.0 + (gs & 2) / 2.0 * 1000.0
        impedance += (gs & 4) / 4.0 * 3300.0 + (gs & 8) / 8.0 * 10000.0
        adc_voltage_range = 1.0  # in Volt
        dc_offset = self.fields['dc_offset']/65536.0  # DC-offset in Volt
        anode_current = 0
        # Test for sign bit: Negative numbers mean zero current (just noise)
        if self.fields['anode_current'] & 0x80000000 == 0:
            anode_current = self.fields['anode_current'] * adc_voltage_range / impedance * pow(2.0, -26.0)
            
        self.user = {
            'temperature': degc,  # Temperature in degree Celsius
            'dc_offset': dc_offset,  # DC-offset in Volt
            'histo_done': self.fields['status'] & 0x1,  # Histogram done
            'full_0': (self.fields['status'] & 0x2)//0x2,  # List mode buffer 0 acquisition complete
            'trace_done': (self.fields['status'] & 0x4)//0x4,  # Trace acquisition complete
            'full_1': (self.fields['status'] & 0x8)//0x8,  # List mode buffer 1 acquisition complete
            'impedance': impedance,
            'max_volt': adc_voltage_range - dc_offset,  # Maximum pulse height in V
            'max_current': (adc_voltage_range - dc_offset) / impedance,  # Maximum anode current in A
            'anode_current': anode_current,
            'adc_sr': self.fields['adc_sr'] * 1.0e6,
            'xt0_done':  self.fields['tgf_status'] & 0x1,
            'xt1_done': (self.fields['tgf_status'] >> 1) & 0x1,
            'xt2_done': (self.fields['tgf_status'] >> 2) & 0x1,
            'xt3_done': (self.fields['tgf_status'] >> 3) & 0x1,
            'xt4_done': (self.fields['tgf_status'] >> 4) & 0x1
        }

    def user_2_fields(self):
        pass

class fpga_tgf_lm:
    def __init__(self):
        self.registers = [0] * (6*2048)
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.cmd_addr = MA_LISTMODE
        self.offset = 0
        self.data_type = 'H'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items * 2
        

    def add_to_cmd_out_list(self, mca):
        pass

    def registers_2_fields(self):
        """
            Unpack the list mode data buffer into energy and time lists
            In 'registers' all raw data are returned.
            In 'fields' the list length is limited to the number of events, same as in 'user'
            :return: None
        """
        L=2048
        E0 = 6*(self.registers[0] & 0xFFF)

        self.fields = {
            'num_events': self.registers[0] & 0xFFF,
            'energies': self.registers[7:E0:6],
            'psd': self.registers[6:E0:6],
            'wc': [w0 + w1*0x10000 + (w2 & 0xF)*0x10000*0x10000 \
                   for w0,w1,w2 in zip(self.registers[8:E0:6], self.registers[9:E0:6],\
                                       self.registers[10:E0:6])],
            'peak': [(x & 0xFFF0)//0x10  for x in self.registers[10:E0:6]],
            'tbnt': [(x & 0xFF)          for x in self.registers[11:E0:6]],
            'nr':  [(x & 0x100)//0x100   for x in self.registers[11:E0:6]],
            'hs':  [(x & 0x200)//0x200   for x in self.registers[11:E0:6]],
            'he':  [(x & 0x400)//0x400   for x in self.registers[11:E0:6]],
            'xt':  [(x & 0x800)//0x800   for x in self.registers[11:E0:6]],
            'pu':  [(p & 0x1000)//0x1000 for p in self.registers[11:E0:6]],
            'ov':  [(p & 0x2000)//0x2000 for p in self.registers[11:E0:6]],
            'or':  [(p & 0x4000)//0x4000 for p in self.registers[11:E0:6]],
            'pps': [(p & 0x8000)//0x8000 for p in self.registers[11:E0:6]]
        }
        
    def fields_2_registers(self):
        pass

    def fields_2_user(self):
        """
            Convert energy and time lists into seconds and mca_bins
            :return: None
        """
        self.user = {
            'energies': [e/16.0 for e in self.fields['energies']],
            'wc': [w/40e6 for w in self.fields["wc"]]      
        }
        

    def user_2_fields(self):
        pass
        
class fpga_tgf_xt28k(): # 8-bit trace with 28*1024 entries
    def __init__(self):
        self.registers = [0] * (14*2048)
        self.fields = {}
        self.user = {}
        self.adc_sr = 40.0e6

        self.cmd_addr = 8
        self.data_type = 'B'
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items

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
        
class fpga_tgf_xt2k_1(fpga_tgf_xt28k): # 8-bit trace with 1024 entries
    def __init__(self):
        super().__init__()
        self.registers = [0] * 2048
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items
        self.cmd_addr = 9
        
class fpga_tgf_xt2k_2(fpga_tgf_xt28k): # 8-bit trace with 1024 entries
    def __init__(self):
        super().__init__()
        self.registers = [0] * 2048
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items
        self.cmd_addr = 10

class fpga_tgf_xt2k_3(fpga_tgf_xt28k): # 8-bit trace with 1024 entries
    def __init__(self):
        super().__init__()
        self.registers = [0] * 2048
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items
        self.cmd_addr = 11
        
class fpga_tgf_xt2k_4(fpga_tgf_xt28k): # 8-bit trace with 1024 entries
    def __init__(self):
        super().__init__()
        self.registers = [0] * 2048
        self.num_items = len(self.registers)
        self.num_bytes = self.num_items
        self.cmd_addr = 12
      
        