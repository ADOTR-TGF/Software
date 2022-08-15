A serial interface to MCA-1K devices (PMT-1000 and SiPM-1000) as well as the SiPM-Counter.

Summary:

The purpose of this C-software is to provide access to the MCA-1K MCA's and counters via their default serial interface at 115200 Baud.

The C-software is designed to work on small 32-bit processors where RAM is limited. Hence data arrays share a common memory.
A file system is only used in the "DEBUG" blocks, which can be removed when working on processors without a file system.
Mostly, the DEBUG blocks serve to write to file the data that were read from a device.

Internal to the MCA-1K devices the serial interface is implemented via polling, rather than interrupts.  This preserves data integrity ensures that the host will not be reading data buffers that are just being changed by the MCA-1K. 


Structure:

All common files, ie the serial driver and the API are in the "common" folder.

Application-specific files are in the individual example folders.


Serial Interface - Hardware:

Pi3_serial.c implements the I/O driver for a serial port on a RaspBerry Pi3 and Pi4.  In this example, the port is "/dev/serial0" which links to "/dev/ttyS0".  Depending on ownership and permissions for this port, an application may have to run as root (sudo ) to be able to open this port and transmit data.

The 5 functions below represent the software interface to the serial port driver.  If they are implemented as specified, the API-layer of the software will function without the need for modifications.

void bpi_serial_init();
void bpi_serial_write(uint8_t *p8_Src, uint32_t num_bytes);
void bpi_serial_read(uint8_t *p8_Dst, uint32_t num_bytes);
void bpi_serial_reset_input_buffer(); 
void bpi_serial_reset_output_buffer();


Serial Interface - Protocol:

mac1k_serial_device.c contains a bulk write and a bulk read function that implement the low-level communications protocol.  The protocol requires sending a ping byte first and waiting for the MCA to respond before transmitting the bulk data.

The MCA polls the serial port about every 50ms.  If the polling routine notices a ping byte, it will respond with a return byte and then perform the bulk data transfer as required.


API layer:

mca1k_api.c is used to prepare the controlling mca_command structure and direct the bulk data transfers to their intended destinations. 


Application code

An application will use bpi_serial_init(); to prepare the serial port.  After that it will only use the functions shown in mca1k_api.c .

The contents of all MCA data arrays are described in the software documentation for each product.  The mca1k_api.h header file contains enums describing the data array contents.


Examples

We provide examples for common read and write operations as well as common tasks, such as re-starting the MCA.
Each example contains one C-file, which is compiled using the compile_me.sh script.  The resulting executable has the same name as the source code file, and data are stored in the "data" sud directory.

The compiler is gcc as it ships with a Raspberry Pi.

For the MCA-1K examples we assume that the host processor can provide aropund 20kB of RAM to store the full histogram memory.

Adding memory for the real-time logger would require another 8kB of RAM.

