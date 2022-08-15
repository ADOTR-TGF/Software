#ifndef BPI_GLOBALS_H
#define BPI_GLOBALS_H

#include <stdint.h>

extern uint32_t command[16];  // Command buffer to send to the command_out endpoint of the MCA
extern uint32_t data[64];     // General purpose data I/O buffer
extern uint32_t replace_idx[1];  // Index of a datum to be replaced in data[]
extern float replace_data[1];    // New value: data[replace_idx[0]] = replace_data[0]

extern int uart0_fd;

#endif