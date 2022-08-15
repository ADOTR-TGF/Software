#!/usr/bin/python
#
# version 1.1
from __future__ import division
import sys
sys.path.append("/home/owner/.local/lib/python3.8/site-packages")
import zmq


class zmq_device():
    def __init__(self, ip, com_type="client", topic=""):
        self.com_type = com_type
        self.ip = ip
        self.topic = topic
        self.context = zmq.Context()
        if com_type == "server":
            self.responder = self.context.socket(zmq.REP)  # A server socket, responding to a client
            self.responder.bind(ip)
        elif com_type == "client":
            self.socket = self.context.socket(zmq.REQ)  # A client socket
            self.socket.connect(ip)
        elif com_type == "pair":
            self.socket = self.context.socket(zmq.PAIR)  # A paired socket
            self.socket.connect(ip)
        elif com_type == "publisher":
            self.publisher = self.context.socket(zmq.PUB)  # A publisher socket
            self.publisher.bind(ip)
        elif com_type == "subscriber":
            self.subscriber = self.context.socket(zmq.SUB)  # A subscriber socket
            self.subscriber.setsockopt(zmq.SUBSCRIBE, topic)  # Publisher sends topic+' '+ message
            self.subscriber.connect(ip)
        else:
            a = 1/0  # Force exception

    def echo(self):  # check for messages and echo if there is one
        xml_str = ""
        num_msg = self.responder.poll(1)
        if num_msg >= 1:
            xml_str = self.responder.recv()  # receive
            self.responder.send(xml_str)  # and echo back
        return num_msg, xml_str

    def poll(self, xml_str, wait=5):  # send a message and wait up to 'wait' seconds for an answer
        self.socket.send(xml_str)
        num_msg = self.socket.poll(wait)
        if num_msg >= 1:
            return self.socket.recv()
        else:
            return b""

    def renew(self):
        if self.com_type == "client":
            self.socket.close()
            self.socket = self.context.socket(zmq.REQ)  # A new client socket
            self.socket.connect(self.ip)
        elif self.com_type == "server":
            self.responder.close()
            self.responder = self.context.socket(zmq.REP)  # A new server socket
            self.responder.bind(self.ip)
        elif self.com_type == "pair":
            self.socket.close()
            self.socket = self.context.socket(zmq.PAIR)  # A paired socket
            self.socket.connect(self.ip)
        elif self.com_type == "publisher":
            self.publisher.close()
            self.publisher = self.context.socket(zmq.PUB)  # A publisher socket
            self.publisher.bind(self.ip)
        elif self.com_type == "subscriber":
            self.subscriber.close()
            self.subscriber = self.context.socket(zmq.SUB)  # A subscriber socket
            self.subscriber.setsockopt(zmq.SUBSCRIBE, self.topic)  # Publisher sends topic+' '+ message
            self.subscriber.connect(self.ip)

    # A server and a subscriber may check for the number of waiting messages
    def listen(self):  # check for message and return number of available messages
        if self.com_type == "server":
            return self.responder.poll(0)
        elif self.com_type == "subscriber":
            return self.subscriber.poll(0)
        else:
            return 0

    def receive(self):  # receive message and return data to caller (this is a blocking call)
        if self.com_type == "server":
            return self.responder.recv()  # receive
        elif self.com_type == "subscriber":
            return self.subscriber.recv()
        else:
            return b""

    def answer(self, xml_str):  # send data to the client
        self.responder.send(xml_str)
        # use responder.send_unicode(ret_msg); when sending unicode data

    # A client sends and receives with a blocking call.
    def send_and_receive(self, xml_str):
        self.socket.send(xml_str)
        return self.socket.recv()

    # For paired sockets this is a non-blocking send; and we don't expect answer
    # The delivery is guaranteed and data will pile up if the partner is slow or non-existent.
    # A publisher will cache messages that cannot be delivered to a connected subscriber
    # If no subscriber is connected, publisher will not keep messages.
    def send(self, xml_str):
        if self.com_type == "publisher":
            self.publisher.send(xml_str)
        elif self.com_type == "pair":
            self.socket.send(xml_str)

