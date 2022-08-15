# FPGA module addresses
CONTROLS = 0  # Access eMorpho control registers
STATISTICS = 1  # Access eMorpho statistics registers
RESULTS = 2  # Access eMorpho results registers (version, telemetry, calibration)
HISTOGRAM = 3  # Access eMorpho histogram memory
TRACE = 4  # Access eMorpho trace memory
LISTMODE = 5  # Access eMorpho list mode memory
USER = 6  # Access eMorpho weights memory
WEIGHTS = 7  # Access eMorpho action registers, eg to start DAQ
NVMEM = 16  # A virtual address for the non-volatile memory
TIME_SLICE = 17  # A virtual address for the time slice memory
LM_2B = 18  # A virtual address for the two-bank list mode memory