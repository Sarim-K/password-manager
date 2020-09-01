# external libraries
from backend import database_connection as db
from backend import encryption as enc

def get_user_passwords(user_id):
	sql_query = f"SELECT * FROM '{user_id}-passwords'"
	data = db.c.execute(sql_query).fetchall()
	return data

def decrypt_data(data, key):
	decrypted_data = []
	for row in data:
		new_row = []
		for cell in row:
			try:
				decrypted_cell = enc.decrypt(key, cell).decode("utf-8")
				new_row.append(decrypted_cell)
			except TypeError:	# will be thrown for the id, as id isn't encrypted
				new_row.append(cell)
		decrypted_data.append(new_row)
	return decrypted_data

def remove_prefix(title):
	new_title = ""
	title = title.split("-")[2:]
	for substring in title:
		new_title += substring + "-"
	new_title = new_title[:-1]
	return title

def matching_word(search_term, title):
	score = 0
	for word in search_term.split(" "):
		score += title.count(search_term) * 5

def same_order(search_term, title):
	passed = False
	count = 0
	search_term = list(search_term)
	for character in title:
		if character == search_term[count]:
			count += 1
			passed = True
		else:
			return passed
		return passed


def search(search_term, user_id, key):
	final = []
	data = get_user_passwords(user_id)
	data = decrypt_data(data, key)

	for row in data:
		score = 0
		title = row[1]
		unprefixed_title = remove_prefix(title)

		# print(row, unprefixed_title)
		if unprefixed_title == search_term:
			final.append({"exact":title})
			continue



		matching_word(search_term, unprefixed_title)
