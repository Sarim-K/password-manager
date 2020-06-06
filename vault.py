from PyQt5 import QtCore, QtGui, QtWidgets, uic
from backend import database_connection as db
import sqlite3, dialog

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
	def __init__(self):
		super(enterDataDialog, self).__init__()
		uic.loadUi("ui_files/vault/enterDataDialog.ui", self)

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

		self.newFolder.triggered.connect(self.addFolder)

		self.drawPreviews()
		self.drawExplorer()
		self.show()

	def drawExplorer(self):
		self.Explorer.clear()
		self.Explorer.setHeaderLabels(["Name", "Type"])

		sql_query = f"SELECT name FROM sqlite_master WHERE name LIKE '{self._user_id}-folder-%'"
		folders = db.c.execute(sql_query).fetchall()

		for folder in folders:
			sanitisedFolderName = folder[0].replace(f"{self._user_id}-folder-","").strip("/")
			f1 = QtWidgets.QTreeWidgetItem(self.Explorer, [sanitisedFolderName, "Folder"])

			sql_query = f"SELECT PASSWORD_ID FROM '{folder[0]}'"
			password_ids = db.c.execute(sql_query).fetchall()

			for password in password_ids:
				sql_query = f"SELECT URL FROM '{self._user_id}-passwords' WHERE ID = '{password[0]}'"
				password_url = db.c.execute(sql_query).fetchone()

				QtWidgets.QTreeWidgetItem(f1, [password_url[0], "Password"])


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
		Dialog = enterDataDialog()
		Dialog.exec_()
		folderName = Dialog.text

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
