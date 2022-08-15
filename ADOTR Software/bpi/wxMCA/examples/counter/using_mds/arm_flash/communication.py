#!/usr/bin/python
#
# version 1.0
from __future__ import division
import zmq

class zmq_device():
    def __init__(self,ip,mode="client"):
        self.mode = mode
        self.ip = ip
        self.context = zmq.Context.instance()
        if mode == "server":
            self.responder = self.context.socket(zmq.REP)  #  A server socket, responding to a client
            self.responder.bind(ip)
        else:
            self.socket = self.context.socket(zmq.REQ)  #  A client socket
            self.socket.connect(ip)

    def echo(self): # check for messages and echo if there is one
        msg = ""
        num_msg = self.responder.poll(1)
        if num_msg >= 1:
            msg = self.responder.recv(); # receive
            self.responder.send(msg) # and echo back
        return num_msg, msg

    def poll(self, msg, wait=5):    # send a message and wait up to 'wait' seconds for an answer
        self.socket.send(msg)
        num_msg = self.socket.poll(wait*1000)
        if num_msg >= 1:
            return self.socket.recv()
        else:
            return b""

    def renew(self):
        if self.mode == "client":
            self.socket.close()
            self.socket = self.context.socket(zmq.REQ)  #  A new client socket
            self.socket.connect(self.ip)
        if self.mode == "server":
            self.responder.close()
            self.responder = self.context.socket(zmq.REP)  #  A new server socket
            self.responder.bind(self.ip)

    # A server will listen, receive and answer
    def listen(self): # check for message and return number of available messages
        return self.responder.poll(0)

    def receive(self): # receive message and return data to caller (this is a blocking call)
        return self.responder.recv(); # receive

    def answer(self,msg): # send data to the client
        self.responder.send(msg)
        # use responder.send_unicode(ret_msg); when sending unicode data

    # A client sends and receives with a blocking call.
    def send_and_receive(self,msg):
        self.socket.send(msg)
        return self.socket.recv()
        
    def close(self):
        if self.mode == "client":
            self.socket.close()
        if self.mode == "server":
            self.responder.close()

