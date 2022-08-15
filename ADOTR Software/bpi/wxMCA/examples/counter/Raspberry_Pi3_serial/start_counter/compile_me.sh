#! 
gcc -I "../common/" start_counter.c ../common/mca1k_api.c ../common/mca1k_serial_device.c ../common/Pi3_serial.c ../common/bpi_globals.c -O3 -o ./start_counter
