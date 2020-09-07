# standard libaries
import sqlite3

# external libaries
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# local imports
from backend import database_connection as db
from backend import encryption as enc
from vault_files.enterdatadialog import *
import vault_files.movefolder as mf

class Preview(QtWidgets.QWidget):
	"""This class is used to display a small summary of a password entry; displayed in a grid on the right side of the vault."""
	changeMade = QtCore.pyqtSignal()
	def __init__(self, key, password_row_data, user_id):
		super().__init__()
		uic.loadUi("ui_files/vault/preview.ui", self)

		self._user_id = user_id
		self._key = key

		self._password_row_data = password_row_data
		self._password_row_data[1] = self._password_row_data[1].replace(f"{self._user_id}-password-", "")

		self.titleLabel.setText(password_row_data[1])

		self.moveButton.clicked.connect(self.move)
		self.deleteButton.clicked.connect(self.remove)
		self.editButton.clicked.connect(self.edit)

	@property
	def id(self):
		return self._password_row_data[0]

	def remove(self):
		sql_query = f"SELECT name FROM sqlite_master WHERE name LIKE '{self._user_id}-folder-%' ORDER BY name ASC"
		folders = db.c.execute(sql_query).fetchall()

		for folder in folders:
			sql_query = f"DELETE FROM '{folder[0]}' WHERE PASSWORD_ID = ?"
			db.c.execute(sql_query, (self.id,))		# remove it from any folders that exist
			db.conn.commit()

		sql_query = f"DELETE FROM '{self._user_id}-passwords' WHERE ID = ?"
		db.c.execute(sql_query, (self.id,))	# remove it from the passwords table
		db.conn.commit()

		self.changeMade.emit()

	def move(self):
		sql_query = f"SELECT name FROM sqlite_master WHERE name LIKE '{self._user_id}-folder-%' ORDER BY name ASC"
		folders = db.c.execute(sql_query).fetchall()

		for folder in folders:
			if folder[0] != f"{self._user_id}-folder-All/":
				sql_query = f"DELETE FROM '{folder[0]}' WHERE PASSWORD_ID = ?"
				db.c.execute(sql_query, (self.id,))		# remove it from any folders that exist
			db.conn.commit()

		Dialog = mf.MoveFolder(self._user_id, self.id, folders)
		Dialog.exec_()

		if Dialog.completed:
			sql_query = f"""
						INSERT OR REPLACE INTO '{Dialog.selection}'
						VALUES(?)
						"""
			db.c.execute(sql_query, (self.id,))
			db.conn.commit()

			self.changeMade.emit()


	def edit(self):
		Dialog = enterDataDialog(self._user_id, self._key, password_row_data=self._password_row_data)
		Dialog.exec_()

		details = Dialog.details

		sql_query = f"""
					UPDATE '{self._user_id}-passwords'
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
