import requests
from multiprocessing.pool import ThreadPool
import json
from os.path import isfile, isdir, join, basename, dirname, splitext
import os
proxies = []

with open("proxy.txt", 'r') as f:
	#print(f.read())
	for i in f.read().splitlines():
		proxies.append({"http":i})
#print(proxies)


#----------------------------
OUT_DIR_IMG_ALL = "download_file_dir"
if (OUT_DIR_IMG_ALL in os.listdir()) == False:
	os.mkdir(OUT_DIR_IMG_ALL)
#----------------------------

#----------------------------


def download_file(url: str):
	file_name_start_pos = url.rfind("/") + 1
	file_name = url[file_name_start_pos:]
	if ((__current_id + '_' + file_name) in os.listdir(OUT_DIR_IMG_ALL) ==False):
		file_name = join(OUT_DIR_IMG_ALL, __current_id + '_' + file_name)


		r = requests.get(url, stream=True)
		if r.status_code == requests.codes.ok:
			with open(file_name, 'wb') as f:
				for data in r:
					f.write(data)

			
		


		return url
	else:
		print("хуй")
def download_images(obj: dict):
	global __current_id
	total_count = len(obj)
	i = 1
	pool = ThreadPool(16)
	for key, urls in obj.items():
		__current_id = key
		print('Downloading ' + str(i) + ' out of ' + str(total_count))
		result = list(pool.imap_unordered(download_file, urls))
		i += 1
	pool.close()

with open("result.json" ,"r") as file:
	file = json.load(file)
	download_images(file)



input()