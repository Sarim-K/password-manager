from PyQt5 import QtCore, QtGui, QtWidgets, uic
from backend import database_connection as db
import sqlite3 

class Preview(QtWidgets.QWidget):
	def __init__(self):
		super(Preview, self).__init__()
		uic.loadUi("ui_files/vault/preview.ui", self)

		self.expandButton = self.findChild(QtWidgets.QPushButton, "expandButton") # Find the button
		self.expandButton.clicked.connect(self.expand)

	def expand(self):
		print()


class Vault(QtWidgets.QMainWindow):
	def __init__(self):
		super(Vault, self).__init__()
		uic.loadUi("ui_files/vault/vault.ui", self)

		for x in range(3):
			for y in range(5):
				self.gridLayout.addWidget(Preview(), y, x)

		self.show()

if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	window = Vault()
	app.exec_()