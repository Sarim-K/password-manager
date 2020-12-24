# standard libaries
import sqlite3

# external libaries
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# local imports
from backend import database_connection as db
from backend import encryption as enc
import dialog

class enterFolderDialog(QtWidgets.QDialog):
	"""This class is a dialog used to create / edit a folder."""
	def __init__(self, key, folderName=""):
		super().__init__()
		uic.loadUi("ui_files/vault/enterFolderDialog.ui", self)

		self._cache = folderName

		self.setWindowTitle("Enter folder name:")
		self.lineEdit.setText(folderName)

		self.OKButton.clicked.connect(self.validateText)

		self.show()

	@property
	def text(self):
		return f"{self._text}/"

	def saveText(self):
		self._text = self.lineEdit.text()
		self.close()


	def validateText(self):
		if self.lineEdit.text() == "":
			Dialog = dialog.Dialog("You cannot have a blank folder name!", dialogName="Blank folder name.")
			Dialog.exec_()
			self.close()

		elif self.lineEdit.text() == self._cache:
			self.close()

		elif "/" in self.lineEdit.text():
			Dialog = dialog.Dialog("You cannot use the '/' character!", dialogName="Invalid character used.")
			Dialog.exec_()
			self.close()
		else:
			self.saveText()
