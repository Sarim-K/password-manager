# standard libaries
import sqlite3
import random

# external libaries
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# local imports
from vault_files.enterdatadialog import *
from vault_files.enterfolderdialog import *
from vault_files.expanddialog import *
from vault_files.passwordgenerator import *
from vault_files.preview import *
import vault_files.search as srch
from backend import encryption as enc
import dialog, settings, importacct


class Vault(QtWidgets.QMainWindow):
	"""This class pulls from ui_files/vault/vault.ui for it's UI elements, and is the MainWindow once logged in."""
	def __init__(self, user_id, password_given):
		super().__init__()
		uic.loadUi("ui_files/vault/vault.ui", self)

		self._user_id = user_id
		self.preview_dict = {}
		self._key = enc.create_key(password_given)

		self.settingsButton.clicked.connect(self.goToSettings)
		self.deleteFolderButton.clicked.connect(self.deleteFolder)
		self.editFolderButton.clicked.connect(self.editFolder)
		self.OKButton.clicked.connect(self.search)
		self.Explorer.currentItemChanged.connect(self.drawFolderPreviews)
		self.newFolder.triggered.connect(self.addFolder)
		self.newEntry.triggered.connect(self.addEntry)
		self.newPassword.triggered.connect(self.generatePassword)

		self.enterKey = QtWidgets.QShortcut(QtGui.QKeySequence("Return"), self)	# return is enter for some reason
		self.enterKey.activated.connect(self.search)

		_later_import_object = importacct.LaterImportAccount(self._user_id, self._key)

		self.drawPreviews()
		self.prepareExplorerData()
		# self.Explorer.setColumnWidth(0, round(self.Explorer.width()*.75))
		# self.Explorer.itemAt(0, 0).setExpanded(0)
		self.show()


	@property
	def key(self):
		return self._key


	@property
	def user_id(self):
		return self._user_id


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
			final_path = f"{self.user_id}-folder-{final_path}"

			return final_path


	def drawFolderPreviews(self):
		suppliedPreviewData = []

		final_path = self.getCurrentItemPath()

		sql_query = f"SELECT PASSWORD_ID FROM '{final_path}'"
		try:
			password_ids = db.c.execute(sql_query).fetchall()
		except sqlite3.OperationalError:	# thrown when an event is called that gets rid of the current selection (i.e. creating a new folder)
			return

		for password in password_ids:
			sql_query = f"SELECT * FROM '{self.user_id}-passwords' WHERE ID = ?"
			data = db.c.execute(sql_query, (password[0],)).fetchone()
			suppliedPreviewData.append(data)

		self.drawPreviews(suppliedPreviewData=suppliedPreviewData)


	def append_to_tree(self, node, c):
		if not c:
			return

		if c[0] not in node:
			node[c[0]] = {}

		self.append_to_tree(node[c[0]], c[1:])


	def prepareExplorerData(self):
		folderArray = []
		folderArray2 = []
		root = {}

		self.Explorer.clear()
		self.Explorer.setHeaderLabels(["Name", "Type"])

		sql_query = f"SELECT name FROM sqlite_master WHERE name LIKE '{self.user_id}-folder-%' ORDER BY name ASC"
		folders = db.c.execute(sql_query).fetchall()

		for folder in folders:
			folderArray.append(folder[0])

		folders = folderArray

		for folder in folderArray:
			sql_query = f"SELECT PASSWORD_ID FROM '{folder}'"
			password_ids = db.c.execute(sql_query).fetchall()

			folderArray2.append(folder.strip("/"))
			for password in password_ids:
				sql_query = f"SELECT TITLE FROM '{self.user_id}-passwords' WHERE ID = ?"
				title = db.c.execute(sql_query, (password[0],)).fetchone()

				try:
					title = enc.decrypt(self.key, title[0]).decode("utf-8")
				except TypeError:	# empty url
					pass

				folderArray2.append(f"{folder}{title}".strip("/"))

		for path in folderArray2:
			self.append_to_tree(root, path.split('/'))

		self.drawExplorer(self.Explorer.invisibleRootItem(), root, folders)
		self.Explorer.expandAll()


	def drawExplorer(self, Explorer, dict_tree, folders):
		for key, val in dict_tree.items():
			child = QtWidgets.QTreeWidgetItem()

			for _ in folders:
				if key.startswith(f"{self.user_id}-password-"):
					Type = "Password"
					child.setText(0, key.replace(f"{self.user_id}-password-", ""))
					break
				else:
					Type = "Folder"
					child.setText(0, key.replace(f"{self.user_id}-folder-", ""))
					break

			child.setText(1, Type)

			Explorer.addChild(child)
			self.drawExplorer(child, val, folders)


	def drawPreviews(self, suppliedPreviewData=False):
		x, y = 0, 0
		max_preview_width = 4 #the previews are 200px long

		for i in reversed(range(self.gridLayout.count())): 	# clears the grid
				self.gridLayout.itemAt(i).widget().setParent(None)

		if suppliedPreviewData == False:
			sql_query = f"SELECT * FROM '{self.user_id}-passwords'"
			data = db.c.execute(sql_query).fetchall()
		else:
			data = suppliedPreviewData
			del suppliedPreviewData

		for preview_data in data:
			decrypted_preview_data = []
			for column in preview_data:
				if type(column) != int:
					column = enc.decrypt(self.key, column).decode("utf-8")
				decrypted_preview_data.append(column)


			if x == max_preview_width:
				x = 0
				y += 1

			tempPreview = Preview(self.key, decrypted_preview_data, self.user_id)
			tempPreview.changeMade.connect(self.drawPreviewsExplorer)
			self.preview_dict[tempPreview.id] = tempPreview
			self.gridLayout.addWidget(tempPreview, y, x)

			x += 1


	def drawPreviewsExplorer(self):
		self.prepareExplorerData()
		if self.getCurrentItemPath():
			self.drawFolderPreviews()
		else:
			self.drawPreviews()


	def search(self):
		srch.search(self.searchBar.text(), self.user_id, self.key)

		# self.drawPreviews(suppliedPreviewData=results)


	def addFolder(self):
		Dialog = enterFolderDialog(self.key)
		Dialog.exec_()

		try:
			folderName = Dialog.text
		except (UnboundLocalError, AttributeError): #user exited dialog, didn't successfully input
			return

		path = self.getCurrentItemPath()
		if path is None or path == f"{self.user_id}-folder-All/":
			folderName = f"{self.user_id}-folder-{folderName}"
		else:
			folderName = f"{path}{folderName}"

		sql_query = f"""
		CREATE TABLE '{folderName}' (
		PASSWORD_ID INTEGER PRIMARY KEY
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
		if path is None or path == f"{self.user_id}-folder-All/":
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
		if path is None or path == f"{self.user_id}-folder-All/":
			Dialog = dialog.Dialog("You cannot edit this folder!", dialogName="Invalid folder.")
			Dialog.exec_()
			return

		else:
			Dialog = enterFolderDialog(self.key, folderName=self.Explorer.currentItem().text(0))
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
		db.c.execute(sql_query)
		db.conn.commit()

		self.drawPreviewsExplorer()


	def addEntry(self):
		Dialog = enterDataDialog(self.user_id, self.key)
		Dialog.exec_()

		try:
			details = Dialog.details
		except (UnboundLocalError, AttributeError):	# user exited dialog, didn't successfully input
			return

		sql_query = f"""
					INSERT OR REPLACE INTO '{self.user_id}-passwords'
					VALUES(?,?,?,?,?,?,?)
					"""
		try:
			db.c.execute(sql_query, (None, details["title"], details["url"], details["username"], details["email"], details["password"], details["other"]))
			db.conn.commit()
		except TypeError:	# user exited without typing anything
			return

		path = self.getCurrentItemPath()
		if path is None:
			path = f"{self.user_id}-folder-All/"

		sql_query = f"""
					INSERT OR REPLACE INTO '{path}'
					VALUES(?)
					"""
		db.c.execute(sql_query, (db.c.lastrowid,))
		db.conn.commit()

		sql_query = f"""
					INSERT OR REPLACE INTO '{self.user_id}-folder-All/'
					VALUES(?)
					"""
		db.c.execute(sql_query, (db.c.lastrowid,))
		db.conn.commit()

		self.drawPreviewsExplorer()


	def generatePassword(self):
		Dialog = passwordGenerator()
		Dialog.exec_()
		return


	def goToSettings(self):
		self.window = settings.Settings(self.user_id, self.key)
		self.close()

if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	window = Vault(1, "sarim786")
	app.exec_()
