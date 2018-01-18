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

	def send(self, req):
		self.socket.send(json.dumps(req).encode("utf-8"))
		log.debug("send: %s" % str(req))

	def recv(self, timeout=0):
		if timeout <= 0:
			res = self.socket.recv()
		else:
			if self.socket in dict(self.poller.poll(timeout)):
				res = self.socket.recv()
			else:
				errstr = "no responce from remote host"
				log.error(errstr)
				raise ConnectionError(errstr)

		res = json.loads(res.decode("utf-8"))
		log.debug("recv: %s" % str(res))
		return res

	def drop(self):
		self.poller.unregister(self.socket)
		self.socket.close()

