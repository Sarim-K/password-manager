# standard libaries
import sqlite3
import random
import os
import json

# external libaries
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog

# local imports
from backend import database_connection as db
from backend import encryption as enc
import dialog


class SharedImportMethods:
	"""This is an abstract class which both import classes inherit, as they both need the method(s) within.
	This should never be instantiated, only inherited."""
	get_old_user_id_length = lambda self, folder_or_password_title: len(str(folder_or_password_title.split("-")[0]))


class InitialImportAccount(SharedImportMethods):
	"""This is a class used to import data from .psm files. This class handles the initial part of importing."""
	def __init__(self):
		_filename = self.get_file_path()
		try:
			_data = self.path_convert_to_dict(_filename)
		except FileNotFoundError:
			return

		_contents, _passwords, _details = self.separate_dict(_data)
		_existing_usernames = self.get_existing_usernames()
		_new_username = self.check_if_username_exists(_existing_usernames, _details[0])

		if _new_username != _details[0]:
			Dialog = dialog.Dialog(f"Your username is taken, your new username is {_new_username}", dialogName="New username.")
			Dialog.exec_()

		_details = self.format_details(_details, _new_username)
		self.create_login_details(_details)
		_user_id = self.get_new_user_id(_new_username)

		_old_user_id_length = self.get_old_user_id_length(list(_contents.keys())[0])

		_passwords = self.encode_passwords(_passwords)
		self.import_passwords(_passwords, _user_id)

		_contents = self.replace_folder_user_ids(_user_id, _old_user_id_length, _contents)
		self.import_folders(_user_id, _contents)

	def get_file_path(self):
		filename = QFileDialog.getOpenFileName(None, 'Open file', os.getcwd(), "*.psm")[0]
		return filename

	def path_convert_to_dict(self, filename):
		with open(filename) as json_file:
			data = json.load(json_file)
		return data

	def separate_dict(self, data):
		contents = data["contents"]
		passwords = data["passwords"]
		details = data["details"]
		return contents, passwords, details

	def get_existing_usernames(self):
		usernames = []
		sql_query = "SELECT USERNAME FROM 'user-data'"
		_usernames = db.c.execute(sql_query).fetchall()

		for username in _usernames:
			usernames.append(username[0])
		return usernames

	def check_if_username_exists(self, usernames, username):
		count = 0
		new_username = username

		while True:
			if username in usernames:
				new_username = str(new_username) + str(count)
				if new_username in usernames:
					count += 1
					new_username = username
				else:
					return new_username
			else:
				return new_username

	def format_details(self, details, new_username):
		# re-orders details for being inserted into database
		details.insert(0, None)
		details[1] = new_username
		details[3] = 1
		details = tuple(details)
		print(details)
		return details

	def create_login_details(self, details):
		sql_query = f"""
		INSERT OR REPLACE INTO 'user-data'
		VALUES(?, ?, ?, ?, ?)
		"""
		db.c.execute(sql_query, details)
		db.conn.commit()

	def get_new_user_id(self, username):
		sql_query = f"SELECT USER_ID FROM 'user-data' WHERE USERNAME = ?"
		user_id = db.c.execute(sql_query, (username,)).fetchone()[0]
		return user_id

	def replace_folder_user_ids(self, user_id, old_user_id_length, contents):
		# old user id in folder names replaced with new user id
		new_contents = {}
		for folder in contents:
			new_contents[(str(user_id)+folder[old_user_id_length:])] = contents[folder]
		return new_contents

	def encode_passwords(self, passwords):
		passwords_dict = {}
		for key in passwords:
			current = []
			for data in passwords[key]:
				try:
					current.append(data.encode())
				except Exception:
					current.append(data)
			passwords_dict[key] = current
		return passwords_dict

	def import_passwords(self, passwords, user_id):
		sql_query = f"""
		CREATE TABLE '{user_id}-passwords' (
		ID INTEGER PRIMARY KEY,
		TITLE		TEXT	(1, 100),
		URL    		TEXT    (1, 100),
		USERNAME    TEXT    (1, 100),
		EMAIL   	TEXT    (1, 100),
		PASSWORD   	TEXT    (1, 100),
		OTHER  		TEXT    (1, 100)
		);"""
		db.c.execute(sql_query)
		db.conn.commit()

		for key in passwords:
			sql_query = f"""
						INSERT OR REPLACE INTO '{user_id}-passwords'
						VALUES(?,?,?,?,?,?,?)
						"""
			db.c.execute(sql_query, (int(key), passwords[key][0], passwords[key][1], passwords[key][2], passwords[key][3], passwords[key][4], passwords[key][5]))
		db.conn.commit()

	def import_folders(self, user_id, contents):
		for folder in contents:
			sql_query = f"""
			CREATE TABLE '{folder}' (
			PASSWORD_ID INTEGER PRIMARY KEY,
			FOREIGN KEY(PASSWORD_ID) REFERENCES '{user_id}-passwords'(ID) ON DELETE CASCADE
			);"""
			db.c.execute(sql_query)
			db.conn.commit()

			for folder_id in contents[folder]:
				sql_query = f"""
				INSERT OR REPLACE INTO '{folder}'
				VALUES(?)
				"""
				db.c.execute(sql_query, (folder_id,))
			db.conn.commit()


class LaterImportAccount(SharedImportMethods):
	"""This is a class also used to import data from .psm files.
	This is instantiated when the imported account is logged into for the first time, from vault.py, exclusively."""
	def __init__(self, _user_id, _key):
		_imported = self.check_if_imported(_user_id)
		print(_imported)
		if _imported:
			_folder_name = self.get_a_folder_name(_user_id)
			_passwords = self.get_passwords(_user_id)
			_old_user_id_length = self.get_old_user_id_length(_folder_name)
			_passwords = self.decrypt_and_replace_titles(_passwords, _key, _user_id, _old_user_id_length)
			_passwords = self.re_encrypt_titles(_passwords, _key)
			self.replace_titles_in_db(_passwords, _user_id)
			self.set_not_imported(_user_id)

	def check_if_imported(self, user_id):
		sql_query = f"SELECT IMPORTED FROM 'user-data' WHERE USER_ID = ?"
		retrieved_data = db.c.execute(sql_query, (user_id,)).fetchone()
		print(retrieved_data)
		try:
			if retrieved_data[0]:
				return True
			else:
				return False
		except TypeError:
			return False

	def get_passwords(self, user_id):
		sql_query = f"SELECT * FROM '{user_id}-passwords'"
		data = db.c.execute(sql_query).fetchall()
		return data

	def get_a_folder_name(self, user_id):	# used for it's contained user_id
		sql_query = f"SELECT name FROM sqlite_master WHERE name LIKE '{user_id}-folder-%' ORDER BY name ASC"
		folder_name = db.c.execute(sql_query).fetchone()[0]
		return folder_name

	replace_title_user_id = lambda self, user_id, old_user_id_length, title: str(user_id)+title[old_user_id_length:]

	def decrypt_and_replace_titles(self, data, key, user_id, old_user_id_length):
		new_data = []
		for entry in data:
			new_entry = list(entry)
			decrypted_title = enc.decrypt(key, entry[1]).decode("utf-8")
			print(decrypted_title)
			decrypted_title = self.replace_title_user_id(user_id, old_user_id_length, decrypted_title)
			print(decrypted_title)
			new_entry[1] = decrypted_title	# entry[1] is the title
			new_data.append(new_entry)
		return new_data

	def re_encrypt_titles(self, data, key):
		new_data = []
		for entry in data:
			new_entry = entry
			encrypted_title = enc.encrypt(key, entry[1])
			new_entry[1] = encrypted_title	# entry[1] is the title
			new_data.append(new_entry)
		return new_data

	def replace_titles_in_db(self, data, user_id):
		for entry in data:
			sql_query = f"UPDATE '{user_id}-passwords' SET TITLE = ? WHERE ID = ?;"
			db.c.execute(sql_query, (entry[1], entry[0]))
		db.conn.commit()

	def set_not_imported(self, user_id):
		# so that we dont need to instantiate this class next time we log in
		sql_query = f"""UPDATE 'user-data'
					SET IMPORTED = 0
					WHERE USER_ID = ?
					;"""
		db.c.execute(sql_query, (user_id,))
		db.conn.commit()
