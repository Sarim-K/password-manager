import sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import register, dialog


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
		
		if len(username) <5 or len(username) > 30:
			errorDialog = dialog.Dialog("Username must be 5 - 30 characters long!", dialogName="Incorrect username.")
			errorDialog.exec_()
			self.usernameEdit.setText("")

		elif len(password) <5 or len(password) > 30:
			errorDialog = dialog.Dialog("Password must be 5 - 30 characters long!", dialogName="Incorrect password.")
			errorDialog.exec_()
			self.passwordEdit.setText("")

		else:
			sql_query = f"SELECT PASSWORD FROM user_data WHERE USERNAME = '{username}'"
			retrieved_data = c.execute(sql_query)
			retrieved_data = retrieved_data.fetchone()[0]

			if password == retrieved_data:
				print("Logged in successfully.")

	def goToRegister(self):
		self.window = register.Register()
		self.close()
