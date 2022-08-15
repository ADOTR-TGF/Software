#include <stdint.h>
#include "Pi3_serial.h"
#include "mca1k_serial_device.h"
#include "mca1k_api.h"
#include "bpi_globals.h"

#include <stdio.h> // For debugging on a device with a file system

void main(){
    /*
        Read the arm_cal.dat file in this directory and rite it to the arm_cal 
        section of the SiPM-counter.
        Note that arm_cal is always written to non-volatile memory, even if the
        command does not ask for that.
        As a result, the arm_cal data should still be there after power cycling 
        the SiPM counter.
    */
    struct mca_command mca_cmd;
    const float cal[64] = {13, 5, 5, 33.684, 33.731, 33.807, 33.908, 34.030, 34.168, 34.321, 34.483, 34.654, 34.830, 35.012, 35.199, 35.394, 0, 0, 0, 0, 0, 0, 0, 2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2, 0};
    float *fp = (float *)data;

    for(uint32_t n=0; n<64; n++){
        fp[n] = cal[n];
    }

    bpi_serial_init();  // Prepare the serial interface communication
    
    arm_cal_write(&mca_cmd);  // Send the arm_cal data
    
    {  // Debugging block
        FILE *fout;
        float *fp = (float *)data;
        fout = fopen("./data/arm_cal_written.txt","w");
        for(uint32_t n=0; n<64; n++){
            fprintf(fout, "%f\n", fp[n]);
        }
        fprintf(fout, "\n");
        fclose(fout);
    }
}
