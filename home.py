# standard libraries
import sqlite3

# external libraries
from argon2 import PasswordHasher
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog

# local imports
from backend import database_connection as db
import dialog, vault, importacct


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
		self.login_dialog = Login()
		self.login_dialog.logged_in.connect(self.login)
		self.login_dialog.exec_()

	def goToRegister(self):
		Dialog = Register()
		Dialog.exec_()

	def goToImport(self):
		_ = importacct.InitialImportAccount()


class Login(QtWidgets.QDialog):
	"""This class is a dialog used to log in."""
	logged_in = QtCore.pyqtSignal()
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

	def validateInputs(self):
		username = self.usernameEdit.text()
		self._password = self.passwordEdit.text()

		try:
			self._user_id, retrieved_password = self.get_user_id_and_password(username)
			PasswordHasher().verify(retrieved_password, self._password)
			self.logged_in.emit()	# this is emitted, and then the MainWindow handles closing itself
			self.close()
		except Exception as e:
			Dialog = dialog.Dialog("Incorrect password!", dialogName="Incorrect password.")
			Dialog.exec_()


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

		# validate for username length
		if len(username) <5 or len(username) > 30:
			Dialog = dialog.Dialog("Username must be 5 - 30 characters long!", dialogName="Incorrect username.")
			Dialog.exec_()
			self.usernameEdit.setText("")
			return

		# validate for password length
		elif len(password) <5 or len(password) > 30 or len(passwordRetype) <5 or len(passwordRetype) > 30:
			Dialog = dialog.Dialog("Password must be 5 - 30 characters long!", dialogName="Incorrect password.")
			Dialog.exec_()
			self.passwordEdit.setText("")
			self.passwordRetypeEdit.setText("")
			return

		# validate for matching passwords
		elif password != passwordRetype:
			Dialog = dialog.Dialog("Passwords must match!", dialogName="Passwords do not match.")
			Dialog.exec_()
			self.passwordEdit.setText("")
			self.passwordRetypeEdit.setText("")
			return

		# validate for existing account
		sql_query = f"SELECT USERNAME FROM 'user-data' WHERE USERNAME = ?"
		retrieved_data = db.c.execute(sql_query, (username,))
		try:
			retrieved_data.fetchone()[0]
			Dialog = dialog.Dialog("Username already registered!", dialogName="Account already exists.")
			Dialog.exec_()
			return
		except TypeError:
			password = PasswordHasher().hash(password)

		# insert username & password into database
		sql_query = f"""
		INSERT OR REPLACE INTO 'user-data'
		VALUES(?, ?, ?, ?)
		"""
		db.c.execute(sql_query, (None, username, password, 0))
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
		PASSWORD_ID INTEGER PRIMARY KEY
		);"""
		db.c.execute(sql_query)
		db.conn.commit()

		Dialog = dialog.Dialog("Account registered successfully!", dialogName="Success.")
		Dialog.exec_()

		self.usernameEdit.setText("")
		self.passwordEdit.setText("")
		self.passwordRetypeEdit.setText("")
