#!/usr/bin/python
#
import time
import os
import platform
import sys
import subprocess
import json
import communication as com
import mca_api as api
import mca_device as bpi_dev

MDS_DO_LOG = False


def run_mds():
    # Load settings
    with open("./mds_config.json") as fin:
        cfg_json = fin.read()
    cfg = json.loads(cfg_json)
    mds_server = com.zmq_device(cfg['server_ip'], "server")

    if cfg["simulate"] == "None":
        print("\n>>>>>" + cfg["sim_off"] + "<<<<<\n")
    else:
        print("\n>>>>>" + cfg["sim_on"] + "<<<<<\n")

    all_mca = bpi_dev.bpi_usb().find_all()  # Dictionary of attached devices, with SN as key.
    num_mca = len(all_mca)
    sn_list = [sn for sn in all_mca]
    print('Attached MCA:', sn_list)

    if cfg['verbose'] > 0:
        print("Listening on: ", cfg['server_ip'])
        # print("pmt_mca Data Server, version = ", version_info["data_dict"])

    then = time.time()  # to reset the clock
    while 1:
        if cfg["simulate"] == "None":
        # Blocking call for a message; use decode to convert bytes into a string
            msg = mds_server.receive().decode('utf-8')
        else:
            while True:
                num_msg = mds_server.listen()  # Check for client messages
                if num_msg > 0:
                    msg = mds_server.receive().decode('utf-8')
                    break
                else:
                    time.sleep(0.050)
                    api.process_cmd({"type": "mca_cmd", "name": "arm_ping"}, all_mca)

        # reboot as needed
        if cfg['plug_and_play']:  # check if the number of eMorphos has changed
            pass

        user_cmd = {"type": "", "name": ""}
        ret_msg = '{"MDS": "Nothing to report"}'
        try:
            user_cmd.update(json.loads(msg))
        except:
            mds_server.answer(ret_msg.encode('utf-8'))
            continue

        if user_cmd["type"] == 'mca_cmd':  # mca command
            if num_mca > 0:  # execute command and create return data if an MCA is present
                ret_dict = api.process_cmd(user_cmd, all_mca)
                ret_msg = json.dumps(ret_dict)
            else:
                ret_msg = '{"MDS": "No MCA attached"}'
        elif user_cmd['type'] == 'server_cmd':  # MDS version and status commands
            ret_dict = server_response(user_cmd, all_mca)
            ret_msg = json.dumps(ret_dict)
        else:
            ret_msg = '{"MDS": "Nothing to report"}'

        mds_server.answer(ret_msg.encode('utf-8'))  # Send reply back to client (use encode to convert string to bytes)

        if user_cmd['type'] == 'server_cmd' and user_cmd['name'] == 'exit':
            sys.exit  # Exit only after we replied to client

        if MDS_DO_LOG:  # log the response to all incoming commands
            with open(cfg['log_path']+"mds_log.txt", "a") as fout:
                fout.write("{}|{}\n".format(time.time()-then, msg))
                fout.write("{}|{}\n".format(time.time()-then, ret_msg))


def server_response(user_cmd, all_mca):
    if user_cmd['name'] == 'get_pid' or user_cmd['name'] == 'get_version':
        return {'version': '3.0', 'os': platform.system().lower(), 'pid': os.getpid()}
    if user_cmd['name'] == 'ping':
        return {'ping': user_cmd['data']}
    if user_cmd['name'] == 'hello':
        sn_list = [key for key in all_mca]
        return {'sn_list': sn_list}
    if user_cmd['name'] == 'identify':
        out_list = list()
        for sn in all_mca:
            out_list += [{sn: all_mca[sn].mca_id_str}]
        return {'mca_id': out_list}
    if user_cmd['name'] == 'details':
        out_list = list()
        for sn in all_mca:
            out_list += [{sn: {
                "mca_id": all_mca[sn].mca_id,
                "mca_id_str": all_mca[sn].mca_id_str,
                "short_sn": all_mca[sn].short_sn,
                "adc_sr": all_mca[sn].adc_sr
                }}]
        return {'mca_details': out_list}

    if user_cmd['name'] == 'exit':
        return {'action': 'exit'}


    return {'err': 'Unknown server command'}


run_mds()
