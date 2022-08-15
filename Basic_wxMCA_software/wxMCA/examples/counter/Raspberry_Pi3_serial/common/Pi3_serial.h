#ifndef PI3_SERIAL_H
#define PI3_SERIAL_H

#include <stdint.h>
extern int uart0_fd;

/*
    User-supplied, functions for serial communication.
    These will naturally depend on the hardware of the host processor.
*/
void bpi_serial_init();
void bpi_serial_write(uint8_t *p8_Src, uint32_t num_bytes);
void bpi_serial_read(uint8_t *p8_Dst, uint32_t num_bytes);
void bpi_serial_reset_input_buffer();   // Empty input buffer, if appropriate
void bpi_serial_reset_output_buffer();  // Empty output buffer, if appropriate


#endif