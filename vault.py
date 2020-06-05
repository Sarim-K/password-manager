from PyQt5 import QtCore, QtGui, QtWidgets, uic
from backend import database_connection as db
import sqlite3

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
		return self._text


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
		self.Explorer.setHeaderLabels(["Name", "Type"])

		a = QtWidgets.QTreeWidgetItem(self.Explorer, ["test", "Folder"])
		a1 = QtWidgets.QTreeWidgetItem(a, ["test2", "Password"])

		b = QtWidgets.QTreeWidgetItem(self.Explorer, ["test3", "Folder"])
		b1 = QtWidgets.QTreeWidgetItem(b, ["test4", "Password"])

		ba = QtWidgets.QTreeWidgetItem(b, ["test5", "Folder"])
		ba1 = QtWidgets.QTreeWidgetItem(ba, ["test6", "Password"])


	def drawPreviews(self):
		x, y = 0, 0
		max_preview_width = int(self.width()/200) #the previews are 200px long

		sql_query = f"SELECT * FROM '{self._user_id}_passwords'"
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
		CREATE TABLE '{self._user_id}_folder_{folderName}' (
		PASSWORD_ID INTEGER PRIMARY KEY
		);"""
		db.c.execute(sql_query)
		db.conn.commit()
		print("Done.")

if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	window = Vault(1)
	app.exec_()