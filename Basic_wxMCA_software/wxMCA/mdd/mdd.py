#!/usr/bin/python3
#
""" MCA Data Daemon
"""
version = [3, 0]
import time
import platform
import os
import sys
import subprocess
import json
import communication as com


def read_config(file_name):
    """ Read a JSON file, remove Python style comments and return a dictionary"""
    with open(file_name, 'r') as fin:
        json.loads(fin.read())


class Process:
    def __init__(self, ip, path, timeout):
        self.client = com.zmq_device(ip, "client")
        self.pid = -1
        self.should_be_active = 1
        self.path = path
        self.timeout = timeout


class MDD:
    def __init__(self, cfg):
        self.op_sys = platform.system().lower()
        if cfg['suspend']:
            return

        if cfg['mds_present']:
            if "linux" in self.op_sys:
                path = cfg['mds_linux_path']
            else:
                path = cfg['mds_win_path']
            self.mds = Process(cfg['mds_ip'], path, cfg['timeout'])

        # mdd's own command interface
        self.mdd_server = com.zmq_device(cfg['mdd_ip'], com_type="server")

    def listen_and_sleep(self, period):
        """ Cut the sleep period into 1-second chunks and check for incoming messages"""
        then = time.time()
        msg = ""
        while time.time()-then < period:
            n = self.mdd_server.listen()
            if n >= 1:
                msg = self.mdd_server.receive()
                self.mdd_server.answer(msg)
                return json.loads(msg)
            time.sleep(1)
        return {"name": ""}

    def process_msg(self, cmd):
        if cmd["name"] == "exit":
            sys.exit()
        elif cmd["name"] == "exit_all":
            self.mds.should_be_active = False

        elif cmd["name"] == "stop_mds":
            self.mds.should_be_active = False
            # print "stopped MDS"
        elif cmd["name"] == "start_mds":
            # print "started MDS"
            self.mds.should_be_active = True


def run_mdd():
    with open("./mdd_config.json") as fin:
        cfg = json.loads(fin.read())
    mdd = MDD(cfg)
    if cfg['suspend']:
        while 1:
            time.sleep(1)

    while True:
        msg = mdd.listen_and_sleep(cfg['repeat_period'])
        mdd.process_msg(msg)

        if cfg['mds_present']:
            # print "Manage MDS\n"
            manage_process(mdd.mds)

def send_and_receive(client, cmd):
    return client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

def poll_and_receive(client, cmd, timeout):
    return client.poll(json.dumps(cmd).encode('utf-8'), timeout).decode('utf-8')


def manage_process(process):
    # {'version': '3.0', 'os': platform.system().lower(), 'pid': os.getpid()}
    pid_cmd = {"type": "server_cmd", "name": "get_pid"}
    stop_cmd = {"type": "server_cmd", "name": "exit"}

    if process.should_be_active:
        process.client.renew()  # renew the connection, in case the process was freshly spawned
        msg = poll_and_receive(process.client, pid_cmd, process.timeout)  # get process id
        # print "Message=",msg
        if msg != "":
            ret = json.loads(msg)
            process.pid = ret["pid"]
        if msg == "":
            if process.pid != -1:
                print("Process", process.pid, "did not answer")
            if process.pid > 0:  # process is thought to be alive, but unresponsive
                kill_process(process.pid)  # kill the process
            process.pid = launch_process(process.path)  # and relaunch
            time.sleep(1)
            process.client.renew()
            print("New process id", process.pid)
            # print "restarted process"
    if not process.should_be_active:  # check if it is alive
        process.client.renew()
        msg = poll_and_receive(client, cmd, process.timeout)
        # print "length of msg",len(msg)
        # print "Message=","|{}|".format(msg)
        if msg != "":
            process.client.poll(stop_cmd, process.timeout)  # gentle way
            time.sleep(2)
            kill_process(process.pid)
            process.pid = -1


def launch_process(path):
    op_sys = platform.system().lower()
    if "linux" in op_sys:
        pid = linux_launch(path)
    else:
        pid = win_launch(path)
    return pid


def kill_process(pid):
    op_sys = platform.system().lower()
    if "linux" in op_sys:
        linux_kill_pid(pid)
    else:
        win_kill_pid(pid)
    return 0


def win_launch(path):
    sub = subprocess.Popen([path])
    return sub.pid
    # os.system(cmd) does not return until the command finishes


def linux_launch(path):
    items = path.split('/')
    c_path = '/'.join(items[:-1])
    # cmd = "#!/bin/sh\ncd "+c_path+"\n./"+items[-1]
    # with open("cmd.sh",'w') as fout:
        # fout.write(cmd)
    # sub = subprocess.Popen(["./cmd.sh"])
    my_path = os.getcwd()
    os.chdir(c_path)
    print("CWD=", os.getcwd())
    if 0:
        cmd = "/home/owner/bpi/wxMCA/run_mds.sh"
        with open("cmd.sh",'w') as fout:
            fout.write(cmd)
        sub = subprocess.Popen(["./cmd.sh"])

    sub = subprocess.Popen(["/home/owner/bpi/wxMCA/run_mds.sh"])  # process survives death of MDD
    #sub = subprocess.Popen(["/usr/bin/python3 "+items[-1]])
    os.chdir(my_path)
    return sub.pid


def win_kill_pid(pid):
    """Kill a process with a given pid. It will not crash if the process does not exist"""
    if pid < 0:
        return 0
    cmd = "Taskkill /PID {} /F".format(pid)
    os.system(cmd)  # Note: Popen will not work for this (returns error code 2)
    return pid


def linux_kill_pid(pid):
    """Kill a process with a given pid. It will not crash if the process does not exist"""
    if pid < 0:
        return
    cmd = "kill -9 {}".format(pid)
    # os.system(cmd) # Note: Popen will not work for this (returns error code 2)
    try:
        subprocess.Popen([cmd])
    except:
        print(cmd)
    return pid

run_mdd()
