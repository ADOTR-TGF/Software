#include "bpi_globals.h"

uint32_t command[16];  // Command buffer to send to the command_out endpoint of the MCA
uint32_t data[64];     // General purpose data I/O buffer
uint32_t replace_idx[1];  // Index of a datum to be replaced in data[]
float replace_data[1];    // New value: data[replace_idx[0]] = replace_data[0]

int uart0_fd = -1;
