from PyQt5 import QtCore, QtGui, QtWidgets, uic

class Dialog(QtWidgets.QDialog):
	"""This class is a generic dialog, mostly used for error messages and other quick pop ups."""
	def __init__(self, errorMessage, dialogName=""):
		super().__init__()
		self._errorMessage = errorMessage
		uic.loadUi("ui_files/other/defaultDialog.ui", self)

		self.OK.clicked.connect(self.close)

		self.setWindowTitle(dialogName)
		self.label.setText(self._errorMessage)

		self.show()
