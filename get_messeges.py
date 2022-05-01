from bs4 import BeautifulSoup
import os 
from tqdm import tqdm
import pymorphy2
import json
import threading
#193183153



clear_lits = [
"Запись",
"Файл",
"Стикер"

]




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


for file_dir in os.listdir("Archive/messages"):
	for file_dir_user in os.listdir("Archive/messages/"+str(file_dir)):
		file_name_list.append("Archive/messages/"+str(file_dir)+"/"+file_dir_user)


def get_stat_tread(file_name_list,text_prog):
	data = {}
	for file_name in tqdm(file_name_list ,desc=("#"+str(text_prog))):
		with open(file_name ,"r") as file:
			f = file.read()
			soup = BeautifulSoup(f, 'lxml')	
			messeges = soup.find_all("div", attrs={ "class" : "item"})
			for i in messeges:
				text = i.find_all("div", attrs={})[3].text
				if len(text.split())>0:
					if (text.split()[0] in clear_lits) == False:
						for ii in text.lower().split():
							if (ii in data)== True:
								data[morph.parse(ii)[0]]["mass"] = data[ii]["mass"] + 1
								data[morph.parse(ii)[0]]["form"].append(ii)
							else:
								data[morph.parse(ii)[0]] = {}
								data[morph.parse(ii)[0]]["mass"] = 1
								data[morph.parse(ii)[0]]["form"] = [ii]
			

	with open(str(text_prog)+".json", "w",encoding='utf-8') as file:
		json.dump(data, file, indent=4, ensure_ascii=False)




# thr1 = threading.Thread(target = get_stat_tread, args = (split_mass(file_name_list,4)[0],))
# thr2 = threading.Thread(target = get_stat_tread, args = (split_mass(file_name_list,4)[1],))
# thr3 = threading.Thread(target = get_stat_tread, args = (split_mass(file_name_list,4)[2],))
# thr4 = threading.Thread(target = get_stat_tread, args = (split_mass(file_name_list,4)[3],))

#колво потоков 
tread_mathc = 4


mass = [] #тут хранятся потоки
file_name_list = split_mass(file_name_list,tread_mathc)
for i in range(0,tread_mathc):
	mass.append(threading.Thread(target = get_stat_tread, args = (file_name_list[i], i,)))
for i in mass:
	i.start()

for i in mass:
	i.join()



# for i in data:
# 	print(i , data[i]["mass"])






# def myfunc(a, b): 
#     print('сумма :',a + b) 
# thr1 = threading.Thread(target = myfunc, args = (1, 2))
# thr1.start()

input("готово")