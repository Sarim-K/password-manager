# standard libaries
import sqlite3
import random
import traceback

# external libaries
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut

# local imports
from vault_files.enterdatadialog import *
from vault_files.enterfolderdialog import *
from vault_files.passwordgenerator import *
from vault_files.preview import *
from vault_files.movefolder import *
from home_files import importacct
import vault_files.search as srch
from backend import encryption as enc
import dialog, settings


class ExplorerMethods:
	"""This is an abstract class which Vault inherits. This should never be instantiated, only inherited."""
	def drawExplorer(self, Explorer, dict_tree, folders):
		for key, val in dict_tree.items():
			child = QtWidgets.QTreeWidgetItem()

			for _ in folders:
				if key.startswith(f"{self._user_id}-password-"):
					Type = "Password"
					child.setText(0, key.replace(f"{self._user_id}-password-", ""))
					break
				else:
					Type = "Folder"
					child.setText(0, key.replace(f"{self._user_id}-folder-", ""))
					break

			child.setText(1, Type)

			Explorer.addChild(child)
			self.drawExplorer(child, val, folders)

	def getCurrentItemPath(self, passwordsEnabled=False):
		path_array = []
		final_path = ""

		item = self.Explorer.currentItem()

		if item is None:	# if user hasn't selected anything
			return

		if item.text(1) != "Folder" and passwordsEnabled == False:
			item = self.Explorer.currentItem().parent()	# selects the folder the password is in, rather than the password itself
		else:
			pass

		try:
			while True:
				item2 = item.parent()
				path_array.append(f"{item.text(0)}/")
				item = item2
		except AttributeError:
			path_array.reverse()

			for subpath in path_array:
				final_path += subpath
			final_path = f"{self._user_id}-folder-{final_path}"

			return final_path

	def prepareExplorerData(self):
		folderArray = []
		folderArray2 = []
		root = {}

		self.Explorer.clear()
		self.Explorer.setHeaderLabels(["Name", "Type"])

		sql_query = f"SELECT name FROM sqlite_master WHERE name LIKE '{self._user_id}-folder-%' ORDER BY name ASC"
		folders = db.c.execute(sql_query).fetchall()

		for folder in folders:
			folderArray.append(folder[0])

		folders = folderArray

		for folder in folderArray:
			sql_query = f"SELECT PASSWORD_ID FROM '{folder}'"
			password_ids = db.c.execute(sql_query).fetchall()

			folderArray2.append(folder.strip("/"))
			for password in password_ids:
				sql_query = f"SELECT TITLE FROM '{self._user_id}-passwords' WHERE ID = ?"
				title = db.c.execute(sql_query, (password[0],)).fetchone()

				try:
					title = enc.decrypt(self._key, title[0]).decode("utf-8")
				except TypeError:	# empty url
					pass

				folderArray2.append(f"{folder}{title}".strip("/"))

		for path in folderArray2:
			self.append_to_tree(root, path.split('/'))

		self.drawExplorer(self.Explorer.invisibleRootItem(), root, folders)
		self.Explorer.expandAll()

	def append_to_tree(self, node, c):
		if not c:
			return

		if c[0] not in node:
			node[c[0]] = {}

		self.append_to_tree(node[c[0]], c[1:])

	def get_all_folders(self, user_id):
		sql_query = f"SELECT name FROM sqlite_master WHERE name LIKE '{self._user_id}-folder-%' ORDER BY name ASC"
		folders = db.c.execute(sql_query).fetchall()
		return folders


class DrawPreviewMethods:
	"""This is an abstract class which Vault inherits. This should never be instantiated, only inherited."""

	def get_password_ids(self):
		final_path = self.getCurrentItemPath()

		sql_query = f"SELECT PASSWORD_ID FROM '{final_path}'"
		password_ids = db.c.execute(sql_query).fetchall()
		return password_ids


	def drawFolderPreviews(self):
		suppliedPreviewData = []

		try:
			password_ids = self.get_password_ids()
		except sqlite3.OperationalError:
			return

		for password in password_ids:
			sql_query = f"SELECT * FROM '{self._user_id}-passwords' WHERE ID = ?"
			data = db.c.execute(sql_query, (password[0],)).fetchone()
			suppliedPreviewData.append(data)

		self.drawPreviews(suppliedPreviewData=suppliedPreviewData)

	def clear_grid_layout(self):
		for i in reversed(range(self.gridLayout.count())): 	# clears the grid
				self.gridLayout.itemAt(i).widget().setParent(None)

	def get_passwords(self):
		sql_query = f"SELECT * FROM '{self._user_id}-passwords'"
		data = db.c.execute(sql_query).fetchall()
		return data

	def drawPreviews(self, suppliedPreviewData=False, decrypted=False):
		x, y = 0, 0
		max_preview_width = 4 #the previews are 200px long

		self.clear_grid_layout()

		if suppliedPreviewData == False:
			data = self.get_passwords()
		else:
			data = suppliedPreviewData
			del suppliedPreviewData

		for preview_data in data:
			decrypted_preview_data = []
			for column in preview_data:
				if decrypted == False:
					if type(column) != int:
						column = enc.decrypt(self._key, column).decode("utf-8")
				decrypted_preview_data.append(column)

			if x == max_preview_width:
				x = 0
				y += 1

			self.render_previews(decrypted_preview_data, y, x)

			x += 1

	def render_previews(self, preview_data, y, x):
		tempPreview = Preview(self._key, preview_data, self._user_id)
		tempPreview.changeMade.connect(self.drawPreviewsExplorer)
		self.preview_dict[tempPreview.id] = tempPreview
		self.gridLayout.addWidget(tempPreview, y, x)


class Vault(QtWidgets.QMainWindow, ExplorerMethods, DrawPreviewMethods):
	"""This class pulls from ui_files/vault/vault.ui for it's UI elements, and is the MainWindow once logged in."""
	def __init__(self, user_id, password_given):
		super().__init__()
		uic.loadUi("ui_files/vault/vault.ui", self)

		self._user_id = user_id
		self.preview_dict = {}
		self._password_given = password_given
		self._key = enc.create_key(password_given)

		self.settingsButton.clicked.connect(self.goToSettings)
		self.deleteFolderButton.clicked.connect(self.deleteFolder)
		self.editFolderButton.clicked.connect(self.editFolder)
		self.OKButton.clicked.connect(self.search)
		self.searchBar.textEdited.connect(self.search)
		self.Explorer.currentItemChanged.connect(self.drawFolderPreviews)
		self.newFolder.triggered.connect(self.addFolder)
		self.newEntry.triggered.connect(self.addEntry)
		self.newPassword.triggered.connect(self.generatePassword)

		self.newEntryShortcut = QShortcut(QKeySequence('Ctrl+E'), self)
		self.newEntryShortcut.activated.connect(self.addEntry)

		self.newFolderShortcut = QShortcut(QKeySequence('Ctrl+F'), self)
		self.newFolderShortcut.activated.connect(self.addFolder)

		self.generatePasswordShortcut = QShortcut(QKeySequence('Ctrl+N'), self)
		self.generatePasswordShortcut.activated.connect(self.generatePassword)

		_later_import_object = importacct.LaterImportAccount(self._user_id, self._key)
		del _later_import_object

		self.drawPreviews()
		self.prepareExplorerData()
		# self.Explorer.setColumnWidth(0, round(self.Explorer.width()*.75))
		# self.Explorer.itemAt(0, 0).setExpanded(0)
		self.show()

	def drawPreviewsExplorer(self):
		self.prepareExplorerData()
		if self.getCurrentItemPath():
			self.drawFolderPreviews()
		else:
			self.drawPreviews()

	def search(self):
		search_object = srch.Search(self.searchBar.text(), self._user_id, self._key)
		self.drawPreviews(suppliedPreviewData=search_object.results, decrypted=True)

	def addFolder(self):
		Dialog = enterFolderDialog(self._key)
		Dialog.exec_()

		try:
			folderName = Dialog.text
		except (UnboundLocalError, AttributeError): #user exited dialog, didn't successfully input
			return

		path = self.getCurrentItemPath()
		if path is None or path == f"{self._user_id}-folder-All/":
			folderName = f"{self._user_id}-folder-{folderName}"
		else:
			folderName = f"{path}{folderName}"

		sql_query = f"""
		CREATE TABLE '{folderName}' (
		PASSWORD_ID INTEGER PRIMARY KEY,
		FOREIGN KEY(PASSWORD_ID) REFERENCES '{self._user_id}-passwords'(ID) ON DELETE CASCADE
		);"""

		try:
			db.c.execute(sql_query)
			db.conn.commit()
		except sqlite3.OperationalError:
			Dialog = dialog.Dialog("Folder already exists!", dialogName="Pre-existing folder.")
			Dialog.exec_()

		Dialog.close()
		self.drawPreviewsExplorer()

	def deleteFolder(self):
		path = self.getCurrentItemPath()
		if path is None or path == f"{self._user_id}-folder-All/":
			Dialog = dialog.Dialog("You cannot delete this folder!", dialogName="Invalid folder.")
			Dialog.exec_()
			return

		sql_query = f"SELECT name FROM sqlite_master WHERE name LIKE '{path}%' ORDER BY name ASC"
		folders = db.c.execute(sql_query).fetchall()

		for folder in folders:
			sql_query = f"DROP TABLE '{folder[0]}'"
			db.c.execute(sql_query)
			db.conn.commit()

		self.drawPreviewsExplorer()

	def editFolder(self):
		final = ""
		path = self.getCurrentItemPath()
		if path is None or path == f"{self._user_id}-folder-All/":
			Dialog = dialog.Dialog("You cannot edit this folder!", dialogName="Invalid folder.")
			Dialog.exec_()
			return

		else:
			Dialog = enterFolderDialog(self._key, folderName=self.Explorer.currentItem().text(0))
			Dialog.exec_()
			try:
				folderName = Dialog.text
			except (UnboundLocalError, AttributeError): #user exited dialog, didn't successfully input
				return

			newPath = path.split("/")
			if len(newPath) == 2:	# not a subdirectory
				newPath = path.split("-")
				newPath[-1] = folderName
				for subpath in newPath:
					final += f"{subpath}-"
				final = final[:-1]

			else:
				newPath[-1] = folderName
				for subpath in newPath:
					final += f"{subpath}/"

		sql_query = f"""ALTER TABLE '{path}'
 					RENAME TO '{final}';
		  			"""

		try:
			db.c.execute(sql_query)
			db.conn.commit()
		except sqlite3.OperationalError:
			Dialog = dialog.Dialog("Folder already exists!", dialogName="Pre-existing folder.")
			Dialog.exec_()

		self.drawPreviewsExplorer()

	def addEntry(self):
		Dialog = enterDataDialog(self._user_id, self._key)
		Dialog.exec_()

		try:
			details = Dialog.details
		except (UnboundLocalError, AttributeError):	# user exited dialog, didn't successfully input
			return

		sql_query = f"""
					INSERT OR REPLACE INTO '{self._user_id}-passwords'
					VALUES(?,?,?,?,?,?,?)
					"""
		try:
			db.c.execute(sql_query, (None, details["title"], details["url"], details["username"], details["email"], details["password"], details["other"]))
			db.conn.commit()
		except TypeError:	# user exited without typing anything
			return

		path = self.getCurrentItemPath()
		if path is None:
			path = f"{self._user_id}-folder-All/"

		sql_query = f"""
					INSERT OR REPLACE INTO '{path}'
					VALUES(?)
					"""
		db.c.execute(sql_query, (db.c.lastrowid,))
		db.conn.commit()

		sql_query = f"""
					INSERT OR REPLACE INTO '{self._user_id}-folder-All/'
					VALUES(?)
					"""
		db.c.execute(sql_query, (db.c.lastrowid,))
		db.conn.commit()

		self.drawPreviewsExplorer()

	def generatePassword(self):
		Dialog = PasswordGenerator()
		Dialog.exec_()
		return

	def goToSettings(self):
		self.window = settings.Settings(self._user_id, self._password_given)
		self.close()


if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	window = Vault(1, "sarim786")
	app.exec_()
