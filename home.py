# standard libraries
import sqlite3

# external libraries
from argon2 import PasswordHasher
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog

# local imports
from backend import database_connection as db
from home_files import login
from home_files import register
from home_files import importacct
import dialog, vault


class Home(QtWidgets.QMainWindow):
	"""This class pulls from ui_files/home/home.ui for it's UI elements; it is the initial MainWindow."""
	def __init__(self):
		super().__init__()
		uic.loadUi("ui_files/home/home.ui", self)

		self.goToLoginButton.clicked.connect(self.goToLogin)
		self.goToRegisterButton.clicked.connect(self.goToRegister)
		self.goToImportButton.clicked.connect(self.goToImport)

		self.show()

	def login(self):
		self.window = vault.Vault(self.login_dialog.user_id, self.login_dialog.password)
		self.close()

	def goToLogin(self):
		self.login_dialog = login.Login()
		self.login_dialog.logged_in.connect(self.login)
		self.login_dialog.exec_()

	def goToRegister(self):
		Dialog = register.Register()
		Dialog.exec_()

	def goToImport(self):
		_ = importacct.InitialImportAccount()
