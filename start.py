import sys
import zmq
import time
import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import logging as log

log.basicConfig(level=log.DEBUG, format="[%(levelname)s] %(message)s")


context = zmq.Context()


class Connect(QWidget):
	def __init__(self):
		super().__init__()

		self.socket = None

		self.label = QLabel("Address:")
		self.addrinput = QLineEdit()
		self.addrinput.setText("10.0.0.2:5556")

		self.button = QPushButton()
		#self.button.setToolTip("This is a <b>QPushButton</b> widget")

		self.layout = QHBoxLayout()
		self.layout.addWidget(self.label)
		self.layout.addWidget(self.addrinput, 1)
		self.layout.addWidget(self.button)
		self.setLayout(self.layout)

		self.setstatus(False)

	def connect(self):
		socket = context.socket(zmq.PAIR)
		addr = self.addrinput.text()
		if ":" not in addr:
			port = 5556
		else:
			addr, port = tuple(addr.split(":"))

		socket.connect("tcp://%s:%s" % (addr, port))
		socket.send(json.dumps({"type": "init"}).encode("utf-8"))

		poller = zmq.Poller()
		poller.register(socket, zmq.POLLIN)
		good = False
		if socket in dict(poller.poll(1000)):
			if json.loads(socket.recv().decode("utf-8"))["status"] == "ok":
				log.debug("connected to '%s'" % addr)
				self.setstatus(True)
				good = True
		
		if not good:
			log.error("cannot connect to '%s'" % addr)
			QMessageBox.warning(self, "Error", "cannot connect to '%s'" % addr)

	def disconnect(self):
		log.debug("disconnected")
		self.setstatus(False)

	def setstatus(self, connected):
		try:
			self.button.clicked.disconnect()
		except TypeError:
			pass
		self.addrinput.setEnabled(not connected)

		if connected:
			self.button.setText("Disconnect")
			self.button.clicked.connect(self.disconnect)
		else:
			self.button.setText("Connect")
			self.button.clicked.connect(self.connect)

class Pannel(QWidget):
	def __init__(self, scene, view):
		super().__init__()

		self.view = view
		self.scene = scene

		self.connect = Connect()

		self.layout = QVBoxLayout()
		self.layout.setAlignment(Qt.AlignTop)
		self.layout.addWidget(self.connect)
		self.setLayout(self.layout)


class Window(QMainWindow):
	def __init__(self):
		super().__init__()
		QToolTip.setFont(QFont('SansSerif', 10))

		self.scene = QGraphicsScene()
		self.view = QGraphicsView()
		self.view.setScene(self.scene)

		self.pannel = Pannel(self.scene, self.view)

		self.layout = QHBoxLayout()
		self.layout.addWidget(self.view, 2)
		self.layout.addWidget(self.pannel, 1)

		self.layoutwrapper = QWidget()
		self.layoutwrapper.setLayout(self.layout)
		self.setCentralWidget(self.layoutwrapper)

		self.resize(900, 600)
		self.setWindowTitle("RPi CNC")
		self.show()

	"""
	def sync(self):
		msg = b"client request"
		socket.send(msg)
		print("[send] '%s'" % msg)

		msg = socket.recv()
		print("[recv] '%s'" % msg)
	"""

app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())
