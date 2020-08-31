# standard libaries
import sqlite3

# external libaries
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# local imports
from backend import database_connection as db
from backend import encryption as enc

class enterDataDialog(QtWidgets.QDialog):
	def __init__(self, user_id, key, password_row_data=["", "", "", "", "", "", ""]):
		super().__init__()
		uic.loadUi("ui_files/vault/enterDataDialog.ui", self)

		self.titleEdit.setText(password_row_data[1])
		self.urlEdit.setText(password_row_data[2])
		self.usernameEdit.setText(password_row_data[3])
		self.emailEdit.setText(password_row_data[4])
		self.passwordEdit.setText(password_row_data[5])
		self.otherEdit.setText(password_row_data[6])

		self.setWindowTitle("Enter details:")

		self.title_cache = password_row_data[1]
		self._user_id = user_id
		self._key = key

		self.generateButton.clicked.connect(self.generatePassword)
		self.OKButton.clicked.connect(self.validateText)

		self.show()


	@property
	def key(self):
		return self._key

	@property
	def details(self):
		try:
			return self._data_dict
		except AttributeError:	# user exited dialog without entering anything
			return

	@property
	def user_id(self):
		return self._user_id

	def validateText(self):
		if self.titleEdit.text() == "":
			Dialog = dialog.Dialog("Title cannot be Empty!", dialogName="Empty field.")
			Dialog.exec_()
			return

		elif self.title_cache == self.titleEdit.text():	# title hasn't changed - no point in validating it further
			self.saveDetails()
			return

		elif "/" in self.titleEdit.text():	# validate for '/' character
			Dialog = dialog.Dialog("You cannot use the '/' character in your title!", dialogName="Invalid character used.")
			Dialog.exec_()
			return

		elif self.titleEdit.text().startswith(f"{self._user_id}-folder-"):
			Dialog = dialog.Dialog("Invalid folder name.", dialogName="Invalid folder name.")
			Dialog.exec_()
			return

		sql_query = f"SELECT TITLE FROM '{self._user_id}-passwords'"
		tempTitles = db.c.execute(sql_query).fetchall()

		for title in tempTitles:
			decryptedTitle = enc.decrypt(self.key, title[0])
			if decryptedTitle.decode("utf-8") == self.titleEdit.text():
				Dialog = dialog.Dialog("This title has already been used!", dialogName="Existing title.")
				Dialog.exec_()
				return

		self.saveDetails()

	def saveDetails(self):
		data_dict = {}
		data_dict["title"] = enc.encrypt(self.key, f"{self.user_id}-password-{self.titleEdit.text()}")
		data_dict["url"] = enc.encrypt(self.key, self.urlEdit.text())
		data_dict["username"] = enc.encrypt(self.key, self.usernameEdit.text())
		data_dict["email"] = enc.encrypt(self.key, self.emailEdit.text())
		data_dict["password"] = enc.encrypt(self.key, self.passwordEdit.text())
		data_dict["other"] = enc.encrypt(self.key, self.otherEdit.text())
		self._data_dict = data_dict
		self.close()

	def generatePassword(self):
		Dialog = passwordGenerator()
		Dialog.exec_()
		return
