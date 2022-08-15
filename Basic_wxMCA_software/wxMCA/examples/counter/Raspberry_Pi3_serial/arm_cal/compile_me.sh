#! 
gcc -I "../common/" write_arm_cal.c ../common/mca1k_api.c ../common/mca1k_serial_device.c ../common/Pi3_serial.c ../common/bpi_globals.c -O3 -o ./write_arm_cal
gcc -I "../common/" read_arm_cal.c ../common/mca1k_api.c ../common/mca1k_serial_device.c ../common/Pi3_serial.c ../common/bpi_globals.c -O3 -o ./read_arm_cal
