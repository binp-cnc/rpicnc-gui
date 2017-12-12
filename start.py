import sys
import zmq
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QToolTip
from PyQt5.QtGui import QFont


class Window(QWidget):
	def __init__(self, socket):
		super().__init__()
		self.socket = socket

		QToolTip.setFont(QFont('SansSerif', 10))

		self.button = QPushButton('Sync', self)
		self.button.setToolTip('This is a <b>QPushButton</b> widget')
		self.button.resize(self.button.sizeHint())
		self.button.move(50, 50)
		self.button.clicked.connect(lambda: self.sync())

		self.resize(800, 600)
		self.setWindowTitle("RPi CNC")
		self.show()

	def sync(self):
		msg = b"client request"
		socket.send(msg)
		print("[send] '%s'" % msg)

		msg = socket.recv()
		print("[recv] '%s'" % msg)


context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://10.0.0.2:5556")
print("[info] connected")

app = QApplication(sys.argv)
window = Window(socket)
sys.exit(app.exec_())
