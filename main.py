import telebot
from telebot import types
from telebot import custom_filters
import dbhelper as db
import textdoc as tc
import schedule
from threading import Thread
from time import sleep

######## MAIN: 5145905234:AAGPmHnQcp-P64B8sWOMYkQGSVoqVgRKP7U
######## TESTING: 5040853954:AAEclR2ai7cGDMtCl5rWab3BsbVQLkBNocE

bot = telebot.TeleBot("5145905234:AAGPmHnQcp-P64B8sWOMYkQGSVoqVgRKP7U")

# ОСНВОНОЕ МЕНЮ | КОМАНДЫ: START, HELP, MENU
@bot.message_handler(commands=['start','help','menu'])
def welcome_menu(message):

	# ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ В БД
	USER_ID = message.from_user.id
	USER_NAME = message.from_user.username
	db.register_user(USER_ID,USER_NAME)

	# ОСНВОНОЕ МЕНЮ
	Main_Menu = types.InlineKeyboardMarkup(row_width=2)
	Item_1 = types.InlineKeyboardButton ('✍️ Write valentine', callback_data='Write')
	Item_2 = types.InlineKeyboardButton ('🗂 All valentines', callback_data='All')
	Item_3 = types.InlineKeyboardButton ('📤 Send all valentines', callback_data='Send')
	Item_4 = types.InlineKeyboardButton ('🧐 Information', callback_data='Information')
	Main_Menu.add (Item_1, Item_2, Item_3, Item_4)

	# ОТПРАВКА МЕНЮ | TEXT | PHOTO | MARKUP
	bot.send_photo(message.chat.id,photo=tc.main_menu_photo,caption=tc.main_menu_txt,reply_markup=Main_Menu,)

		#|||||||||||||||||||||||||||||||||||||||#
		#_______________________________________#
		#_______________________________________#
		# ////// ОБРАБОТКА БАЗ ЗАПРОСОВ  \\\\\\ #

# ОБРАБОТКА ЗАПРОСА "MENU"
@bot.callback_query_handler(lambda query: query.data in ['menu'])
def get_back_to_main_menu(call):
	if call.data == 'menu':
		welcome_menu(call.message)
	else:
		pass

# ОБРАБОТКА ЗАПРОСА "WRITE"
@bot.callback_query_handler(lambda query: query.data in ['Write'])
def welcome_writing(call):
	bot.send_message(call.message.chat.id,text=tc.write_menu_open)
	bot.register_next_step_handler(call.message,get_name)

# ОБРАБОТКА ЗАПРОСА "SEND"
@bot.callback_query_handler(lambda query: query.data in ['Send'])
def send_all_messages(call):
	USER_ID = call.from_user.id
	bot.send_message(call.message.chat.id,text=tc.send_menu_txt)
	bot.register_next_step_handler(call.message,send_messages,USER_ID)

# ОБРАБОТКА ЗАПРОСА "INFORMATION" !!!!!
@bot.callback_query_handler(lambda query: query.data in ['Information'])
def send_all_messages(call):
	Infroamtion_menu = types.InlineKeyboardMarkup (row_width=1)
	Back = types.InlineKeyboardButton (text='◀️ Back', callback_data="menu")
	More = types.InlineKeyboardButton (text='🌐 More', url=tc.more_infromation_link)
	Infroamtion_menu.add (Back,More)
	bot.send_message(call.message.chat.id,text=tc.information_menu,reply_markup=Infroamtion_menu)

		# |||||||||||||||||||||||||||||||||||||||#
		# _______________________________________#
		# _______________________________________#
		# ////// ОБРАБОТКА ЗАПРОСОВ НАПИС \\\\\\ #


# ОБРАБОТКА ЗАПРОСА "WRITE"
# ПОЛУЧЕНИЕ ИМЕНИ И ПРОВЕРКА ЕГО ПО БД и ЗАПРОС ТЕКСТА
@bot.message_handler(func=lambda call:False)
def get_name (message):

	# ПОЛУЧЕНИЕ ДАННЫХ ОТПАРВИТЕЛЯ
	USER_ID_SENDER = message.from_user.id
	USER_NAME_SENDER = message.from_user.username

	# ПОЛУЧЕНИЕ ИМЕНИ ПОЛУЧАТЕЛЯ
	user_name_reciever = message.text
	user_name_reciever = user_name_reciever.split ('@', 1)
	try:
		USER_NAME_RECIEVER = user_name_reciever [1]

		# ПОЛУЧЕНИЕ ID / ПРОВЕРКА НА НАЛИЧИЕ В БД
		user_id_reciever = db.get_user_id (USER_NAME_RECIEVER)
		if user_id_reciever == 0:
			USER_ID_RECIEVER = 0
			bot.send_message (message.chat.id,text=tc.write_reciever_n_found)
		else:
			USER_ID_RECIEVER = user_id_reciever
			bot.send_message (message.chat.id,text=tc.write_reciever_found)

		bot.send_message (message.from_user.id, text=tc.write_message_txt)
		bot.register_next_step_handler (message, get_valentine, USER_ID_SENDER, USER_NAME_SENDER, USER_NAME_RECIEVER,USER_ID_RECIEVER)

	except IndexError:
		bot.send_message(message.chat.id,text=tc.write_error_reciever)
		welcome_menu(message)

# ПОЛУЧЕНИЕ ТЕКСТА и ЗАПРОС СТАТУСА
def get_valentine (message,USER_ID_SENDER,USER_NAME_SENDER, USER_NAME_RECIEVER,USER_ID_RECIEVER):
	# ПОЛУЧЕНИЕ ПИСЬМА
	USER_MESSAGE = message.text
	# ПОЛУЧЕНИЕ КОЛИЧЕСТВА ПИСЕМ, ДЛЯ СОЗДАНИЯ УНИКАЛЬНОГО ПОРЯДКОВОГО НОМЕРА
	MESSAGE_NUMBER = db.get_number_of_messages () + 1
	bot.send_message (message.chat.id,text=tc.write_sender_status_txt)

	bot.register_next_step_handler (message, get_show_status, USER_ID_SENDER, USER_NAME_SENDER, USER_NAME_RECIEVER,USER_ID_RECIEVER,USER_MESSAGE,MESSAGE_NUMBER)

# ПОЛУЧЕНИЕ СТАТУСА и ЗАПРОС
def get_show_status (message,USER_ID_SENDER, USER_NAME_SENDER, USER_NAME_RECIEVER,USER_ID_RECIEVER,USER_MESSAGE,MESSAGE_NUMBER):
	# ПОЛУЧЕНИЕ СТАТУСА ОТПРАВИТЕЛЯ
	try:
		SENDER_SHOW_STATUS = int(message.text)
		if SENDER_SHOW_STATUS == 1 or SENDER_SHOW_STATUS == 0:

			# СОЗДАНИЕ НОВОГО ПИСЬМА В БД
			db.register_message (MESSAGE_NUMBER, USER_ID_SENDER, USER_NAME_SENDER, USER_MESSAGE, USER_ID_RECIEVER,
								 USER_NAME_RECIEVER, SENDER_SHOW_STATUS)
			bot.send_message (message.chat.id,text=tc.write_menu_end)
			welcome_menu (message)

		else:
			bot.send_message (message.chat.id, text=tc.write_error_sender_status_digit)
			bot.send_message (message.chat.id, text="Your's valentine:\n\n" + USER_MESSAGE)
			welcome_menu (message)

	except ValueError:
		bot.send_message (message.chat.id,text=tc.write_error_sender_status_letter)
		bot.send_message (message.chat.id,text="Your's valentine:\n\n"+USER_MESSAGE)
		welcome_menu (message)

	# |||||||||||||||||||||||||||||||||||||||#
	# _______________________________________#
	# _______________________________________#
	# ////// ADMIN ADMIN ADMIN ADMIN  \\\\\\ #

@bot.message_handler (chat_id=[5164010500], commands=['send'])
def admin_message (message):
	bot.send_message (message.chat.id,
					  "#222 Направь сообщение, оно будет отправлено всем, зарегестрированным в боте")
	bot.register_next_step_handler (message, admin_write_1)

def admin_write_1 (message):
	MESSAGE = message.text
	bot.send_message (message.chat.id, text='Your message:\n' + MESSAGE + '\nSend? (yes/no)')
	bot.register_next_step_handler (message, admin_write_2, MESSAGE)

def admin_write_2 (message, MESSAGE):
	user_response = message.text.lower ()
	RESTRICT = [5145905234, 5040853954]

	if user_response == 'yes':
		all_users = db.get_all_users ()
		for _ in range (len (all_users)):
			USER_ID = all_users [_] [0]
			if USER_ID in RESTRICT:
				print ('Skipping sending to BOT')
				pass
			else:
				bot.send_message (chat_id=USER_ID,
								  text='⚠️Message from admin⚠️\n\n' + MESSAGE + '\n\nFor help write to @mibvalentines')

		bot.send_message (message.chat.id, 'Выполнено')
	elif user_response == 'no':
		bot.send_message (message.chat.id, 'Отменено )))')
	welcome_menu (message)

		# |||||||||||||||||||||||||||||||||||||||#
		# _______________________________________#
		# _______________________________________#
		# ////// ОБРАБОТКА ЗАПРОСОВ РЕД   \\\\\\ #

# ОБРАБОТКА ЗАПРОСА "ALL"
@bot.callback_query_handler(lambda query: query.data in ['All'])
def all_valentines(call):
#	print(call.from_user.id)
	Valentines_menu = types.InlineKeyboardMarkup (row_width=2)
	# ПОЛУЧАЕМ ВСЕ ВАЛЕНТИНКИ ЧЕЛОВЕКА
	all_valentines_from_user = db.get_message(call.from_user.id)
	for _ in range (len(all_valentines_from_user)):
		reciver_name = all_valentines_from_user[_][5]
		_ = types.InlineKeyboardButton (text=reciver_name,callback_data="valentine!" + reciver_name)
		Valentines_menu.add(_)
	Back = types.InlineKeyboardButton (text='◀️ Back',callback_data="menu")
	Valentines_menu.add (Back)
	# ВЫВОД ВСЕХ ВАЛЕНТИНОК
	bot.send_message(call.message.chat.id,text=tc.edit_menu_list,reply_markup=Valentines_menu)

# ОБРАБОТКА ЗАПРОСА "ALL" ДЛЯ ОДНОГО СООБЩЕНИЯ
@bot.callback_query_handler (func=lambda call: True)
def check(call):
	if call.data.startswith("valentine!"):
		USER_ID = call.from_user.id
		MESSAGE_RECIVER = call.data
		MESSAGE_RECIVER = MESSAGE_RECIVER.split ('!')[1]

		# ВЫВОД ПРЕВЬЮ СООБЩЕНИЯ
		all_valentines_from_user = db.get_message (call.from_user.id)
		for _ in range (len (all_valentines_from_user)):
			if all_valentines_from_user[_][5] == MESSAGE_RECIVER:
				MESSAGE_NUMBER = all_valentines_from_user [_] [0]
				MESSEGE = all_valentines_from_user [_] [3]
				MESSAGE_RECIVER = all_valentines_from_user[_][5]
				SHOW_SENDER_STATUS = all_valentines_from_user[_][6]
				break
			else:
				pass

		# ДЕЙСТВИЕ ПО УДАЛЕНИЮ/РЕДАКТИРОВАНИЮ СООБЩЕНИЯ
		Message_Menu = types.InlineKeyboardMarkup (row_width=2)
		Item_1= types.InlineKeyboardButton (text='❌ Delete',callback_data="delete!"+ str(MESSAGE_NUMBER))
		Item_2 = types.InlineKeyboardButton (text='✍️ Edit text',callback_data="edit!"+ str(MESSAGE_NUMBER))
		Item_3 = types.InlineKeyboardButton (text='◀️ Back', callback_data="All")
		Message_Menu.add(Item_1,Item_2,Item_3)

		if SHOW_SENDER_STATUS == 0:
			bot.send_message (call.message.chat.id, text='Not anonymous\nValentine to: ' + '@' + MESSAGE_RECIVER + '\n' + MESSEGE,reply_markup=Message_Menu)

		elif SHOW_SENDER_STATUS == 1:
			bot.send_message (call.message.chat.id, text='Anonymous\nValentine to: ' + '@' + MESSAGE_RECIVER + '\n' + MESSEGE, reply_markup=Message_Menu)


#		bot.send_message(call.message.chat.id, text='Valentine to: '+'@'+MESSAGE_RECIVER+'\n'+MESSEGE,reply_markup=Message_Menu)
#		print(call.message.message_id)

	# РЕДАКТИРОВАНИЕ СООБЩЕНИЯ
	if call.data.startswith ("edit!"):
		MESSAGE_NUMBER = call.data
		MESSAGE_NUMBER = int (MESSAGE_NUMBER.split ('!') [1])

		bot.send_message (call.message.chat.id, text=tc.edit_menu_text)
		bot.register_next_step_handler(call.message,change_text,MESSAGE_NUMBER)

	# УДАЛЕНИЕ СООБЩЕНИЯ
	if call.data.startswith ("delete!"):
		MESSAGE_NUMBER = call.data
		MESSAGE_NUMBER = int(MESSAGE_NUMBER.split ('!') [1])

		# ПРОВЕРКА УДАЛЕНИЯ ПИСЬМА
		bot.send_message(call.message.chat.id,text=tc.edit_menu_delete_check)
		bot.register_next_step_handler(call.message,final_delete_message,MESSAGE_NUMBER)

# ОБРАБОТКА ЗАПРОСА ПО ЗАМЕНЕ ТЕКСТА
@bot.message_handler(func=lambda call:False)
def change_text (message,MESSAGE_NUMBER):
	user_message = message.text
	db.change_text(MESSAGE_NUMBER,user_message)

	all_valentines_from_user = db.get_message (message.from_user.id)
	for _ in range (len (all_valentines_from_user)):
		if all_valentines_from_user [_] [0] == MESSAGE_NUMBER:
			MESSAGE_NUMBER = all_valentines_from_user [_] [0]
			MESSEGE = all_valentines_from_user [_] [3]
			MESSAGE_RECIVER = all_valentines_from_user [_] [5]
			# "SHOW SENDER STATUS ?????????????????????????????????"
			break
		else:
			pass

	# ДЕЙСТВИЕ ПО УДАЛЕНИЮ/РЕДАКТИРОВАНИЮ СООБЩЕНИЯ
	Message_Menu = types.InlineKeyboardMarkup (row_width=2)
	Item_1 = types.InlineKeyboardButton (text='❌ Delete', callback_data="delete!" + str (MESSAGE_NUMBER))
	Item_2 = types.InlineKeyboardButton (text='✍️ Edit text', callback_data="edit!" + str (MESSAGE_NUMBER))
	Item_3 = types.InlineKeyboardButton (text='◀️ Back', callback_data="All")
	Message_Menu.add (Item_1, Item_2, Item_3)

	bot.send_message (message.chat.id, text='Valentine to: ' + '@' + MESSAGE_RECIVER + '\n' + MESSEGE,reply_markup=Message_Menu)

# ПОДТВРЕЖДЕНИЕ УДАЛЕНИЯ ПИСЬМА
def final_delete_message (message,MESSAGE_NUMBER):
	user_response = message.text.lower()
	if user_response == "yes":
		# ОБРАЩЕНИЕ К БД для удаления
		db.delete_message(MESSAGE_NUMBER)
		# УДАЛЕНИЕ СООБЩЕНИЯ ПРОШЛОГО
		bot.delete_message(message.chat.id, message.message_id)
		bot.delete_message (message.chat.id, message.message_id - 1)
		bot.delete_message (message.chat.id, message.message_id-2)

		bot.send_message(message.chat.id,text=tc.edit_menu_delete_suc )
		welcome_menu(message)
	elif user_response == "no":
		bot.send_message (message.chat.id,text=tc.edit_menu_delete_can)
		welcome_menu (message)
	else:
		bot.send_message (message.chat.id,text=tc.edit_menu_delete_er)
		welcome_menu (message)

		# |||||||||||||||||||||||||||||||||||||||#
		# _______________________________________#
		# _______________________________________#
		# ////// ОБРАБОТКА ЗАПРОСОВ ОТП   \\\\\\ #

# ОБРАБОТКА ЗАПРОСА ПО ОТПРАВКЕ ПИСЬМА
@bot.message_handler(func=lambda call:False)
def send_messages (message,USER_ID):
	user_response = message.text.lower ()
	if user_response == "yes":
		# ОБРАЩЕНИЕ К БД ДЛЯ ВЫГРУЗКИ ВСЕХ ПИСЕМ
		all_valentines_from_user = db.get_message (USER_ID)
		for _ in range (len (all_valentines_from_user)):
			MESSAGE_NUMBER = all_valentines_from_user[_][0]
			MESSAGE_SENDER = all_valentines_from_user[_][2]
			MESSAGE = all_valentines_from_user[_][3]
			MESSAGE_RECIVER_ID = all_valentines_from_user[_][4]
			MESSAGE_RECIVER_NAME = all_valentines_from_user[_][5]
			SHOW_SENDER_STATUS = all_valentines_from_user[_][6]

			if MESSAGE_RECIVER_ID !=0:
				if SHOW_SENDER_STATUS == 0:
					bot.send_message(chat_id=MESSAGE_RECIVER_ID,text='💌 You have new Valentine: \n' + MESSAGE)
				elif SHOW_SENDER_STATUS != 0:
					SENDER_NAME = '@'+MESSAGE_SENDER
					SENDING_MESSAGE = f'From: {SENDER_NAME}\n' + MESSAGE
					bot.send_message(chat_id=MESSAGE_RECIVER_ID,text='💌 You have new Valentine: \n' + SENDING_MESSAGE)

				# УДАЛЕНИЕ ЭТОГО ПИСЬМА ИЗ БД (ОБНУЛЕНИЕ ПОКАЗАТЕЛЕЙ)
				db.delete_message (MESSAGE_NUMBER)

			elif MESSAGE_RECIVER_ID == 0:
#####			bot.send_message(message.chat.id,text=f'User @{MESSAGE_RECIVER_NAME} hasnot login in a bot, therefore message to this person will not be sent ')
				bot.send_message(message.chat.id,text=f'User: @{MESSAGE_RECIVER_NAME} '+tc.send_menu_er)

				pass

		bot.send_message (message.chat.id,text=tc.send_menu_suc)
		welcome_menu (message)

	elif user_response == "no":
		bot.send_message (message.chat.id,text=tc.send_menu_can)
		welcome_menu (message)
	else:
		bot.send_message (message.chat.id,text=tc.send_menu_answer_er)
		welcome_menu (message)


		# |||||||||||||||||||||||||||||||||||||||#
		# _______________________________________#
		# _______________________________________#
		# ////// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ  \\\\\\ #



### ФУНКЦИЯ ДЛЯ ПОВТОРЯЮЩИХСЯ ДЕЙСТВИЙ
def schedule_checker():
	while True:
		schedule.run_pending()
		sleep(1)

# ФУНКЦИЯ ОБНОВЛЕНИЯ БАЗЫ ДАННЫХ
def funtion_to_run():
	messages_no_reciever = db.get_message_no_user_reciever_id ()
	for _ in range (len (messages_no_reciever)):
		MESSAGE_NUMBER = messages_no_reciever [_] [0]
		MESSAGE_SENDER_ID = messages_no_reciever [_] [1]
		MESSAGE_RECIVER_ID = messages_no_reciever [_] [4]
		MESSAGE_RECIVER_NAME = messages_no_reciever [_] [5]

		USER_ID_RECIVER_FROM_USERS_DB = db.get_user_id(MESSAGE_RECIVER_NAME)
		if USER_ID_RECIVER_FROM_USERS_DB == 0:
#			print('NO UPDATE')
			pass
		else:
			MESSAGE_RECIVER_ID = USER_ID_RECIVER_FROM_USERS_DB
			db.insert_message_user_id(MESSAGE_NUMBER,MESSAGE_RECIVER_ID)
			bot.send_message(chat_id=MESSAGE_SENDER_ID,text=f'User @{MESSAGE_RECIVER_NAME} '+tc.db_user_update_suc)

#			print ('UPDATE')


#### ADMIN PART
bot.add_custom_filter(custom_filters.ChatFilter ())


		# |||||||||||||||||||||||||||||||||||||||#
		# _______________________________________#
		# _______________________________________#
		# ////// START START START START  \\\\\\ #

if __name__ == "__main__":
	# СОЗДАНИЕ БД
	db.create_users_tables ()
	db.create_messages_tables ()

	# SCHEDULE ОБНОВЛЕНИЕ БД
	schedule.every(1).minutes.do(funtion_to_run)
	Thread(target=schedule_checker).start()

	##### Чек регистр телегии по нику !!!!!!!!

	# ЗАПУСК БОТА
#	bot.infinity_polling ()
	bot.polling(none_stop=True)

