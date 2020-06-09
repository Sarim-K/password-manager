from PyQt5 import QtCore, QtGui, QtWidgets, uic
from backend import database_connection as db
import sqlite3, dialog

class Preview(QtWidgets.QWidget):
	def __init__(self, password_row_data):
		super(Preview, self).__init__()
		uic.loadUi("ui_files/vault/preview.ui", self)

		self._password_row_data = password_row_data

		self.urlLabel.setText(password_row_data[1])

		self.expandButton = self.findChild(QtWidgets.QPushButton, "expandButton")
		self.expandButton.clicked.connect(self.expand)
		self.deleteButton = self.findChild(QtWidgets.QPushButton, "deleteButton")
		self.deleteButton.clicked.connect(self.remove)

	@property
	def id(self):
		return self._password_row_data[0]

	def remove(self):
		sql_query = f"SELECT name FROM sqlite_master WHERE name LIKE '{window.user_id}-folder-%' ORDER BY name ASC"
		folders = db.c.execute(sql_query).fetchall()
		
		for folder in folders:	
			sql_query = f"DELETE FROM '{folder[0]}' WHERE PASSWORD_ID = ?"
			db.c.execute(sql_query, (self.id,))		# remove it from any folders that exist
			db.conn.commit()

		sql_query = f"DELETE FROM '{window.user_id}-passwords' WHERE ID = ?"
		db.c.execute(sql_query, (self.id,))	# remove it from the passwords table
		db.conn.commit()

		if window.getCurrentItemPath():
			window.drawFolderPreviews()
		else:
			window.drawPreviews()
		window.drawExplorer()

	def expand(self):
		Dialog = expandDialog(self._password_row_data)
		Dialog.exec_()


class expandDialog(QtWidgets.QDialog):
	def __init__(self, password_row_data):
		super(expandDialog, self).__init__()
		uic.loadUi("ui_files/vault/expandDialog.ui", self)

		self.urlLabel.setText(password_row_data[1])
		self.usernameLabel.setText(password_row_data[2])
		self.emailLabel.setText(password_row_data[3])
		self.passwordLabel.setText(password_row_data[4])
		self.otherLabel.setText(password_row_data[5])

		self.show()


class enterFolderDialog(QtWidgets.QDialog):
	def __init__(self):
		super(enterFolderDialog, self).__init__()
		uic.loadUi("ui_files/vault/enterFolderDialog.ui", self)

		self.setWindowTitle("Enter folder name:")

		self.OKButton = self.findChild(QtWidgets.QPushButton, "OKButton")
		self.OKButton.clicked.connect(self.validateText)

		self.show()

	def saveText(self):
		self._text = self.lineEdit.text()
		self.close()

	def validateText(self):
		if "/" in self.lineEdit.text():
			Dialog = dialog.Dialog("You cannot use the '/' character!", dialogName="Invalid character used.")
			Dialog.exec_()
		else:
			self.saveText()

	@property
	def text(self):
		return f"{self._text}/"


class enterDataDialog(QtWidgets.QDialog):
	def __init__(self):
		super(enterDataDialog, self).__init__()
		uic.loadUi("ui_files/vault/enterDataDialog.ui", self)

		self.setWindowTitle("Enter details:")

		self.OKButton = self.findChild(QtWidgets.QPushButton, "OKButton")
		self.OKButton.clicked.connect(self.saveDetails)

		self.show()

	@property
	def details(self):
		return self._data_dict

	def saveDetails(self):
		data_dict = {}
		data_dict["url"] = self.urlEdit.text()
		data_dict["username"] = self.usernameEdit.text()
		data_dict["email"] = self.emailEdit.text()
		data_dict["password"] = self.passwordEdit.text()
		data_dict["other"] = self.otherEdit.text()
		self._data_dict = data_dict
		self.close()


class Vault(QtWidgets.QMainWindow):
	def __init__(self, user_id):
		super(Vault, self).__init__()
		uic.loadUi("ui_files/vault/vault.ui", self)

		self._user_id = user_id
		self.preview_dict = {}

		self.deleteFolderButton.clicked.connect(self.deleteFolder)
		self.Explorer.currentItemChanged.connect(self.drawFolderPreviews)
		self.newFolder.triggered.connect(self.addFolder)
		self.newEntry.triggered.connect(self.addEntry)

		self.drawPreviews(suppliedPreviewData=False)
		self.drawExplorer()
		self.Explorer.setColumnWidth(0, round(self.Explorer.width()*.75))

		self.show()


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
			sql_query = f"SELECT * FROM '{self.user_id}-passwords' WHERE ID = {password[0]}"
			data = db.c.execute(sql_query).fetchone()
			suppliedPreviewData.append(data)

		self.drawPreviews(suppliedPreviewData=suppliedPreviewData)

		
	def append_to_tree(self, node, c):
		if not c:
			return

		if c[0] not in node:
			node[c[0]] = {}

		self.append_to_tree(node[c[0]], c[1:])	


	def drawExplorer(self):
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
				sql_query = f"SELECT URL FROM '{self.user_id}-passwords' WHERE ID = {password[0]}"
				url = db.c.execute(sql_query).fetchone()
				folderArray2.append(f"{folder}{url[0]}".strip("/"))

		for path in folderArray2:
			self.append_to_tree(root, path.split('/'))

		self.fill_explorer(self.Explorer.invisibleRootItem(), root, folders)
		self.Explorer.expandAll()


	def fill_explorer(self, explorer_widget, dict_tree, folders):
		if type(dict_tree) is dict:
			for key, val in dict_tree.items():
				
				child = QtWidgets.QTreeWidgetItem()
				child.setText(0, key.replace(f"{self.user_id}-folder-", ""))

				for folder in folders:
					if key in folder:
						Type = "Folder"
						break
					else:
						Type = "Password"

				child.setText(1, Type)
				explorer_widget.addChild(child)
				self.fill_explorer(child, val, folders)
				

		elif type(dict_tree) is list:
			for val in dict_tree:
				child = QtWidgets.QTreeWidgetItem()
				explorer_widget.addChild(child)
			if type(val) is dict:      
				child.setText(0, '[dict]')
				self.fill_item(child, val)
			elif type(val) is list:
				child.setText(0, '[list]')
				self.fill_item(child, val)
			else:
				child.setText(0, val)
		else:
			child = QTreeWidgetItem()
			child.setText(0, dict_tree)
			explorer_widget.addChild(child)


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
			if x == max_preview_width:
				x = 0
				y += 1

			tempPreview = Preview(preview_data)
			self.preview_dict[tempPreview.id] = tempPreview
			self.gridLayout.addWidget(tempPreview, y, x)

			x += 1


	def addFolder(self):
		Dialog = enterFolderDialog()
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

		self.drawExplorer()
		if self.getCurrentItemPath():
			self.drawFolderPreviews()
		else:
			self.drawPreviews()


	def deleteFolder(self):
		path = self.getCurrentItemPath()
		print(path)
		if path == f"{self.user_id}-folder-All/":
			Dialog = dialog.Dialog("You cannot delete this folder!", dialogName="Invalid folder.")
			Dialog.exec_()
			return

		sql_query = f"SELECT name FROM sqlite_master WHERE name LIKE '{path}%' ORDER BY name ASC"
		folders = db.c.execute(sql_query).fetchall()

		for folder in folders:
			sql_query = f"DROP TABLE '{folder[0]}'"
			db.c.execute(sql_query)
			db.conn.commit()

		self.drawExplorer()
		if self.getCurrentItemPath():
			self.drawFolderPreviews()
		else:
			self.drawPreviews()


	def addEntry(self):
		Dialog = enterDataDialog()
		Dialog.exec_()

		try:
			details = Dialog.details
		except (UnboundLocalError, AttributeError):	#user exited dialog, didn't successfully input
			return

		sql_query = f"""
					INSERT OR REPLACE INTO '{self.user_id}-passwords'
					VALUES(?,?,?,?,?,?)
					"""
		db.c.execute(sql_query, (None, details["url"], details["username"], details["email"], details["password"], details["other"]))
		db.conn.commit()

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

		self.drawExplorer()
		if self.getCurrentItemPath():
			self.drawFolderPreviews()
		else:
			self.drawPreviews()	
		

if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	window = Vault(1)
	app.exec_()