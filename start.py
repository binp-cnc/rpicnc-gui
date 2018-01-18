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
		if self.addrinput.enabled():
			return self.addrinput.text()
		else:
			return None

	def setconn(self, conn):
		self.connected = conn is not None

		self.addrinput.setEnabled(not connected)

		if connected:
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

		label = QLabel("Size:")
		edit = QLineEdit()
		edit.setText("0")
		edit.setReadOnly(True)
		button = QPushButton("Measure")
		button.clicked.connect(lambda: self.conn.send({"type": "scan", "axis": self.name}))
		layout = QHBoxLayout()
		layout.addWidget(edit, 1)
		layout.addWidget(button)
		self.layout.addRow(label, layout)

		label = QLabel("Position:")
		edit = QLineEdit()
		edit.setText("0")
		edit.setReadOnly(True)
		self.layout.addRow(label, edit)

		label = QLabel("Move to:")
		edit = QLineEdit()
		edit.setText("0")
		button = QPushButton("Move")
		layout = QHBoxLayout()
		layout.addWidget(edit, 1)
		layout.addWidget(button)
		self.layout.addRow(label, layout)
		
		self.setLayout(self.layout)

		handle.bind("setconn", self.setconn)

	def setconn(self, conn):
		self.conn = conn


class Toolbar(QWidget):
	def __init__(self, handle):
		super().__init__()

		self.xaxis = Axis("x", handle=handle)
		self.yaxis = Axis("y", handle=handle)

		self.layout = QVBoxLayout()
		self.layout.addWidget(self.xaxis)
		self.layout.addWidget(self.yaxis)
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
		if addr is None:
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
		else:
			self.handle.call("setconn", self.conn)

		"""
		if res["status"] == "ok":
			log.debug("connected to '%s'" % addr)
		else:
			errstr = "response status is '%s'" % res["status"]
			log.error(errstr)
			raise ConnectionError(errstr)
		"""

		status = conn is not None
		self.view.setEnabled(status)

		if status:
			self.timer.start(1000)
		else:
			self.timer.stop()

	def timeout(self):
		print("timeout")

	def quit(self):
		if self.conn is not None:
			pass


app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())
