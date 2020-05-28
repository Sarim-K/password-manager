if __name__ == "__main__":	
	import sys
	import sqlite3
	from PyQt5 import QtCore, QtGui, QtWidgets, uic
	from PyQt5.QtCore import pyqtSlot
	import login, register, dialog

	conn = sqlite3.connect("password-manager.db")
	c = conn.cursor()

	sql_query = f"""
	CREATE TABLE IF NOT EXISTS user_data (
	USER_ID INTEGER PRIMARY KEY,
	USERNAME  TEXT    (5, 30),
	PASSWORD    TEXT    (5, 30)
	);"""
	c.execute(sql_query)
	conn.commit()

	app = QtWidgets.QApplication(sys.argv)
	window = login.Login()
	app.exec_()
