# standard libaries
import sqlite3

# external libaries
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# local imports
from backend import database_connection as db
from backend import encryption as enc

class expandDialog(QtWidgets.QDialog):
	"""This class is a dialog used to display a read-only version of a password entry."""
	def __init__(self, password_row_data):
		super().__init__()
		uic.loadUi("ui_files/vault/expandDialog.ui", self)

		self.displayDetails(password_row_data)

	def displayDetails(self, password_row_data):
		self.titleLabel.setText(password_row_data[1])
		self.urlLabel.setText(password_row_data[2])
		self.usernameLabel.setText(password_row_data[3])
		self.emailLabel.setText(password_row_data[4])
		self.passwordLabel.setText(password_row_data[5])
		self.otherLabel.setText(password_row_data[6])

		self.show()
