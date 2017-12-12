import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QToolTip
from PyQt5.QtGui import QFont


class Window(QWidget):
	def __init__(self):
		super().__init__()

		QToolTip.setFont(QFont('SansSerif', 10))

		self.movebutton = QPushButton('Move', self)
		self.movebutton.setToolTip('This is a <b>QPushButton</b> widget')
		self.movebutton.resize(self.movebutton.sizeHint())
		self.movebutton.move(50, 50)

		self.resize(800, 600)
		self.setWindowTitle("RPi CNC")
		self.show()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = Window()
	sys.exit(app.exec_())
