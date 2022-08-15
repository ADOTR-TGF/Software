from pathlib import Path
import sys
import os

# Get include_path = ../bpi_module absolute path
include_path = os.getcwd().rsplit("/", 1)[0] # "{}/bpi_module".format(os.getcwd().rsplit("/", 1)[0])
print(include_path)
sys.path.append(include_path)

import bridgeport_mca as bpi
import bridgeport_mca.mod1 as mod1
import bridgeport_mca.mod2

print(dir(bridgeport_mca))

def test_import():
    mod1.mod1_func1()
    bpi.mod2.mod2_func1()


test_import()
