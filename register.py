from argon2 import PasswordHasher
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from backend import database_connection as db
import sqlite3
import login, dialog


class Register(QtWidgets.QMainWindow):
	def __init__(self):
		super(Register, self).__init__()
		uic.loadUi("ui_files/register/register.ui", self)
		
		self._passwordHidden = True

		self.showPassButton = self.findChild(QtWidgets.QPushButton, "showPassButton") # Find the button
		self.showPassButton.clicked.connect(self.unhidePassword)

		self.submitButton = self.findChild(QtWidgets.QPushButton, "submitButton") # Find the button
		self.submitButton.clicked.connect(self.validateInputs)

		self.goToLoginButton = self.findChild(QtWidgets.QPushButton, "goToLoginButton") # Find the button
		self.goToLoginButton.clicked.connect(self.goToLogin)

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
		
		if len(username) <5 or len(username) > 30:
			errorDialog = dialog.Dialog("Username must be 5 - 30 characters long!", dialogName="Incorrect username.")
			errorDialog.exec_()
			self.usernameEdit.setText("")

		elif len(password) <5 or len(password) > 30:
			errorDialog = dialog.Dialog("Password must be 5 - 30 characters long!", dialogName="Incorrect password.")
			errorDialog.exec_()
			self.passwordEdit.setText("")
			self.passwordRetypeEdit.setText("")

		elif password != passwordRetype:
			errorDialog = dialog.Dialog("Passwords must match!", dialogName="Passwords do not match.")
			errorDialog.exec_()
			self.passwordEdit.setText("")
			self.passwordRetypeEdit.setText("")			

		else:
			password = PasswordHasher().hash(password)

			sql_query = f"""
			INSERT INTO user_data(USERNAME, PASSWORD)
			VALUES('{username}','{password}');
			"""
			db.c.execute(sql_query)
			db.conn.commit()

			print("done.")
			print(password)

	def goToLogin(self):
		self.window = login.Login()
		self.close()