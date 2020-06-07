from PyQt5 import QtCore, QtGui, QtWidgets, uic
from backend import database_connection as db
import sqlite3, dialog
import pprint, json

class Preview(QtWidgets.QWidget):
	def __init__(self, password_row_data):
		super(Preview, self).__init__()
		uic.loadUi("ui_files/vault/preview.ui", self)

		self._password_row_data = password_row_data
		self._id = password_row_data[0]

		self.urlLabel.setText(password_row_data[1])
		self.nameLabel.setText(password_row_data[2])

		self.expandButton = self.findChild(QtWidgets.QPushButton, "expandButton")
		self.expandButton.clicked.connect(self.expand)

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


class enterDataDialog(QtWidgets.QDialog):
	def __init__(self, title=""):
		super(enterDataDialog, self).__init__()
		uic.loadUi("ui_files/vault/enterDataDialog.ui", self)

		self.setWindowTitle(title)

		self.OKButton = self.findChild(QtWidgets.QPushButton, "OKButton")
		self.OKButton.clicked.connect(self.saveText)

		self.show()

	def saveText(self):
		self._text = self.lineEdit.text()
		self.close()

	@property
	def text(self):
		return f"{self._text.replace('/', '')}/"


class Vault(QtWidgets.QMainWindow):
	def __init__(self, user_id):
		super(Vault, self).__init__()
		uic.loadUi("ui_files/vault/vault.ui", self)

		self._user_id = user_id
		self.preview_dict = {}

		self.Explorer = self.findChild(QtWidgets.QTreeWidget, "Explorer")

		self.newFolder.triggered.connect(self.addFolder)

		self.drawPreviews()
		self.drawExplorer()
		self.show()


	def append_to_tree(self, node, c):
		if not c:
			return

		if c[0] not in node:
			node[c[0]] = {}

		self.append_to_tree(node[c[0]], c[1:])	

	def drawExplorer(self):
		folderArray = []
		root = {}

		self.Explorer.clear()
		self.Explorer.setHeaderLabels(["Name", "Type"])

		sql_query = f"SELECT name FROM sqlite_master WHERE name LIKE '{self._user_id}-folder-%' ORDER BY name ASC"
		folders = db.c.execute(sql_query).fetchall()

		for folder in folders:
			folderArray.append(folder[0].strip("/"))

		print(folderArray)
		
		for path in folderArray:
			self.append_to_tree(root, path.split('/'))

		self.fill_widget(self.Explorer, root)


	def fill_item(self, item, value):
		if type(value) is dict:
			for key, val in sorted(value.items()):
				child = QtWidgets.QTreeWidgetItem()
				child.setText(0, key)
				item.addChild(child)
				self.fill_item(child, val)
		elif type(value) is list:
			for val in value:
				child = QtWidgets.QTreeWidgetItem()
				item.addChild(child)
			if type(val) is dict:      
				child.setText(0, '[dict]')
				self.fill_item(child, val)
			elif type(val) is list:
				child.setText(0, '[list]')
				self.fill_item(child, val)
			else:
				child.setText(0, val)              
			child.setExpanded(True)
		else:
			child = QTreeWidgetItem()
			child.setText(0, value)
			item.addChild(child)


	def fill_widget(self, widget, value):
		widget.clear()
		self.fill_item(widget.invisibleRootItem(), value)
		widget.expandAll()


	def drawPreviews(self):
		x, y = 0, 0
		max_preview_width = int(self.width()/200) #the previews are 200px long

		sql_query = f"SELECT * FROM '{self._user_id}-passwords'"
		data = db.c.execute(sql_query).fetchall()

		for preview_data in data:
			if x == max_preview_width:
				x = 0
				y += 1

			tempPreview = Preview(preview_data)
			self.preview_dict[tempPreview._id] = tempPreview
			self.gridLayout.addWidget(tempPreview, y, x)

			x += 1
	

	def addFolder(self):
		Dialog = enterDataDialog(title="Enter folder name:")
		Dialog.exec_()

		try:
			folderName = Dialog.text
		except AttributeError: #user exited dialog, didn't successfully input
			pass

		sql_query = f"""
		CREATE TABLE '{self._user_id}-folder-{folderName}' (
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


if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	window = Vault(1)
	app.exec_()
