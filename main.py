if __name__ == "__main__":	
	import sys
	import sqlite3
	from PyQt5 import QtCore, QtGui, QtWidgets, uic
	from backend import database_connection as db
	import login, register, dialog, vault

	sql_query = """
	CREATE TABLE IF NOT EXISTS 'user-data' (
	USER_ID INTEGER PRIMARY KEY,
	USERNAME  TEXT    (1, 100),
	PASSWORD    TEXT    (1, 100)
	);"""
	db.c.execute(sql_query)
	db.conn.commit()

	app = QtWidgets.QApplication(sys.argv)
	window = login.Login()
	app.exec_()
