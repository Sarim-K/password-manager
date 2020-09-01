# standard libaries
import sqlite3
import random

# external libaries
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# local imports
from backend import database_connection as db
from backend import encryption as enc

class passwordGenerator(QtWidgets.QDialog):
	"""This class is a dialog used to randomly generate a sequence of characters, which one could use as a password."""
	def __init__(self):
		super().__init__()
		uic.loadUi("ui_files/vault/generatorDialog.ui", self)

		self.setWindowTitle("Password Generator")

		self.onlyInt = QtGui.QIntValidator()
		self.lengthEdit.setValidator(self.onlyInt)

		self.lengthSlider.setMinimum(1)
		self.lengthSlider.setMaximum(50)

		self.lengthSlider.valueChanged.connect(self.setLengthEdit)
		self.lengthEdit.textChanged.connect(self.setLengthSlider)
		self.generateButton.clicked.connect(self.generatePassword)
		self.copyButton.clicked.connect(self.copyToClipboard)

		self.show()


	def setLengthEdit(self):
		self.lengthEdit.setText(str(self.lengthSlider.value()))

	def setLengthSlider(self):
		try:
			self.lengthSlider.setValue(int(self.lengthEdit.text()))
		except ValueError:
			self.lengthEdit.setText(str(0))

	def generatePassword(self):
		generated = ""
		for _ in range(self.lengthSlider.value()):
			generated += random.choice("""0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[]^_`{|}~""")
		self.passwordEdit.setText(generated)


	def copyToClipboard(self):
		cb = QtWidgets.QApplication.clipboard()
		cb.clear(mode=cb.Clipboard)
		cb.setText(self.passwordEdit.text(), mode=cb.Clipboard)
