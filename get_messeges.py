from bs4 import BeautifulSoup
import os 
from tqdm import tqdm
import pymorphy2
import json
import threading
import sqlite3
#193183153



filters = ["'",",",".",'[',']','{','}','(',")",
'«','»',"-",";"
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



def split_mass(lst , n):
	a = []
	for i in range(0,n):
		a.append([])

	b = 0
	for i in lst:
		a[b].append(i)
		b =b +1
		if b >n-1:
			b = 0
	return a



def anti_simfol(text):

	for uu in filters:
		text = text.translate({ord(i): None for i in uu})

	return text



#получение всех сообщений из переписок вк

def get_vk_messages_list():
	data = []
	list_dir_mess = []
	for file_dir in os.listdir("Archive/messages"):
		if ("index-messages.html" !=file_dir) ==True:
			if int(file_dir) >0:#проверка на бота
				for file_dir_user in os.listdir("Archive/messages/"+str(file_dir)):
						file_name = "Archive/messages/"+str(file_dir)+"/"+file_dir_user
						list_dir_mess.append(file_name)

	for file_name in tqdm(list_dir_mess):
		with open(file_name ,"r") as file:
			f = file.read()
			soup = BeautifulSoup(f, 'lxml') 
			messeges = soup.find_all("div", attrs={ "class" : "item"})

			for i in messeges:
				text = i.find_all("div", attrs={})[3].text
				if ((len(text.split())>0) and (text!= " ")):
					if (text.split()[0] in clear_lits) == False:
						data.append(text)


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




tesst = get_vk_messages_list()

text = []

for i in tesst:
	for ii in i.split():
		text.append(ii)


cur = conn.cursor()
for i in tqdm(text):
	i= anti_simfol(i)
	cur.execute("INSERT INTO word VALUES(?,?);",(i.lower() ,morph.parse(i)[0].normal_form,) )	
conn.commit()



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





input("готово")

