# standard libraries
import sqlite3
import random

# external libraries
from argon2 import PasswordHasher
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# local imports
from backend import database_connection as db
from backend import encryption as enc
from home_files import gen_two_factor as tfa
import dialog, vault

class Login(QtWidgets.QDialog):
	"""This class is a dialog used to log in."""
	logged_in = QtCore.pyqtSignal()
	two_factor_check = QtCore.pyqtSignal()
	def __init__(self):
		super().__init__()
		uic.loadUi("ui_files/home/login.ui", self)

		self._passwordHidden = True
		self._user_id = None
		self._password = None

		self.showPassButton.clicked.connect(self.unhidePassword)
		self.submitButton.clicked.connect(self.validateInputs)

		self.show()

	@property
	def user_id(self):
		return self._user_id

	@property
	def password(self):
		return self._password

	def unhidePassword(self):
		if self._passwordHidden is True:
			self.passwordEdit.setEchoMode(QtWidgets.QLineEdit.Normal)
			self.showPassButton.setText("Hide Password")
			self._passwordHidden = False
		else:
			self.passwordEdit.setEchoMode(QtWidgets.QLineEdit.Password)
			self.showPassButton.setText("Show Password")
			self._passwordHidden = True

	def get_user_id_and_password(self, username):
		sql_query = f"SELECT * FROM 'user-data' WHERE USERNAME = ?"
		retrieved_data = db.c.execute(sql_query, (username,)).fetchone()
		return retrieved_data[0], retrieved_data[2]	# user_id, password

	def get_email(self):
		sql_query = f"SELECT EMAIL FROM 'user-data' WHERE USER_ID = ?"
		retrieved_data = db.c.execute(sql_query, (self._user_id,)).fetchone()
		return retrieved_data

	def validateInputs(self):
		username = self.usernameEdit.text()
		self._password = self.passwordEdit.text()

		try:
			self._user_id, retrieved_password = self.get_user_id_and_password(username)
			PasswordHasher().verify(retrieved_password, self._password)

			email = self.get_email()[0]
			if email:         
				key = enc.create_key(self._password)
				email = enc.decrypt(key, email).decode("utf-8")

				self.tfa_obj = tfa.GenerateTwoFactorAuth(email)
				self.two_factor_check.emit()

			self.logged_in.emit()	# this is emitted, and then the MainWindow handles closing itself
			self.close()

		except Exception:
			Dialog = dialog.Dialog("Incorrect password!", dialogName="Incorrect password.")
			Dialog.exec_()
