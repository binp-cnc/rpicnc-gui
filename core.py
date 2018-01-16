import json
import zmq
import logging as log

log.basicConfig(level=log.DEBUG, format="[%(levelname)s] %(message)s")


zmqcontext = zmq.Context()


class ConnectionError(Exception):
		def __init__(self, info):
			super().__init__(info)

class Connection:
	def __init__(self, addr, port):
		self.address = addr
		self.port = port

		self.socket = zmqcontext.socket(zmq.PAIR)

		self.socket.connect("tcp://%s:%s" % (self.address, self.port))

		self.poller = zmq.Poller()
		self.poller.register(self.socket, zmq.POLLIN)

		res = self.send({"type": "init"})
		log.debug("response: %s" % str(res))
		if res["status"] == "ok":
			log.debug("connected to '%s'" % addr)
		else:
			errstr = "response status is '%s'" % res["status"]
			log.error(errstr)
			raise ConnectionError(errstr)
			

	def send(self, req):
		self.socket.send(json.dumps(req).encode("utf-8"))

		if self.socket in dict(self.poller.poll(4000)):
			res = json.loads(self.socket.recv().decode("utf-8"))
			return res
		else:
			errstr = "no responce from remote host"
			log.error(errstr)
			raise ConnectionError(errstr)

	def drop(self):
		self.poller.unregister(self.socket)
		self.socket.close()

