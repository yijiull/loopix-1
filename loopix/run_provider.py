import os
import sys
current_path = os.getcwd()
print "Current path %s" % current_path
sys.path += [current_path]

from loopix_provider import LoopixProvider
from twisted.internet import reactor
from twisted.application import service, internet
import petlib.pack
from sphinxmix.SphinxParams import SphinxParams

port = int(sys.argv[1])
if not (os.path.exists("secretProvider-%d.prv" % port) and os.path.exists("publicProvider-%d.bin" % port)):
	raise Exception("Key parameter files not found")

secret = petlib.pack.decode(file("secretProvider-%d.prv" % port, "rb").read())
_, name, port, host, _ = petlib.pack.decode(file("publicProvider-%dbin" % port, "rb").read())
sec_params = SphinxParams(header_len=1024)

try:
	provider = LoopixProvider(sec_params, name, port, host, privk=secret, pubk=None)
	# reactor.listenUDP(port, provider)
	# reactor.run()
 	udp_server = internet.UDPServer(port, provider)
 	application = service.Application("Provider")
 	udp_server.setServiceParent(application)

except Exception, e:
	print str(e)
