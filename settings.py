from backend import database_connection as db
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import dialog
import json


class Settings(QtWidgets.QMainWindow):
	"""This class pulls from ui_files/settings/settings.ui for it's UI elements, and is a MainWindow."""
	export_clicked = QtCore.pyqtSignal()
	def __init__(self, user_id, key):
		super().__init__()
		uic.loadUi("ui_files/settings/settings.ui", self)

		self._user_id = user_id
		self._key = key

		export_obj = Export(self._user_id, self._key)
		self.gridLayout.addWidget(export_obj, 1, 0)

		self.show()


class Export(QtWidgets.QWidget):
	"""This class pulls from ui_files/settings/export.ui for it's UI elements, and is a widget within the Settings MainWindow."""
	def __init__(self, user_id, key):
		super().__init__()
		uic.loadUi("ui_files/settings/export.ui", self)

		self._user_id = user_id
		self._key = key

		self.exportButton.clicked.connect(self.export)

	def export(self):
		user_dict = {}
		contents, passwords, details = self.export_to_dict()
		user_dict["contents"] = contents
		user_dict["passwords"] = passwords
		user_dict["details"] = details

		with open("export.psm", 'w') as json_file:
  			json.dump(user_dict, json_file)

		Dialog = dialog.Dialog("Account successfully exported as 'export.psm!'", dialogName="Export complete.")
		Dialog.exec_()

	def export_to_dict(self):
		contents = {}

		folder_names = self.get_folder_names()
		for folder in folder_names:
			folder_content = self.get_folder_content(folder)
			contents[folder] = folder_content

		passwords = self.get_passwords()
		passwords = self.decode_passwords(passwords)

		details = self.get_details()
		return contents, passwords, details

	def get_folder_names(self):
		final = []
		sql_query = f"SELECT name FROM sqlite_master WHERE name LIKE '{self._user_id}-folder-%' ORDER BY name ASC"
		folders = db.c.execute(sql_query).fetchall()

		for folder in folders:
			final.append(folder[0])
		return final

	def get_folder_content(self, folder_path):
		final = []
		sql_query = f"SELECT * FROM '{folder_path}'"
		ids = db.c.execute(sql_query).fetchall()

		for id in ids:
			final.append(id[0])
		return final

	def get_passwords(self):
		passwords = {}
		sql_query = f"SELECT * FROM '{self._user_id}-passwords'"
		password_list = db.c.execute(sql_query).fetchall()
		return password_list

	def decode_passwords(self, password_list):
		passwords_dict = {}
		for password_entry in password_list:
			current = []
			for data in password_entry:
				try:
					current.append(data.decode("utf-8"))
				except Exception:
					current.append(data)
			passwords_dict[current[0]] = current[1:]
		return passwords_dict

	def get_details(self):
		sql_query = "SELECT USERNAME, PASSWORD FROM 'user-data' WHERE USER_ID = ?"
		username, password = db.c.execute(sql_query, (self._user_id,)).fetchone()
		return username, password
