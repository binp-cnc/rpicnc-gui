import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import logging as log

import core

log.basicConfig(level=log.DEBUG, format="[%(levelname)s] %(message)s")


class Handle:
	def __init__(self):
		self.calls = {}

	def call(self, name, *args, **kwargs):
		log.debug("handle call '%s(%s, %s)'" % (name, str(args), str(kwargs)))
		for callback in self.calls[name]:
			callback(*args, **kwargs)

	def bind(self, name, callback):
		try:
			self.calls[name].append(callback)
		except KeyError:
			self.calls[name] = [callback]


class Connect(QWidget):
	def __init__(self, handle):
		super().__init__()

		handle.bind("setconn", self.setconn)

		self.connected = False

		self.label = QLabel("Address:")
		self.addrinput = QLineEdit()
		self.addrinput.setText("10.0.0.2:5556")

		self.button = QPushButton()
		self.button.clicked.connect(lambda: handle.call("connect", self.getaddr()))
		#self.button.setToolTip("This is a <b>QPushButton</b> widget")

		self.layout = QHBoxLayout()
		self.layout.addWidget(self.label)
		self.layout.addWidget(self.addrinput, 1)
		self.layout.addWidget(self.button)
		self.setLayout(self.layout)

	def getaddr(self):
		if not self.connected:
			return self.addrinput.text()
		else:
			return None

	def setconn(self, conn):
		self.connected = conn is not None

		self.addrinput.setEnabled(not self.connected)

		if self.connected:
			self.button.setText("Disconnect")
		else:
			self.button.setText("Connect")

class Axis(QGroupBox):
	def __init__(self, name, handle):
		super().__init__()

		self.conn = None

		self.name = name
		self.setTitle("Axis %s" % self.name.upper())

		self.layout = QFormLayout()

		label = QLabel("Size")
		edit = QLineEdit()
		edit.setText("0")
		edit.setReadOnly(True)
		button = QPushButton("Scan")
		button.clicked.connect(lambda: self.conn.send({"type": "scan", "axis": self.name}))
		layout = QHBoxLayout()
		layout.addWidget(edit, 1)
		layout.addWidget(button)
		self.layout.addRow(label, layout)

		self.sizeedit = edit

		label = QLabel("Position")
		edit = QLineEdit()
		edit.setText("0")
		edit.setReadOnly(True)
		self.layout.addRow(label, edit)
		
		self.setLayout(self.layout)

		handle.bind("setconn", self.setconn)
		handle.bind("setsize", self.setsize)

	def setconn(self, conn):
		self.conn = conn

	def setsize(self, axis, size):
		if axis == self.name:
			self.sizeedit.setText(str(size))

class Motion(QGroupBox):
	def __init__(self, handle):
		super().__init__()

		self.layout = QFormLayout()
		self.conn = None

		self.setTitle("Motion")

		label = QLabel("Axis")
		xlabel = QLabel("X")
		ylabel = QLabel("Y")
		layout = QHBoxLayout()
		layout.addWidget(xlabel, 1)
		layout.addWidget(ylabel, 1)
		self.layout.addRow(label, layout)

		alabel = QLabel("Acceleration")
		xaedit = QLineEdit()
		xaedit.setText("10000")
		yaedit = QLineEdit()
		yaedit.setText("10000")
		layout = QHBoxLayout()
		layout.addWidget(xaedit, 1)
		layout.addWidget(yaedit, 1)
		self.layout.addRow(alabel, layout)

		vlabel = QLabel("Speed")
		xvedit = QLineEdit()
		xvedit.setText("2000")
		yvedit = QLineEdit()
		yvedit.setText("2000")
		layout = QHBoxLayout()
		layout.addWidget(xvedit, 1)
		layout.addWidget(yvedit, 1)
		self.layout.addRow(vlabel, layout)

		plabel = QLabel("Relative position")
		xpedit = QLineEdit()
		xpedit.setText("0")
		ypedit = QLineEdit()
		ypedit.setText("0")
		layout = QHBoxLayout()
		layout.addWidget(xpedit, 1)
		layout.addWidget(ypedit, 1)
		self.layout.addRow(plabel, layout)

		button = QPushButton("Move")
		button.clicked.connect(self.move)
		self.layout.addRow(button, None)

		self.setLayout(self.layout)

		self.ins = {
			"acc": (xaedit, yaedit),
			"vel": (xvedit, yvedit),
			"pos": (xpedit, ypedit),
		}

		handle.bind("setconn", self.setconn)

	def move(self):
		self.conn.send({
			"type": "move",
			"pos": [int(self.ins["pos"][0].text()), int(self.ins["pos"][1].text())],
			"vel": [int(self.ins["vel"][0].text()), int(self.ins["vel"][1].text())],
			"acc": [int(self.ins["acc"][0].text()), int(self.ins["acc"][1].text())],
		})

	def setconn(self, conn):
		self.conn = conn


class Toolbar(QWidget):
	def __init__(self, handle):
		super().__init__()

		self.xaxis = Axis("x", handle=handle)
		self.yaxis = Axis("y", handle=handle)
		self.motion = Motion(handle=handle)

		self.layout = QVBoxLayout()
		self.layout.addWidget(self.xaxis)
		self.layout.addWidget(self.yaxis)
		self.layout.addWidget(self.motion)
		self.setLayout(self.layout)

		handle.bind("setconn", lambda conn: self.setEnabled(conn is not None))


class Pannel(QWidget):
	def __init__(self, scene, view, handle):
		super().__init__()

		self.view = view
		self.scene = scene

		self.connect = Connect(handle=handle)
		self.toolbar = Toolbar(handle=handle)

		self.layout = QVBoxLayout()
		self.layout.setAlignment(Qt.AlignTop)
		self.layout.addWidget(self.connect)
		self.layout.addWidget(self.toolbar)
		self.setLayout(self.layout)


class Window(QMainWindow):
	def __init__(self):
		super().__init__()
		QToolTip.setFont(QFont('SansSerif', 10))

		self.handle = Handle()
		self.conn = None

		self.scene = QGraphicsScene()
		self.view = QGraphicsView()
		self.view.setScene(self.scene)

		self.pannel = Pannel(self.scene, self.view, handle=self.handle)

		self.layout = QHBoxLayout()
		self.layout.addWidget(self.view, 1)
		self.layout.addWidget(self.pannel, 1)

		self.layoutwrapper = QWidget()
		self.layoutwrapper.setLayout(self.layout)
		self.setCentralWidget(self.layoutwrapper)

		self.resize(800, 600)
		self.setWindowTitle("RPi CNC")
		self.show()

		self.timer = QTimer()
		self.timer.timeout.connect(self.timeout)

		self.handle.bind("connect", self.connect)

		self.connect(None)

	def connect(self, addr):
		self.timer.stop()

		if addr is None:
			if self.conn is not None:
				self.conn.send({"type": "init"})
				self.conn.drop()
				self.conn = None
			self.handle.call("setconn", None)
			return
		

		if ":" not in addr:
			port = 5556
		else:
			addr, port = tuple(addr.split(":"))

		try:
			self.conn = core.Connection(addr, port)
		except core.ConnectionError as ce:
			QMessageBox.warning(self, "Error", str(ce))
		
		self.conn.send({"type": "init"})

		if self.conn is not None:
			self.timer.start(100)


	def timeout(self):
		while True:
			msg = self.conn.recv()
			if msg is None:
				break

			if msg["type"] == "init":
				if msg["status"] == "ok":
					self.handle.call("setconn", self.conn)

			if msg["type"] == "quit":
				if msg["status"] == "ok":
					self.handle.call("setconn", None)

			if msg["type"] == "scan":
				if msg["status"] == "ok":
					self.handle.call("setsize", msg["axis"], msg["size"])

		log.debug("timeout")

	def quit(self):
		if self.conn is not None:
			pass


app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())
