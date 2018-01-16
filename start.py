import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import logging as log

import core

log.basicConfig(level=log.DEBUG, format="[%(levelname)s] %(message)s")


class Connect(QWidget):
	def __init__(self, cnxcb):
		super().__init__()

		self.connection = None

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

		self.cnxcb = cnxcb

	def connect(self):
		addr = self.addrinput.text()
		if ":" not in addr:
			port = 5556
		else:
			addr, port = tuple(addr.split(":"))

		try:
			self.connection = core.Connection(addr, port)
			self.cnxcb(self.connection)
		except core.ConnectionError as ce:
			QMessageBox.warning(self, "Error", str(ce))

		self.connection.send({ "type": "scan", "axis": "x" })

	def disconnect(self):
		self.connection.drop()
		self.connection = None

		log.debug("disconnected")
		self.cnxcb(self.connection)

	def setcnx(self, connected):
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

class Axis(QGroupBox):
	def __init__(self, name):
		super().__init__()

		self.name = name
		self.setTitle("Axis %s" % self.name.upper())

		self.layout = QFormLayout()

		label = QLabel("Size:")
		edit = QLineEdit()
		edit.setText("0")
		edit.setReadOnly(True)
		button = QPushButton("Measure")
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


class Toolbar(QWidget):
	def __init__(self):
		super().__init__()

		self.xaxis = Axis("x")
		self.yaxis = Axis("y")

		self.layout = QVBoxLayout()
		self.layout.addWidget(self.xaxis)
		self.layout.addWidget(self.yaxis)
		self.setLayout(self.layout)


class Pannel(QWidget):
	def __init__(self, scene, view, cnxcb):
		super().__init__()

		self.view = view
		self.scene = scene

		self.connect = Connect(cnxcb)
		self.toolbar = Toolbar()

		self.layout = QVBoxLayout()
		self.layout.setAlignment(Qt.AlignTop)
		self.layout.addWidget(self.connect)
		self.layout.addWidget(self.toolbar)
		self.setLayout(self.layout)

		self.cnxcb = cnxcb

	def setcnx(self, conn):
		status = conn is not None
		self.connect.setcnx(status)
		self.toolbar.setEnabled(status)


class Window(QMainWindow):
	def __init__(self):
		super().__init__()
		QToolTip.setFont(QFont('SansSerif', 10))

		self.scene = QGraphicsScene()
		self.view = QGraphicsView()
		self.view.setScene(self.scene)

		self.pannel = Pannel(self.scene, self.view, self.setcnx)

		self.layout = QHBoxLayout()
		self.layout.addWidget(self.view, 1)
		self.layout.addWidget(self.pannel, 1)

		self.layoutwrapper = QWidget()
		self.layoutwrapper.setLayout(self.layout)
		self.setCentralWidget(self.layoutwrapper)

		self.resize(800, 600)
		self.setWindowTitle("RPi CNC")
		self.show()

		self.setcnx(None)

	def setcnx(self, conn):
		status = conn is not None
		self.view.setEnabled(status)
		self.pannel.setcnx(conn)


app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())
