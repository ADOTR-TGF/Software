// https://raspberry-projects.com/pi/programming-in-c/uart-serial-port/using-the-uart
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>	
#include <fcntl.h>		
#include <termios.h>

#include "bpi_globals.h"


void bpi_serial_init(){
    
    struct termios usart_options;

    //	O_NDELAY / O_NONBLOCK (same function): We use c_cc[VMIN] and c_cc[VTIME] instead
    //	O_NOCTTY - When set and path identifies a terminal device, open() shall not cause the terminal device to become the controlling terminal for the process.
    // cf man open for the flags
    uart0_fd = open("/dev/serial0", O_RDWR | O_NOCTTY);	//  Open in read/write mode
    if (uart0_fd == -1)
    {
        printf("Error - Unable to open /dev/serial0 as UART \n");
    }
    
    // See <bits/termios.h> /usr/includearm-linux-gnueabihf/bits/termios.h for the options
    // See man tcgetattr for details
    // pySerial creates: [iflag=0, oflag=0, cflag=0x18B2, lflag=0, ispeed=0x1002, ospeed=0x1002, cc]; That is the same as what the code below is doing.
    tcgetattr(uart0_fd, &usart_options);
    usart_options.c_cflag = B115200 | CS8 | CLOCAL | CREAD;	// baud rate and other settings
    usart_options.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL | IXON);
    usart_options.c_oflag &= ~OPOST;
    usart_options.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);
    usart_options.c_cflag &= ~(CSIZE | PARENB);
    usart_options.c_cflag |= CS8;
    usart_options.c_cc[VMIN] = 0;    // read() with time out
    usart_options.c_cc[VTIME] = 0;  // Polling read
    tcflush(uart0_fd, TCIOFLUSH);
    tcsetattr(uart0_fd, TCSANOW, &usart_options);
    printf("%X %X %X %X %X %X\n", usart_options.c_iflag, usart_options.c_oflag, usart_options.c_cflag, usart_options.c_lflag, usart_options.c_ispeed, usart_options.c_ospeed);
}

void bpi_serial_write(uint8_t *p8_Src, uint32_t num_bytes){
    uint32_t ret;
    ret = write(uart0_fd, p8_Src, num_bytes);
    printf("%d / %d bytes written\n", ret, num_bytes);
}

void bpi_serial_read(uint8_t *p8_Dst, uint32_t num_bytes){
    uint32_t ret, count=0;
    do{
        ret = read(uart0_fd, p8_Dst+count, num_bytes);
        count += ret;
    } while(count < num_bytes);
    
    printf("%d / %d bytes read\n", count, num_bytes);
}

void bpi_serial_reset_input_buffer(){  // Empty input buffer, if appropriate
    tcflush(uart0_fd, TCIFLUSH);
}
void bpi_serial_reset_output_buffer(){  // Empty output buffer, if appropriate
    tcflush(uart0_fd, TCOFLUSH);
}

