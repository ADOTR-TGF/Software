#ifndef BPI_DEVICE_H
#define BPI_DEVICE_H

#include <stdint.h>


/*
  Functions to write a command or data, and a function to read data.
  These two functions also implement the flow control using 1-byte pings
  to ascertain that either side is ready.
*/

void bpi_write_buffer(uint32_t *pSrc, uint32_t num_bytes);
void bpi_read_buffer(uint32_t *pDst, uint32_t num_bytes);


#endif
