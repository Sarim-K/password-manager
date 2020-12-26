# external libaries
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# external libraries
from argon2 import PasswordHasher

# local imports
from backend import database_connection as db
from backend import encryption as enc
import dialog

class EmailAddressMethods:
	"""This is an abstract class which Details inherits. This should never be instantiated, only inherited."""
	@property
	def email_address(self):
		if "@" in self.lineEdit.text() and "." in self.lineEdit.text().split("@")[1]:
			return self.lineEdit.text()
		else:
			return None

	@property
	def existing_email_address(self):
		sql_query = f"SELECT EMAIL FROM 'user-data' WHERE USER_ID = ?"
		retrieved_data = db.c.execute(sql_query, (self._user_id,)).fetchone()[0]
		return retrieved_data

	def set_email_address(self):
		if self.email_address:
			enc_email_address = enc.encrypt(self._key, self.email_address)
			sql_query = f"""
						UPDATE 'user-data'
						SET EMAIL = ?
						WHERE USER_ID = ?
						"""

			db.c.execute(sql_query, (enc_email_address, self._user_id))
			db.conn.commit()
			Dialog = dialog.Dialog("Email updated successfully!", dialogName="Success.")
			Dialog.exec_()
		else:
			Dialog = dialog.Dialog("Invalid email!", dialogName="Invalid email.")
			Dialog.exec_()

	def remove_email_address(self):
		sql_query = f"""
					UPDATE 'user-data'
					SET EMAIL = ?
					WHERE USER_ID = ?
					"""

		db.c.execute(sql_query, (None, self._user_id))
		db.conn.commit()
		self.lineEdit.setText("")
		Dialog = dialog.Dialog("Email updated successfully!", dialogName="Success.")
		Dialog.exec_()


class PasswordChangeMethods:
	"""This is an abstract class which Details inherits. This should never be instantiated, only inherited."""
	@property
	def new_master_password(self):
		return self.passEdit.text()

	def validate(self):
		return len(self.passEdit.text()) > 3

	def get_passwords(self):
		passwords = {}
		sql_query = f"SELECT * FROM '{self._user_id}-passwords'"
		password_list = db.c.execute(sql_query).fetchall()
		return password_list

	def decrypt_data(self, data):
		decrypted_data = []
		for row in data:
			decrypted_row = []
			for cell in row:
				if type(cell) != int:
					cell = enc.decrypt(self._key, cell).decode("utf-8")
				decrypted_row.append(cell)
			decrypted_data.append(decrypted_row)
		return decrypted_data

	def encrypt_data(self, data):
		self._key = enc.create_key(self.new_master_password)
		encrypted_data = []
		for row in data:
			encrypted_row = []
			for cell in row:
				if type(cell) != int:
					cell = enc.encrypt(self._key, cell)
				encrypted_row.append(cell)
			encrypted_data.append(encrypted_row)
		return encrypted_data

	def reformat_data(self, data):
		new_data = []
		for entry in data:
			entry.append(entry[0])
			entry.pop(0)
			new_data.append(entry)
		return new_data

	def update_passwords(self, data):
		sql_query = f"""UPDATE '{self._user_id}-passwords'
					SET TITLE = ?,
					URL = ?,
					USERNAME = ?,
					EMAIL = ?,
					PASSWORD = ?,
					OTHER = ?
					WHERE ID = ?
					"""
		db.c.executemany(sql_query, data)

	def change_master_password(self):	# hash
		password = PasswordHasher().hash(self.new_master_password)
		sql_query = f"""UPDATE 'user-data'
					SET PASSWORD = ?
					WHERE USER_ID = ?"""
		db.c.execute(sql_query, (password, self._user_id))
		db.conn.commit()

	def change_pass(self):
		bool = self.validate()
		if not bool:
			Dialog = dialog.Dialog("Password must be 4 characters or longer!", dialogName="Password is not long enough.")
			Dialog.exec_()
			self.passEdit.setText("")
			return

		data = self.get_passwords()
		data = self.decrypt_data(data)
		data = self.encrypt_data(data)
		data = self.reformat_data(data)
		self.update_passwords(data)
		self.change_master_password()
		self.password_changed.emit()


class Details(QtWidgets.QWidget, EmailAddressMethods, PasswordChangeMethods):
	password_changed = QtCore.pyqtSignal()
	deleted_account = QtCore.pyqtSignal()
	"""This class pulls from ui_files/settings/details.ui for it's UI elements, and is a widget within the Settings MainWindow."""
	def __init__(self, user_id, password_given):
		super().__init__()
		uic.loadUi("ui_files/settings/details.ui", self)

		self._key = enc.create_key(password_given)
		self._user_id = user_id

		if self.existing_email_address:
			decrypted_existing_email = enc.decrypt(self._key, self.existing_email_address).decode("utf-8")
			self.lineEdit.setText(decrypted_existing_email)

		self.removeEmail.clicked.connect(self.remove_email_address)
		self.OKButton.clicked.connect(self.set_email_address)
		self.passwordOKButton.clicked.connect(self.change_pass)
		self.deleteAccount.clicked.connect(self.delete_account)

	def get_password(self):
		sql_query = f"SELECT PASSWORD FROM 'user-data' WHERE USER_ID = ?"
		retrieved_data = db.c.execute(sql_query, (self._user_id,)).fetchone()
		return retrieved_data[0]	# user_id, password

	def delete_account(self):
		retrieved_password = self.get_password()
		Dialog = dialog.InputDialog("Verify your password in order to delete your account:", dialogName="Input password.", passwordMode=True)
		Dialog.exec_()

		try:
			PasswordHasher().verify(retrieved_password, Dialog.input)
		except Exception as e:
			Dialog = dialog.Dialog("Incorrect password!", dialogName="Incorrect password.")
			Dialog.exec_()
			return

		sql_query = f"""SELECT name
			FROM sqlite_master
			WHERE type = 'table'
			AND name LIKE '{self._user_id}-%'
			"""
		tables = db.c.execute(sql_query).fetchall()

		for table in tables:
			sql_query = f"DROP TABLE '{table[0]}'"
			db.c.execute(sql_query)

		sql_query = f"DELETE FROM 'user-data' WHERE USER_ID = ?"
		db.c.execute(sql_query, (self._user_id,))
		db.conn.commit()

		self.deleted_account.emit()
