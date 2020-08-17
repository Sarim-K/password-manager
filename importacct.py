from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog
from backend import database_connection as db
from backend import encryption as enc
import dialog
import os, json

def import_acct():
	filename = get_file_path()
	try:
		data = path_convert_to_dict(filename)
	except FileNotFoundError:
		return

	contents, passwords, details = separate_dict(data)
	existing_usernames = get_existing_usernames()
	new_username = check_if_username_exists(existing_usernames, details[0])

	if new_username != details[0]:
		Dialog = dialog.Dialog(f"Your username is taken, your new username is {new_username}", dialogName="New username.")
		Dialog.exec_()

	create_login_details(new_username, details[1])
	user_id = get_new_user_id(new_username)

	for key in contents:
		old_user_id_length = get_old_user_id_length(key)
		break

	contents = replace_folder_user_ids(user_id, old_user_id_length, contents)
	import_folders(contents)

	# passwords = replace_password_user_ids(user_id, passwords)
	passwords = encode_passwords(passwords)
	import_passwords(passwords, user_id)

def get_file_path():
	filename = QFileDialog.getOpenFileName(None, 'Open file', os.getcwd(), "*.psm")[0]
	return filename

def path_convert_to_dict(filename):
	with open(filename) as json_file:
		data = json.load(json_file)
	return data

def separate_dict(data):
	contents = data["contents"]
	passwords = data["passwords"]
	details = data["details"]
	return contents, passwords, details

def get_existing_usernames():
	usernames = []
	sql_query = "SELECT USERNAME FROM 'user-data'"
	_usernames = db.c.execute(sql_query).fetchall()

	for username in _usernames:
		usernames.append(username[0])
	return usernames

def check_if_username_exists(usernames, username):
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

def create_login_details(username, password):
	sql_query = f"""
	INSERT OR REPLACE INTO 'user-data'
	VALUES(?, ?, ?, ?)
	"""
	db.c.execute(sql_query, (None, username, password, 1))
	db.conn.commit()

def get_old_user_id_length(folder_or_password_title):
	return len(str(folder_or_password_title.split("-")[0]))

def get_new_user_id(username):
	sql_query = f"SELECT USER_ID FROM 'user-data' WHERE USERNAME = ?"
	user_id = db.c.execute(sql_query, (username,)).fetchone()[0]
	return user_id

def replace_folder_user_ids(user_id, old_user_id_length, contents):
	new_contents = {}
	for folder in contents:
		new_contents[(str(user_id)+folder[old_user_id_length:])] = contents[folder]
	return new_contents

def import_folders(contents):
	for folder in contents:
		sql_query = f"""
		CREATE TABLE '{folder}' (
		PASSWORD_ID INTEGER PRIMARY KEY
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

def encode_passwords(passwords):
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

def import_passwords(passwords, user_id):
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

# below are executed through vault.py exclusively
def check_if_imported(user_id):
	sql_query = f"SELECT IMPORTED FROM 'user-data' WHERE USER_ID = ?"
	retrieved_data = db.c.execute(sql_query, (user_id,)).fetchone()[0]
	if retrieved_data:
		return True
	else:
		return False

def get_passwords(user_id):
	sql_query = f"SELECT * FROM '{user_id}-passwords'"
	data = db.c.execute(sql_query).fetchall()
	return data

def get_a_folder_name(user_id):	# used for it's contained user_id
	sql_query = f"SELECT name FROM sqlite_master WHERE name LIKE '{user_id}-folder-%' ORDER BY name ASC"
	folder_name = db.c.execute(sql_query).fetchone()[0]
	return folder_name

def replace_title_user_id(user_id, old_user_id_length, title):
	# print(str(user_id)+title[old_user_id_length:])
	return str(user_id)+title[old_user_id_length:]

def decrypt_and_replace_titles(data, key, user_id, old_user_id_length):
	new_data = []
	for entry in data:
		new_entry = list(entry)
		decrypted_title = enc.decrypt(key, entry[1]).decode("utf-8")
		decrypted_title = replace_title_user_id(user_id, old_user_id_length, decrypted_title)
		new_entry[1] = decrypted_title	# entry[1] is the title
		new_data.append(new_entry)
	return new_data

def re_encrypt_titles(data, key):
	new_data = []
	for entry in data:
		new_entry = entry
		encrypted_title = enc.encrypt(key, entry[1])
		new_entry[1] = encrypted_title	# entry[1] is the title
		new_data.append(new_entry)
	return new_data

def replace_titles_in_db(data, user_id):
	for entry in data:
		sql_query = f"UPDATE '{user_id}-passwords' SET TITLE = ? WHERE ID = ?;"
		db.c.execute(sql_query, (entry[1], entry[0]))
	db.conn.commit()

def set_not_imported(user_id):
	sql_query = f"""UPDATE 'user-data'
				SET IMPORTED = 0
				WHERE USER_ID = ?
				;"""
	db.c.execute(sql_query, (user_id,))
	db.conn.commit()
