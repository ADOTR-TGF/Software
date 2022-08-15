// https://raspberry-projects.com/pi/programming-in-c/uart-serial-port/using-the-uart
#include <stdint.h>
#include <unistd.h>	
#include <fcntl.h>		
#include <termios.h>
#include <stdlib.h>
#include <sys/mman.h>
#include "bcm2835.h"
#include "Pi3_serial.h"

#include "bpi_globals.h"

#define symlnk_UART0 "/dev/serial0"
#define PI4_UART0 "/dev/ttyAMA0"

#define PI3_VERBOSE 0
#define RS_485 1
#define PIN_P4 4

#if PI3_VERBOSE
#include <stdio.h>  // For printf()
#endif

/*
 Note: On the Raspberry Pi 3,4 you need to have root privilege to open the UART.
 Hence, Run your examples like this: sudo arm_status_read
*/

void bpi_serial_init(){
    
    struct termios usart_options;
    uint32_t *timer_map;
    int32_t mem_fd;
    const uint32_t io_mask = 0x3;
    const uint32_t map_shared = 0x1;
    const uint32_t base_add = 0x3F000000; // Pi2 -> 0x20000000, Pi3B+ -> 0x3F000000, Pi4 -> 0xFE000000
    const uint32_t timer_base = 0x00003000;
    const uint32_t int_base = 0x0000B000;

    //	O_NDELAY / O_NONBLOCK (same function): We use c_cc[VMIN] and c_cc[VTIME] instead
    //	O_NOCTTY - When set and path identifies a terminal device, open() shall not cause the terminal device to become the controlling terminal for the process.
    // cf man open for the flags
    uart0_fd = open(symlnk_UART0, O_RDWR | O_NOCTTY);	//  Open in read/write mode
#if PI3_VERBOSE
    if (uart0_fd == -1){ printf("Error - Unable to open %s as UART \n", symlnk_UART0); }
#endif
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
    
#if PI3_VERBOSE
    printf("%X %X %X %X %X %X\n", usart_options.c_iflag, usart_options.c_oflag, usart_options.c_cflag, usart_options.c_lflag, usart_options.c_ispeed, usart_options.c_ospeed);
#endif
    

    // Timer initialization
    mem_fd = open("/dev/mem", O_RDWR|O_SYNC);
    timer_map = mmap(NULL,4096,io_mask,map_shared,mem_fd,base_add+timer_base);
    timer = (volatile uint32_t *)timer_map+1;
    // timer->: bytes 0-3: status?, bytes 4-7 lo word, bytes 8-11 hi word 
    close(mem_fd);

    if(RS_485){
        int ret;
        ret = bcm2835_init();
        #if PI3_VERBOSE
        printf("bcm2835_init returned %d\n", ret);
        #endif
        
        bcm2835_gpio_clr(PIN_P4);      // Turn the RS485 driver off
        bcm2835_gpio_fsel(PIN_P4, 1);  // Make P4 an output
        bcm2835_gpio_clr(PIN_P4);      // Turn the RS485 driver off
        
        /*
        bcm2835_gpio_set(PIN_P4);
        timer_wait(1);
        bcm2835_gpio_clr(PIN_P4); 
        timer_wait(1);
        bcm2835_gpio_set(PIN_P4);
        timer_wait(1);
        bcm2835_gpio_clr(PIN_P4); 
        timer_wait(1);
        bcm2835_gpio_set(PIN_P4);
        timer_wait(1);
        bcm2835_gpio_clr(PIN_P4); 
        */

        // Test interruppts(0)
        /*
        {
            uint64_t now, then, diff;
            uint32_t sdiff;
            then = ((*(timer+1))*0x100000000) + (*timer);

            interrupts(0);
            timer_wait(10000000);
            interrupts(1);
            now = ((*(timer+1))*0x100000000) + (*timer);
            diff = now - then;
            sdiff = diff;
            printf("dt: %d\n", sdiff);
        }

        printf("Timer test done.\n");
        */
    }
              
}

void bpi_serial_write(uint8_t *p8_Src, uint32_t num_bytes){
    uint32_t ret;
    uint32_t dt = (uint32_t)(num_bytes*86.805556f*1.01f);  // Timed for 115200Bd, even if clock is 1% too slow
    
    if(RS_485){ bcm2835_gpio_set(PIN_P4); }    // Turn the RS485 driver on   
    ret = write(uart0_fd, p8_Src, num_bytes);
    // timer_wait(dt);  // Sleep is timed for 115200Bd, or 100us/byte
#if PI3_VERBOSE
    printf("%d / %d bytes written\n", ret, num_bytes);
#endif
    if(RS_485){ bcm2835_gpio_clr(PIN_P4); }    // Turn the RS485 driver off 
}

void bpi_serial_read(uint8_t *p8_Dst, uint32_t num_bytes){
    uint32_t ret, count=0;
    do{
        ret = read(uart0_fd, p8_Dst+count, num_bytes);
        count += ret;
    } while(count < num_bytes);
    
#if PI3_VERBOSE
    printf("%d / %d bytes read\n", count, num_bytes);
#endif
}

void bpi_serial_reset_input_buffer(){  // Empty input buffer
    tcflush(uart0_fd, TCIFLUSH);
}
void bpi_serial_reset_output_buffer(){  // Empty output buffer
    tcflush(uart0_fd, TCOFLUSH);
}

void bpi_serial_reset_buffers(){  // Empty input and output buffer
    tcflush(uart0_fd, TCIFLUSH | TCOFLUSH);
}

/*
    Function that uses the processor internal 64-bit (48 bit?) microsecond timer
*/
void timer_wait(uint32_t dt){
    // Wait dt micro seconds
    // accuracy: -.5 us to +1.5 us 
    uint64_t now;
    uint64_t timend;
    timend = ((*(timer+1))*0x100000000) + (*timer) + dt;
    do{
        now = ((*(timer+1))*0x100000000) + (*timer);
    } while(now < timend);
}