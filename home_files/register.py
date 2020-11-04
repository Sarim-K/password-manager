# standard libraries
import sqlite3

# external libraries
from argon2 import PasswordHasher
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# local imports
from backend import database_connection as db
import dialog

class Register(QtWidgets.QDialog):
	"""This class is a dialog used to register an account."""
	def __init__(self):
		super().__init__()
		uic.loadUi("ui_files/home/register.ui", self)

		self._passwordHidden = True

		self.showPassButton.clicked.connect(self.unhidePassword)
		self.submitButton.clicked.connect(self.validateInputs)

		self.show()

	def unhidePassword(self):
		if self._passwordHidden is True:
			self.passwordEdit.setEchoMode(QtWidgets.QLineEdit.Normal)
			self.passwordRetypeEdit.setEchoMode(QtWidgets.QLineEdit.Normal)
			self.showPassButton.setText("Hide Password")
			self._passwordHidden = False
		else:
			self.passwordEdit.setEchoMode(QtWidgets.QLineEdit.Password)
			self.passwordRetypeEdit.setEchoMode(QtWidgets.QLineEdit.Password)
			self.showPassButton.setText("Show Password")
			self._passwordHidden = True

	def validateInputs(self):
		username = self.usernameEdit.text()
		password = self.passwordEdit.text()
		passwordRetype = self.passwordRetypeEdit.text()

		# validate for matching passwords
		if password != passwordRetype:
			Dialog = dialog.Dialog("Passwords must match!", dialogName="Passwords do not match.")
			Dialog.exec_()
			self.passwordEdit.setText("")
			self.passwordRetypeEdit.setText("")
			return

		# validate for existing account
		sql_query = f"SELECT USERNAME FROM 'user-data' WHERE USERNAME = ?"
		retrieved_data = db.c.execute(sql_query, (username,)).fetchone()
		if retrieved_data:
			Dialog = dialog.Dialog("Username already registered!", dialogName="Account already exists.")
			Dialog.exec_()
			return
		else:
			password = PasswordHasher().hash(password)
			self.create_account(username, password)

	def create_account(self, username, password):
		# insert username & password into database
		sql_query = f"""
		INSERT OR REPLACE INTO 'user-data'
		VALUES(?, ?, ?, ?, ?)
		"""
		db.c.execute(sql_query, (None, username, password, None, None))
		db.conn.commit()

		# get user's id
		sql_query = f"SELECT USER_ID FROM 'user-data' WHERE USERNAME = ?"
		user_id = db.c.execute(sql_query, (username,)).fetchone()[0]

		# create user's passwords table
		sql_query = f"""
		CREATE TABLE '{user_id}-passwords' (
		ID INTEGER PRIMARY KEY,
		TITLE		TEXT	(1, 100),
		URL    		TEXT    (1, 100),
		USERNAME    TEXT    (1, 100),
		EMAIL   	TEXT    (1, 100),
		PASSWORD   	TEXT    (1, 100),
		OTHER  		TEXT    (1, 100)
		);"""
		db.c.execute(sql_query)
		db.conn.commit()

		# create user's all folder table
		sql_query = f"""
		CREATE TABLE '{user_id}-folder-All/' (
		PASSWORD_ID INTEGER PRIMARY KEY,
		FOREIGN KEY(PASSWORD_ID) REFERENCES '{user_id}-passwords'(ID) ON DELETE CASCADE
		);"""
		db.c.execute(sql_query)
		db.conn.commit()

		Dialog = dialog.Dialog("Account registered successfully!", dialogName="Success.")
		Dialog.exec_()

		self.usernameEdit.setText("")
		self.passwordEdit.setText("")
		self.passwordRetypeEdit.setText("")
