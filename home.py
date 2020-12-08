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

		self._2fa_status = None

		self.goToLoginButton.clicked.connect(self.goToLogin)
		self.goToRegisterButton.clicked.connect(self.goToRegister)
		self.goToImportButton.clicked.connect(self.goToImport)

		self.show()

	def login(self):
		if self._2fa_status is True or self._2fa_status is None: #if 2fa has been entered sucesfully, or 2fa isnt enabled
			self.window = vault.Vault(self.login_dialog.user_id, self.login_dialog.password)
		self.close()

	def tfa(self):
		Dialog = dialog.InputDialog("Input your 2fa code.", dialogName="Two Factor Authentication.")
		Dialog.exec_()
		inputted_code = Dialog.input

		if str(inputted_code) == str(self.login_dialog.tfa_obj.code):
			self._2fa_status = True
		else:
			self._2fa_status = False

        # switch to login page
	def goToLogin(self):
		self.login_dialog = login.Login()
		self.login_dialog.two_factor_check.connect(self.tfa)
		self.login_dialog.logged_in.connect(self.login)
		self.login_dialog.exec_()

        # switch to register page
	def goToRegister(self):
		Dialog = register.Register()
		Dialog.exec_()

        # open import account functionality
	def goToImport(self):
		_ = importacct.InitialImportAccount()
