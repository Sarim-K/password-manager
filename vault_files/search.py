# external libraries
from backend import database_connection as db
from backend import encryption as enc


class Search:
        def __init__(self, search_term, user_id, key):
                final = []
                data = self.get_user_passwords(user_id)
                data = self.decrypt_data(data, key)

                for row in data:
                        score = 0
                        title = row[1]
                        unprefixed_title = self.remove_prefix(title)[0]

                        score += self.exact_match(search_term, unprefixed_title)
                        score += self.same_order(search_term, unprefixed_title)
                        score += self.matching_word(search_term, unprefixed_title)

                        if score >= 5:
                                final.append({score:row})

                self._results = self.sort_and_format(final)


        @property
        def results(self):
                return self._results

        def get_user_passwords(self, user_id):
                sql_query = f"SELECT * FROM '{user_id}-passwords'"
                data = db.c.execute(sql_query).fetchall()
                return data

        def decrypt_data(self, data, key):
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

        def remove_prefix(self, title):
                new_title = ""
                title = title.split("-")[2:]
                for substring in title:
                        new_title += substring + "-"
                new_title = new_title[:-1]
                return title

        def matching_word(self, search_term, title):
                score = 0
                for word in search_term.split(" "):
                        score += title.count(search_term) * 5
                return score

        def same_order(self, search_term, title):
                search_term, title = search_term.replace(" ", ""), title.replace(" ", "")

                start = 0
                for character in search_term:
                        found = False
                        for count in range(start, len(title), 1):
                                start = count
                                temp = title[count]

                                if character == temp:
                                        found = True
                                        break

                        if not found:
                                return 0

                return 5	# 5 score

        def exact_match(self, search_term, unprefixed_title):
                if unprefixed_title == search_term:
                        return 9999
                else:
                        return 0

        def sort_and_format(self, data):
                formatted_data = []
                data = sorted(data, key=lambda d: sorted(d.items()))
                for password in data:
                        formatted_data.append(list(password.values())[0])
                return formatted_data
