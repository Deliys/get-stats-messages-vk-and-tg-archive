from bs4 import BeautifulSoup
import os 
from tqdm import tqdm
import pymorphy2
import json
import threading
import sqlite3
from colorama import Fore, Back, Style


try:
	os.mkdir("data")
except Exception as e:
	pass

filters = ["'",",",".",'[',']','{','}','(',")",
'«','»',"-",";" , "'", '"'
]


clear_lits = [
"Запись",
"Файл",
"Стикер",
"удалено"
]


conn = sqlite3.connect('main.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS  word(
   word TEXT,
   word_normal_form TEXT

);
""")
cur.execute("""CREATE TABLE IF NOT EXISTS word_normal(   
   word TEXT,
   match INT
);
""")
cur.execute('DELETE FROM word;',);
cur.execute('DELETE FROM word_normal;',);

conn.commit()

file_name_list = []
morph = pymorphy2.MorphAnalyzer()



#оздание таблицы подсчета повторений
def create_table():
	cur = conn.cursor()
	print(cur.execute("""INSERT INTO word_normal(word,match) SELECT
		`word_normal_form`,
		COUNT(`word_normal_form`) AS `count`
	FROM
		`word`
	GROUP BY
		`word_normal_form`
	HAVING 
		`count` > 1"""))
	conn.commit() 

#создание обще таблицы слов и их изначальной формы
def create_word_table(data):
	print(Fore.GREEN)
	text = []
	for i in data:
		for ii in i.split():
			text.append(ii)


	cur = conn.cursor()
	for i in tqdm(text , desc= "создание общей таблицы"):
		i= anti_simfol(i)
		cur.execute("INSERT INTO word VALUES(?,?);",(i.lower() ,morph.parse(i)[0].normal_form,) )	
	conn.commit()

	print(Style.RESET_ALL)

def anti_simfol(text):

	for uu in filters:
		text = text.translate({ord(i): None for i in uu})

	return text



#получение всех сообщений из переписок вк

def get_vk_messages_list(data):
	print(Fore.MAGENTA)
	list_dir_mess = []
	for file_dir in os.listdir("data/Archive/messages"):
		if ("index-messages.html" !=file_dir) ==True:
			if int(file_dir) >0:#проверка на бота
				for file_dir_user in os.listdir("data/Archive/messages/"+str(file_dir)):
						file_name = "data/Archive/messages/"+str(file_dir)+"/"+file_dir_user
						list_dir_mess.append(file_name)

	for file_name in tqdm(list_dir_mess , desc= "vk"):
		with open(file_name ,"r") as file:
			f = file.read()
			soup = BeautifulSoup(f, 'lxml') 
			messeges = soup.find_all("div", attrs={ "class" : "item"})

			for i in messeges:
				text = i.find_all("div", attrs={})[3].text
				if ((len(text.split())>0) and (text!= " ")):
					if (text.split()[0] in clear_lits) == False:
						data.append(text)

	print(Style.RESET_ALL)
	return data

#получение всех сообщений из переписок tg
def get_tg_messages_list(data):
	print(Fore.YELLOW)
	list_dir_mess = []
	for file_dir in os.listdir("data/DataExport/chats"):
		
		for file_dir_user in os.listdir("data/DataExport/chats/"+str(file_dir)):
				file_name = "data/DataExport/chats/"+str(file_dir)+"/"+file_dir_user
				list_dir_mess.append(file_name)

	for file_name in tqdm(list_dir_mess , desc= "tg"):
		if str(file_name).split(".")[-1] == "html":
			with open(file_name ,"r",encoding='utf-8') as file:
				f = file.read()
				soup = BeautifulSoup(f, 'lxml') 
				messeges = soup.find_all("div", attrs={ "class" : "text"})

				for i in messeges:
					text = i.text
					if ((len(text.split())>0) and (text!= " ")):
						if (text.split()[0] in clear_lits) == False:
							data.append(text)

	print(Style.RESET_ALL)
	return data




# просто разбивает элементы массива(сообщения целиком) на слова и создает из них текс
def list_to_text(lst):
	text = ""
	for i in lst:
		for ii in i.split():
			text = text + "\n"+ii

	return text

#  просто разбивает элементы массива(сообщения целиком) на слова и переделывает в общую форму
def list_to_normal_form(lst):

	text_end = []
	for i in lst:
		for ii in i.split():
			text_end.append(morph.parse(ii)[0].normal_form)
			#print(ii , morph.parse(ii)[0].normal_form)
			#input()
	
	return text_end









def start():
	data = []
	
	b = 0
	if "Archive" in os.listdir("data"):
		b = b+1
		data = get_vk_messages_list(data) # получение vk 
	if "DataExport" in os.listdir("data"):
		b = b+1
		data = get_tg_messages_list(data) # получение tg

	if b == 0:
		print("переместите вк/тг архив ")
		print("убедитесь что название папок залано правильно")
		print("*DataExport - для тг")
		print("*Archive - для vk")

	else:
		create_word_table(data)
		create_table()


start()
input("готово")

