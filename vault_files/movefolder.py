# external libaries
from PyQt5 import QtCore, QtGui, QtWidgets, uic


class MoveFolder(QtWidgets.QDialog):
	"""This class is a dialog used to select a folder to move the password to."""
	def __init__(self, user_id, password_id, folders):
		super().__init__()
		uic.loadUi("ui_files/vault/moveFolder.ui", self)

		self._user_id = user_id
		self._password_id = password_id
		self._completed = False

		self.format_folder_list(folders)

		self.OKButton.clicked.connect(self.add_to_new_folder)
		self.listWidget.addItems(self._folders)

		self.show()

	def format_folder_list(self, folders):
		self._folders = []
		for folder in folders:
			if folder[0] != f"{self._user_id}-folder-All/":
				self._folders.append(folder[0])

	def save_selection(self):
		self._selection = self.listWidget.selectedItems()[0].text()

	def add_to_new_folder(self):
		try:
			self._completed = True
			self.save_selection()
			self.close()
		except IndexError:
			return

	@property
	def selection(self):
		return self._selection

	@property
	def completed(self):
		return self._completed
