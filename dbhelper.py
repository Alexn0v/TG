import sqlite3
from sqlite3 import Error

# ФУНКЦИЯ ЗАПИСИ ДАННЫХ В БД
def post_sql_query (sql_query):
	with sqlite3.connect ('user_data.db') as connection:
		cursor = connection.cursor ()
		try:
			cursor.execute (sql_query)
		except Error:
			pass
		result = cursor.fetchall ()
		return result

# ФУНКЦИЯ СОЗДАНИЯ ТАБЛИЦЫ С ИМЕНАМИ И ID ПОЛЬЗОВАТЕЛЕЙ
def create_users_tables():
	users_query = '''CREATE TABLE IF NOT EXISTS USERS (
	user_id INTEGER PRIMARY KEY NOT NULL, 
	user_name TEXT);
	'''
	post_sql_query (users_query)

# ФУНКЦИЯ СОЗДАНИЯ ТАБЛИЦЫ С ПИСЬМАМИ ПОЛЬЗОВАТЕЛЕЙ
def create_messages_tables():
	users_query = '''CREATE TABLE IF NOT EXISTS MESSAGES (
	message_number INTEGER PRIMARY KEY NOT NULL,
	user_id_sender INTEGER,
	user_name_sender TEXT,
	user_message TEXT,
	user_id_reciever INTEGER,
	user_name_reciever TEXT,
	user_sender_show INTEGER);
	'''
	post_sql_query (users_query)

# ФУНКЦИЯ ЗАПИСИ НОВОГО ПОЛЬЗОВАТЕЛЯ
def register_user (user_id,user_name):
	user_check_query = f'SELECT * FROM USERS WHERE user_id = {user_id};'
	user_check_data = post_sql_query (user_check_query)
	if not user_check_data:
			insert_to_db_query = f'INSERT INTO USERS (user_id, user_name) VALUES ({user_id},"{user_name}");'
			post_sql_query (insert_to_db_query)

# ФУНКЦИЯ ПОИСКА ПОЛЬЗОВАТЕЛЯ В БД
def get_user_id (user_name):
	with sqlite3.connect ('user_data.db') as connection:
		cursor = connection.cursor ()
		user_find_id = cursor.execute("SELECT * FROM USERS WHERE user_name=?", (user_name,))
		rows = cursor.fetchone ()
		# Если пользовать еще не запуск бота - НЕ УСПЕШНО
		if rows is None:
			user_id = 0
			return user_id
		# Если пользовать запускал бота - УСПЕШНО
		else:
			user_id = rows [0]
			return user_id

# ФУНКЦИЯ ЗАПИСИ НОВОГО ПИСЬМА
def register_message (message_number,user_id_sender,user_name_sender,user_message,user_id_reciever,user_name_reciever,user_sender_show):
	insert_to_db_query = f'INSERT INTO MESSAGES (message_number,user_id_sender,user_name_sender,user_message,user_id_reciever,user_name_reciever,user_sender_show) ' \
						 f'VALUES ({message_number},{user_id_sender},"{user_name_sender}","{user_message}",{user_id_reciever},"{user_name_reciever}",{user_sender_show});'
	post_sql_query (insert_to_db_query)

# ФУНКЦИЯ ЗАПИСИ КОЛИЧЕСТВА СУЩЕСТВУЮЩИХ ПИСЕМ
def get_number_of_messages ():
	with sqlite3.connect ('user_data.db') as connection:
		cursor = connection.cursor ()
	cursor.execute ("SELECT * FROM MESSAGES")
	result = cursor.fetchall ()
	print (len (result))
	return len (result)

# ФУНКЦИЯ ПОИСКА ПИСЕМ ОТ ОДНОГО ОТПРАВИТЕЛЯ
def get_message(user_id):
	with sqlite3.connect ('user_data.db') as connection:
		cursor = connection.cursor()
		cursor.execute("SELECT * FROM MESSAGES WHERE user_id_sender=?", (user_id,))
		rows = cursor.fetchall()
	return rows

# ФУНКЦИЯ УДАЛЕНИЕ ОДНОГО ПИСЬМА | КОСТЫЛЬ, ЗАМЕНЯЕТ ВСЕ ЗАНЧЕНИЯ НА СТАНДАРТНЫЕ
def delete_message(message_number):
	with sqlite3.connect('user_data.db') as connection:
		cursor = connection.cursor()
		cursor.execute(f"UPDATE MESSAGES SET user_id_sender = 0, user_name_sender = 'NO', user_message = 'NO', user_id_reciever = 0, user_name_reciever = 'NO', user_sender_show = 0 WHERE message_number = {message_number}")
		print('FIELDS UPDATED')

#		cursor.execute("DELETE FROM MESSAGES WHERE message_number=?", (new_message_number,))

# ФУНКЦИЯ ЗАМЕНЫ ТЕКСТА ПОЗДАРВЛЕНИЯ
def change_text(message_number,user_message):
	with sqlite3.connect('user_data.db') as connection:
		cursor = connection.cursor()
		cursor.execute(f"UPDATE MESSAGES SET user_message = ? WHERE message_number = ?", (user_message, message_number,))
		print('Text Changed')

# ФУНКЦИЯ ОБНОВЛЕНИЯ БАЗЫ ПИСЕМ
def get_message_no_user_reciever_id ():
	with sqlite3.connect ('user_data.db') as connection:
		cursor = connection.cursor ()
		user_id = 0
		cursor.execute("SELECT * FROM MESSAGES WHERE user_id_reciever=?", (user_id,))
		rows = cursor.fetchall()
	return rows

# ОБНОВЛЕНИЕ ПОЛЕЙ ID ПОЛУЧАТЕЛЯ
def insert_message_user_id (message_number,user_id):
	with sqlite3.connect ('user_data.db') as connection:
		cursor = connection.cursor ()
		cursor.execute (f"UPDATE MESSAGES SET user_id_reciever = ? WHERE message_number = ?", (user_id, message_number,))

# ФУНКЦИЯ ВЫГРУЗКИ ВСЕХ ЗАРЕГЕСТРИРВОАННЫХ В БОТЕ
def get_all_users():
	with sqlite3.connect ('user_data.db') as connection:
		cursor = connection.cursor ()
		cursor.execute("SELECT * FROM USERS")
		rows = cursor.fetchall()
	return rows

