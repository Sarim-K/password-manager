# standard libaries
import json

# external libaries
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# local imports
from backend import database_connection as db
from backend import encryption as enc
from settings_files import details
from settings_files import export
from settings_files import vaultchecker
import home
import vault
import dialog


class Settings(QtWidgets.QMainWindow):
	"""This class pulls from ui_files/settings/settings.ui for it's UI elements, and is a MainWindow."""
	def __init__(self, user_id, password_given):
		super().__init__()
		uic.loadUi("ui_files/settings/settings.ui", self)

		self._user_id = user_id
		self._password_given = password_given
		self._key = enc.create_key(password_given)
		self._password_changed = False

        # creates the individual settings widgets
		self._details_obj = details.Details(self._user_id, self._password_given)
		self._details_obj.password_changed.connect(self.set_password_changed)
		self._details_obj.deleted_account.connect(self.logout)
		self._export_obj = export.Export(self._user_id, self._key)
		self._vault_checker_obj = vaultchecker.VaultChecker(self._user_id, self._password_given)


		self.goBackButton.clicked.connect(self.goBack)
		self.logOutButton.clicked.connect(self.logout)

		self.initUI()
		self.show()

        # adds the individual settings widgets to the QTabWidget
	def initUI(self):
		self.tabwidget = QtWidgets.QTabWidget()
		self.tabwidget.addTab(self._export_obj, "Export")
		self.tabwidget.addTab(self._details_obj, "Details")
		self.tabwidget.addTab(self._vault_checker_obj, "Vault Checker")
		self.gridLayout.addWidget(self.tabwidget, 0, 0)

	def set_password_changed(self):
		self._password_changed = True

	def logout(self):
		self.window = home.Home()
		self.hide()

	def goBack(self):
		if self._password_changed:
			self.window = vault.Vault(self._user_id, self._details_obj.new_master_password)
		else:
			self.window = vault.Vault(self._user_id, self._password_given)
		self.close()
