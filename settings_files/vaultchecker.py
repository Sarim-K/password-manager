import webbrowser
import re
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from backend import encryption as enc
from backend import database_connection as db

class SharedMethods:
	def calculate_strength(self, string):
		if len(string)>=8:
		    if bool(re.match('((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,30})', string)) == True:
		        return "Strong"
		    elif bool(re.match('((\d*)([a-z]*)([A-Z]*)([!@#$%^&*]*).{8,30})', string)) == True:
		        return "Medium"
		else:
		    return "Weak"


class Report(QtWidgets.QWidget, SharedMethods):
	def __init__(self, report_data):	# title, url, password
		super().__init__()
		uic.loadUi("ui_files/settings/vault_checker/report.ui", self)
		self._report_data = report_data

		size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
		self.setSizePolicy(size_policy)

		self.titleLabel.setText(report_data[0][self.get_user_id_length(report_data[0])+10:])
		self.strengthLabel.setText(self.calculate_strength(report_data[1]))

	get_user_id_length = lambda self, title: len(str(title.split("-")[0]))

	def launch_site(self):
		webbrowser.open(self._report_data[2], new=0, autoraise=True)


class ReportLayout(QtWidgets.QWidget):
	def __init__(self, list_of_report_data):
		super().__init__()

		self._overall_list = []

		self._scores = {"Weak": 1,
						"Weak - Medium": 2,
						"Medium": 3,
						"Medium - Strong": 4,
						"Strong": 5}

		self._reverse_scores = {1: "Weak",
								2: "Weak - Medium",
								3: "Medium",
								4: "Medium - Strong",
								5: "Strong"}

		self.gridLayout = QtWidgets.QGridLayout()
		for report_data in list_of_report_data:
			self.report = Report(report_data)
			self._overall_list.append(self._scores[self.report.strengthLabel.text()])
			self.gridLayout.addWidget(self.report)
		self.setLayout(self.gridLayout)

		print(self._overall_list)

	@property
	def overall_list(self):
		return self._overall_list

	@property
	def scores(self):
		return self._scores

	@property
	def reverse_scores(self):
		return self._reverse_scores


class VaultChecker(QtWidgets.QWidget, SharedMethods):
	"""This class pulls from ui_files/settings/export.ui for it's UI elements, and is a widget within the Settings MainWindow."""
	def __init__(self, user_id, password_given):
		super().__init__()
		uic.loadUi("ui_files/settings/vault_checker/vaultchecker.ui", self)
		self._user_id = user_id
		self._key = enc.create_key(password_given)

		self.get_report_data()
		self.decrypt_report_data()

		self.layout = ReportLayout(self._data)
		self.scrollArea.setWidget(self.layout)

		overall = self.calculate_overall()
		self.overallLabel.setText(overall)

		master = self.calculate_strength(password_given)
		self.masterLabel.setText(master)

	def decrypt_report_data(self):
		data = []
		for report in self._data:
			temp = []
			for string in report:
				temp.append(enc.decrypt(self._key, string).decode("utf-8"))
			data.append(temp)
		self._data = data

	def get_report_data(self):
		sql_query = f"SELECT TITLE, URL, PASSWORD FROM '{self._user_id}-passwords'"
		self._data = db.c.execute(sql_query).fetchall()

	def calculate_overall(self):
		overall = int(sum(self.layout.overall_list) / len(self.layout.overall_list))
		return self.layout.reverse_scores[overall]
