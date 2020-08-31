# standard libaries
import sqlite3

# external libaries
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# local imports
from backend import database_connection as db
from backend import encryption as enc
from vault_files.enterdatadialog import *
from vault_files.expanddialog import *

class Preview(QtWidgets.QWidget):
	changeMade = QtCore.pyqtSignal()

	def __init__(self, key, password_row_data, user_id):
		super().__init__()
		uic.loadUi("ui_files/vault/preview.ui", self)

		self._user_id = user_id
		self._key = key

		self._password_row_data = password_row_data
		self._password_row_data[1] = self._password_row_data[1].replace(f"{self.user_id}-password-", "")

		self.titleLabel.setText(password_row_data[1])

		self.expandButton.clicked.connect(self.expand)
		self.deleteButton.clicked.connect(self.remove)
		self.editButton.clicked.connect(self.edit)

	@property
	def user_id(self):
		return self._user_id


	@property
	def id(self):
		return self._password_row_data[0]


	@property
	def key(self):
		return self._key

	def remove(self):
		sql_query = f"SELECT name FROM sqlite_master WHERE name LIKE '{self.user_id}-folder-%' ORDER BY name ASC"
		folders = db.c.execute(sql_query).fetchall()

		for folder in folders:
			sql_query = f"DELETE FROM '{folder[0]}' WHERE PASSWORD_ID = ?"
			db.c.execute(sql_query, (self.id,))		# remove it from any folders that exist
			db.conn.commit()

		sql_query = f"DELETE FROM '{self.user_id}-passwords' WHERE ID = ?"
		db.c.execute(sql_query, (self.id,))	# remove it from the passwords table
		db.conn.commit()

		self.changeMade.emit()


	def expand(self):
		Dialog = expandDialog(self._password_row_data)
		Dialog.exec_()


	def edit(self):
		Dialog = enterDataDialog(self.user_id, self.key, password_row_data=self._password_row_data)
		Dialog.exec_()

		details = Dialog.details

		sql_query = f"""
					UPDATE '{self.user_id}-passwords'
					SET TITLE = ?,
					URL = ?,
					USERNAME = ?,
					EMAIL = ?,
					PASSWORD = ?,
					OTHER = ?
					WHERE ID = ?
					"""
		try:
			db.c.execute(sql_query, (details["title"], details["url"], details["username"], details["email"], details["password"], details["other"], self.id))
			db.conn.commit()
		except TypeError:	# user exited dialog without entering anything
			return

		self.changeMade.emit()
