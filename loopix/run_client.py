import petlib.pack
import os
import sys
current_path = os.getcwd()
print "Current Path: %s" % current_path
sys.path += [current_path]

from loopix_client import LoopixClient
from loopix_connector import LoopixConnector
import petlib.pack
from twisted.internet import reactor
from twisted.application import service, internet
from sphinxmix.SphinxParams import SphinxParams


file_name = os.path.basename(__file__)
port = int(file_name[file_name.find('_', 5) + 1: file_name.find('.')])
if not (os.path.exists("secretClient-%d.prv" % port) and os.path.exists("publicClient-%d.bin" % port)):
    raise Exception("Key parameter files not found")

secret = petlib.pack.decode(file("secretClient-%d.prv" % port, "rb").read())
sec_params = SphinxParams(header_len=1024)
try:
    data = file("publicClient-%d.bin" % port, "rb").read()
    _, name, port, host, _, prvinfo = petlib.pack.decode(data)

    client = LoopixClient(sec_params, name, port, host, provider_id = prvinfo, privk = secret)
    connector = LoopixConnector(host, port, client)
    client.set_frontend(connector)

    udp_server = internet.UDPServer(port, client)
    udp_connector = internet.UDPServer(port + 1000, connector)
    
    application = service.Application("Client")
    udp_server.setServiceParent(application)
    udp_connector.setServiceParent(application)

    # reactor.listenUDP(port, client)
    # reactor.listenUDP(port + 1000, connector)
    # reactor.run()

except Exception, e:
    print e