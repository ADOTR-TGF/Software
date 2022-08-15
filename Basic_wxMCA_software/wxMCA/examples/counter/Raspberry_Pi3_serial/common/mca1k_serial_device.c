#include <stdint.h>
#include "Pi3_serial.h"
#include "mca1k_serial_device.h"
#include "mca1k_api.h"
#include "bpi_globals.h"


/*
  This is a simple C-driver for communicating with a BPI MCA device.
  It is intended for embedded microcontrollers with limited RAM and program space.
  
  We assume that the controller is a 32-bit device and the natural item size is 32 bit.
  
  The structure of the first 32-bit word of any command is the same for all BPI MCA devices, such as PMT-MCA, armBase/armMorpho, SiPM-MCA, and SiPM-Morpho
  
  Since the stack memory space is quite limited on a micro-controller, the generic interface assumes that all bulk data arrays are global variables.
  
  Variable sizes are shown explicitly via uint32_t, uint16_t, etc instructions.
*/

/*
    Host wants to write an array of 4-byte data to the MCA.
    pSrc: Pointer to a 4-byte aligned data source
    num_words: Number of 4-bye data to be written; data may be uint32_t or float.
    
    Data will be transmitted byte-wise with the LSB being sent first
    
    We prepare the data to be sent.  Then we send a ping to the device.
    When we receive an answer to the ping, we send the data.
*/
void bpi_write_buffer(uint32_t *pSrc, uint32_t num_bytes){
    const uint32_t chunk_size = 256;
    uint32_t ping_send = 0xFF;  // A ping byte to send
    uint32_t ping_recv = 1;  // Store the received ping byte
    uint32_t num_chunks, frac_length;

    num_chunks = num_bytes >> 8;  // num_bytes / chunk_size
    frac_length = num_bytes - chunk_size * num_chunks;
    
    for(uint32_t n=0; n<num_chunks; n++){
        bpi_serial_write((uint8_t *)&ping_send, 1);  // Send a ping
        bpi_serial_read((uint8_t *)&ping_recv, 1);   // Blocking read of 1 byte
        bpi_serial_reset_input_buffer();   // Empty input buffer, if appropriate
        bpi_serial_reset_output_buffer();  // Empty output buffer, if appropriate
        bpi_serial_write((uint8_t *)pSrc, chunk_size);  // Send a ping
    }
    if(frac_length>0){
        bpi_serial_write((uint8_t *)&ping_send, 1);  // Send a ping
        bpi_serial_read((uint8_t *)&ping_recv, 1);   // Blocking read of 1 byte
        bpi_serial_reset_input_buffer();   // Empty input buffer, if appropriate
        bpi_serial_reset_output_buffer();  // Empty output buffer, if appropriate
        bpi_serial_write((uint8_t *)pSrc, frac_length);  // Send a ping
    }
    
}

/*
    Host wants to read an array of 4-byte data from the MCA.
    pDst: Pointer to a 4-byte aligned data source
    num_words: Number of 4-bye data to be written; data may be uint32_t or float.
    
    Data will be transmitted byte-wise with the LSB being sent first
    
    We are waiting to receive a ping from the MCA.  When it arrives, we answer 
    and then we can receive the data.
*/
void bpi_read_buffer(uint32_t *pDst, uint32_t num_bytes){
    const uint32_t chunk_size = 256;
    uint32_t ping_send = 0xFF;  // A ping byte to send
    uint32_t ping_recv = 1;  // Store the received ping byte
    uint32_t num_chunks, frac_length;
    
    num_chunks = num_bytes >> 8;  // num_bytes / chunk_size
    frac_length = num_bytes - chunk_size * num_chunks;
    
    for(uint32_t n=0; n<num_chunks; n++){
        bpi_serial_read((uint8_t *)&ping_recv, 1);   // Blocking read of 1 byte
        bpi_serial_reset_input_buffer();   // Empty input buffer, if appropriate
                                       // Prepare to receive data from MCA
        bpi_serial_write((uint8_t *)&ping_send, 1);  // Answer the ping
        bpi_serial_read((uint8_t *)pDst, chunk_size);  // Receive the data
    }
    if(frac_length>0){
        bpi_serial_read((uint8_t *)&ping_recv, 1);   // Blocking read of 1 byte
        bpi_serial_reset_input_buffer();   // Empty input buffer, if appropriate
        bpi_serial_write((uint8_t *)&ping_send, 1);  // Answer the ping
                                                 // Prepare to receive data from MCA
        bpi_serial_read((uint8_t *)pDst, frac_length);  // Receive the data
    }
}



// https://en.cppreference.com/w/c/language
// http://www.cplusplus.com/reference/clibrary/
