from Queue import Queue
from database_connect import DatabaseManager
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, task, abstract
from twisted.python import log

import twisted.names.client
from loopix_client import LoopixClient
import struct

class LoopixConnector(DatagramProtocol):
    def __init__(self, host, port, client):
        self.client = client
        self.host = host
        self.port = port
        self.local_port = port + 1001
        self.internal_port = port + 1000

    def datagramReceived(self, data, (host, port)):
        dest_high, dest_low = struct.unpack('>BB', data[2:4])
        dest_idx = dest_high * 256 + dest_low
        print "send msg to " + str(dest_idx)
        self.client.sendto(data, dest_idx)
        # self.reply_to_frontend(data)

    # reply to frontend
    def reply(self, message):
        idx_high, idx_low = struct.unpack('>BB', message[0:2])
        idx = idx_high * 256 + idx_low
        print "received message from " + str(idx)
        self.transport.write(message, ("127.0.0.1", self.local_port))

    def startProtocol(self):
        self.client.sendto("Hello World", 0)
