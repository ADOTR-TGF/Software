/*
    Bridgeport Instruments, LLC, 2020-08-20
    Open the documentation in your browser: documentation/english/introduction/introduction.html
    or online at 
    www.bridgeportinstruments.com/products/software/wxMCA_doc/documentation/english/introduction/introduction.html
*/

This is a portable, self-contained version of the MCA software.  You can copy this software folder to anywhere on your hard disk.

1) The documentation begins at documentation/english/introduction/introduction.html

2) Software requirements:
  64-bit Python 3.7
  If any of the modules below are missing, cd to the Python37 folder where python.exe is located.
  Then perform the commands below as needed.
  
  a) pyzmq (python -m pip install zmq)
  b) matplotlib (python -m pip install matplotlib)
  c) wxPython (python -m pip install -U wxPython)

4) Launch run_mds.cmd to start the MCA Data Server.

5) Launch run_wxMCA.cmd to start the GUI.