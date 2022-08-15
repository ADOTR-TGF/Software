#ifndef SIPM_MCA_API_H
#define SIPM_MCA_API_H

struct mca_command{
    uint32_t *cmd;        // 64-byte, 16-word array
    uint32_t read_type;   // ARM read command type
    uint32_t write_type;  // ARM write command type
    uint32_t com_address; // ARM command addresses
    uint32_t mem_type;    // Memory type addressed by a command
    uint32_t num_bytes;   // Number of bytes requested for next data read or write
    uint32_t *u_data;     // Point to the local uint32_t data buffer
    float *f_data;        // Point to the local float data buffer
    uint32_t *replace_idx;    // Points to the index of data that are to be replaced when performing a read-modify-write
    uint32_t *replace_u_data;  // Points to the replacement data when performing a read-modify-write
    float *replace_f_data;  // Points to the replacement data when performing a read-modify-write
    uint32_t replace_num; // Number of items to replace in a read-modify-write
};

/*
    Functions for complete data transfers: write, read and read-modify-write
*/
void mca_write(struct mca_command *mca_cmd);
void mca_read(struct mca_command *mca_cmd);
void mca_rmw(struct mca_command *mca_cmd);


void arm_command_defaults(struct mca_command *mca_cmd);
void arm_version_read(struct mca_command *mca_cmd);
void arm_status_read(struct mca_command *mca_cmd);
void arm_ctrl_read(struct mca_command *mca_cmd);
void arm_cal_read(struct mca_command *mca_cmd);
void arm_histo_read(struct mca_command *mca_cmd);
void arm_histo2k_read(struct mca_command *mca_cmd);
void arm_bck_read(struct mca_command *mca_cmd);
void arm_diff_read(struct mca_command *mca_cmd);
void arm_ctrl_write(struct mca_command *mca_cmd);
void arm_ctrl_rmw(struct mca_command *mca_cmd, uint32_t num_items);
void arm_cal_write(struct mca_command *mca_cmd);
void arm_cal_rmw(struct mca_command *mca_cmd, uint32_t num_items);

// Command types
// ARM command types
enum{
    ARM_WRITE = 3, 
    ARM_READ = 4
};

// ARM command addresses
enum{
    ARM_VERSION = 0,  // Read ARM software and hardware version
    ARM_STATUS, // Operational status of the slow-control system (R)
    ARM_CTRL,   // Operational control of the slow-control system (R/W)
    ARM_CAL,    // Calibration and LUT in RAM
    ARM_HISTO,  // MCA data with statistics and histogram (foreground)
    ARM_BCK,    // MCA data with statistics and histogram (background)
    ARM_DIFF    // MCA data with statistics and histogram (foreground-background)
};

enum{  // Memory type addressed by a command:
	MT_RAM = 0,  // Data exchange with RAM
	MT_FLASH,    // Data exchange with FLASH memory
	MT_RESET     // Copy factory reset reset_cal into arm_cal and into flash memory.
};

enum{  // Offsets in the ARM version array when interpreting arm_version as an array of 32 uint16_t integers
	AV_DEVICE_ID = 0,   // Device type, armMorpho, sipmMorpho, etc.
	AV_SHORT_SN,   // Device serial number
	AV_ARM_SN0,    // ARM serial number, word 0
	AV_ARM_SN1,    // ARM serial number, word 1
	AV_ARM_SN2,    // ARM serial number, word 2
	AV_ARM_SN3,    // ARM serial number, word 3
	AV_HW_VERSION, // Hardware version major.minor; BCD range 0.0 to 255.255 
	AV_SW_VERSION, // Software version major.minor; BCD range 0.0 to 255.255 
	AV_SW_BUILD,   // Software build number (a new build has bug fixes, but no new features)
	AV_CUSTOM_0,   // Customization ID, minor
	AV_CUSTOM_1    // Customization ID, major
};
	
enum{  // Offsets in the ARM status array when interpreting arm_status as an array of 64 floats
	AS_OV = 0,      // Current operating voltage
	AS_OV_TARGET,   // Computed target voltage is AC_OV_REQ (directly or with correction applied)
	AS_OV_SET,      // Current operating voltage set by the DAC (so that AC_OV matches AC_OV_REQ (directly or with correction applied)
	AS_DG_TARGET,   // Computed target digital gain 
	AS_ARM_TEMP,    // Current ARM M0+ temperature
	AS_X_TEMP,      // Current temperature measured by the external temperature sensor.
	AS_AVG_TEMP,    // Current temperature average
	AS_TIME_WC,     // wall_clock
	AS_RUN_STATUS,  // Run status bitfield; bit_0-> histo_active, 1-> alarm_active, 2-> riid_active
	AS_RT,          // Run time of foreground counter
	AS_RATE,        // Foreground count rate
	AS_RATE_ERR,    // Foreground count rate, 2-sigma error
	AS_RT_BCK,      // Run time of background counter
	AS_RATE_BCK,    // Background count rate
	AS_RATE_BCK_ERR,  // Background count rate, 2-sigma error
	AS_RATE_DIFF,   // Foreground - Background count rate
	AS_RATE_DIFF_ERR,   // Foreground - Background count rate, , 2-sigma error
	AS_BCK_PROB,    // Background probability, given foreground and background counts
	AS_TS_READY,    // Alarming system is ready
	AS_TS_ALARM,    // 1 if there is an active alarm
	AS_TS_NET,      // Net counts above background during the last L time slices
	AS_TS_BCK,      // Background counts during the last L time slices
	AS_TS_PROB,     // Probability that net is caused by the accepted background rate.
	AS_TS_RST       // Logger was reset due to an extended alarm (longer than arm_ctrl[AC_TS_H])
};

enum{  // AS_RUN_STATUS bit field
	RS_COUNTER=1,  // 1-> histogramming and counting is active
	RS_ACTIVE_BANK=2 // The bank currently acquiring data
};

enum{  // Offsets in the ARM controls array when interpreting arm_ctrl as an array of 64 floats
	AC_GAIN_STAB=0, // 0-> Use OV_RQ as is; 1-> Apply temperature correction
	AC_PELTIER,     // Either fixed peltier power (0 to 100%) or maximum power; To allow a host control loop
	AC_T_CTRL,      // 0-> Use ARM temperature sensor; 1-> Use external LTC2997 sensor; 2-> Use value in the AC_TEMP_TEST field
	AC_TEMP_TARGET, // Temperature input for testing purposes, or target temperature for Peltier cooling
	AC_TEMP_PERIOD, // Update period for temperature measurements
	AC_TEMP_WEIGHT, // Weight for geometric averaging: Purpose is noise reduction or matching thermal relaxation time.
	AC_CAL_TEMP,    // Temperature (in deg C) at which the detector was calibrated
	AC_CAL_OV,      // Operating voltage when the detector was calibrated
	AC_CAL_DG,      // Digital gain when the detector was calibrated
	AC_CAL_TARGET,  // Target value for ROI or LED measured response; used with gain_stab[3:0]=2,3
	AC_CAL_ROI_LOW, // [roi_low : roi_high] => Region of interest used when gain-stabilizing on ROI
	AC_CAL_ROI_HIGH,

	AC_RUN_MODE,    // Run mode: bitfield; see enum below
	AC_RUN_ACTION,  // Run action: bitfield; bit_0-> clear_statistics of active bank
	AC_RUN_TIME_SAMPLE,  // Requested run time for a counting acquisition; 0-> forever
	AC_RUN_TIME_BCK,     // Requested run time for a background counting acquisition; 0-> forever
	AC_ALARM_THR,   // Alarm threshold;  If alarm_probability less than this, blink a light or send a pulse on digital out.
	AC_ROI_LOW,     // ROI for count rate and alarming purpose
	AC_ROI_HIGH,    // ROI for count rate and alarming purpose
	AC_TS_PER,      // Time slice period in seconds.
	AC_TS_RST,      // Reset time-slice alarm system
	AC_TS_L,        // Summation length for alarm computation
	AC_TS_H,        // History length for alarms; maximum length of alarm before resetting
	AC_TS_WAIT,     // Minimum wait time until we will accept alarms, having sufficient background accuracy
	AC_TS_B,        // Background averaging length
	AC_TS_EPS,      // Alarm threshold for time-slice system
	AC_TRIGGER_WIDTH, // Output pulse width, for alarms 
	AC_TRIGGER_THR,   // Trigger threshold in V (typ. 0.025)
	AC_INT_TIME       // Integration time, in seconds, typ. 0.50e-6
};

enum{  // Run modes of arm_ctr[AC_RUN_MODE]
	RM_HISTOGRAM_RUN = 1,  // 1-> Counting and histogramming is active
	RM_ACTIVE_BANK = 2,    // 0->foreground, 1->background
	RM_TRIGGER_ENABLE = 4, // 1-> allow trigger output
	RM_READ_CLEAR = 8,     // Enable read_and_clear feature for counting
	RM_TWO_BANK = 0x10,    // Enable automatic selection of the inactive bank for reading and clearing
	RM_HISTO_2K = 0x20,    // Use one 2Kx32 histogram
	RM_USE_ROI = 0x40,     // Use ROI in the computation of alarms
	RM_SAMPLE_ALARM = 0x80,  // Compute alarm probability for foreground vs background 
	RM_TIME_SLICE = 0x100,   // Activate time slice system and dynamic alarming
	RM_RIID_RUN = 0x200
};

enum{  // Run actions of arm_ctr[AC_RUN_ACTION]
	RA_CLEAR_STATS = 1,  // 1-> Clear statistics for active bank
	RA_CLEAR_HISTO = 2   // 1-> Clear histogram for active bank
};

enum{  // Offsets in the LUT controls array when interpreting lut_ctrl as an array of 64 floats
	AL_LEN=0,   // Number of entries in the LUT; <= 20
	AL_TMIN,    // Temperature for the first LUT data entry
	AL_DT,      // Temperature step between LUT data entries
	AL_OV = 3,  // Start of OV LUT
	AL_DG = 23, // Start of DG LUT
	AL_LED = 43, // Start of LED LUT
	AL_MODE = 63 // Lock bit
};


#endif