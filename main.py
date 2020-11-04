if __name__ == "__main__":
	# standard libaries
	import sys
	import sqlite3

	# external libaries
	from PyQt5 import QtCore, QtGui, QtWidgets, uic

	# local imports
	from backend import database_connection as db
	import home


	sql_query = """
	CREATE TABLE IF NOT EXISTS 'user-data' (
	USER_ID 	INTEGER 		PRIMARY KEY,
	USERNAME  	TEXT	(1, 100)	NOT NULL,
	PASSWORD  	TEXT    (1, 100)	NOT NULL,
	IMPORTED	INTEGER (1, 1),
	EMAIL		TEXT 	(1, 100),
	SEC_QUES_1	INT	(1, 10),
	SEC_QUES_2	INT	(1, 10),
	SEC_QUES_3	INT	(1, 10),
        SEC_ANS_1	TEXT	(1, 100),
        SEC_ANS_2	TEXT	(1, 100),
        SEC_ANS_3	TEXT	(1, 100)
	);"""
	db.c.execute(sql_query)
	db.conn.commit()

	app = QtWidgets.QApplication(sys.argv)
	window = home.Home()
	app.exec_()
