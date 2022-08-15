#!/bin/sh
/bin/sleep 60
cd /Detector1/bpi/wxMCA/mds
/bin/sleep 20
/usr/bin/python3.8 /Detector1/bpi/wxMCA/mds/lm_onedet.py AFD8C28B54525251202020412C2B5FF 455 pla Detector1 20 &
/bin/sleep 2
/usr/bin/python3.8 /Detector1/bpi/wxMCA/mds/lm_onedet.py ACC715C54525251202020412DA5FF 464 nai Detector1 20 &
/bin/sleep 2
/usr/bin/python3.8 /Detector1/files/GPSlogger.py &

