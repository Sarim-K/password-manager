from argon2 import PasswordHasher
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from backend import database_connection as db
import sqlite3
import register, dialog, vault


class Login(QtWidgets.QMainWindow):
	def __init__(self):
		super(Login, self).__init__()
		uic.loadUi("ui_files/login/login.ui", self)
		
		self._passwordHidden = True

		self.showPassButton = self.findChild(QtWidgets.QPushButton, "showPassButton") # Find the button
		self.showPassButton.clicked.connect(self.unhidePassword)

		self.submitButton = self.findChild(QtWidgets.QPushButton, "submitButton") # Find the button
		self.submitButton.clicked.connect(self.validateInputs)

		self.goToRegisterButton = self.findChild(QtWidgets.QPushButton, "goToRegisterButton") # Find the button
		self.goToRegisterButton.clicked.connect(self.goToRegister)

		self.show()

	def unhidePassword(self):
		if self._passwordHidden is True:
			self.passwordEdit.setEchoMode(QtWidgets.QLineEdit.Normal)
			self.showPassButton.setText("Hide Password")
			self._passwordHidden = False
		else:
			self.passwordEdit.setEchoMode(QtWidgets.QLineEdit.Password)
			self.showPassButton.setText("Show Password")
			self._passwordHidden = True

	def validateInputs(self):
		username = self.usernameEdit.text()
		password = self.passwordEdit.text()

		sql_query = f"SELECT * FROM user-data WHERE USERNAME = '{username}'"
		retrieved_data = db.c.execute(sql_query).fetchone()

		try:
			user_id, retrieved_password = retrieved_data[0], retrieved_data[2]
			PasswordHasher().verify(retrieved_password, password)
			Dialog = dialog.Dialog("Logged in successfully!", dialogName="Success.")
			Dialog.exec_()
		except Exception as e:
			print(e)
			Dialog = dialog.Dialog("Incorrect password!", dialogName="Incorrect password.")
			Dialog.exec_()
			return

		try:
			self.window = vault.Vault(user_id)
			self.close()
		except Exception as e:
			print(e)

	def goToRegister(self):
		self.window = register.Register()
		self.close()
