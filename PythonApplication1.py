# -*- coding: utf-8 -*-
import urllib
from bs4 import BeautifulSoup
from urllib.request import urlopen
import os
import sys
import re
from colorama import init
init(strip=not sys.stdout.isatty())
from termcolor import cprint 
from pyfiglet import figlet_format
from prettytable import PrettyTable

source = "http://quduju.com"

def search():
	keywords = input("输入书名搜索:")
	keyname = urllib.parse.quote(keywords)
	result = []
	search = urlopen(source + "/search/?q=" + keyname).read().decode('utf-8')
	bookinfo = BeautifulSoup(search, features='html.parser').find('div', class_="novel").find("ul").find_all('li')
	for items in bookinfo:
		result.append([items.find('h4', class_="book-title").get_text(), 
			items.find('a', class_="book-layout").get('href'),
			items.find('span', class_="book-author").get_text(), 
			items.find('p', class_="book-desc").get_text()])
		#print(items.find('span',class_='pl_s1').find('a').get_text())
	#print(result)
	return result

def table(bookid):
	table = urlopen(source + "/mulu/" + bookid + "/1.html").read().decode('utf-8')
	output_list = BeautifulSoup(table, features='html.parser').find('ul', class_='novel-text-list').find_all('li')
	tables = []

	for link in output_list:
		tables.append([link.find('a').get_text(), source + link.find('a').get('href')])

	return tables

def content(page):
	content = urlopen(page).read().decode('utf-8')
	out_text = BeautifulSoup(content, features='html.parser').find("div",class_="chaptercontent").get_text().split()
	for ie in out_text:
		print(ie)
	#print(out_text)

def turnpage(page):
	turnpage = urlopen(page).read().decode('utf-8')
	pointer = BeautifulSoup(turnpage, features='html.parser')
	pointer_p = pointer.find('li', class_="end-itm prev").find('a').get('href')
	pointer_n = pointer.find('li', class_="end-itm next").find('a').get('href')
	if pointer_p == '':
		pointer_p = 'none'
	return [pointer_p, pointer_n]

if __name__ == "__main__":
	os.system('clear')
	cprint(figlet_format('telereader', font='doom'), 'green', attrs=['bold'])
	#os.system('clear') use 'cls' for windows ;use 'clear' for linux
	print('\x1b[6;30;42m' + 'telereader: Read the novel in your terminal' + '\x1b[0m')
	search_result_raw = search()
	search_result = PrettyTable(["Index", "Title", "Author", "Updated to"])
	search_indexof = 1
	for result_raw in search_result_raw:
		desc = re.sub(r'[a-zA-Z",:{}]',"",result_raw[3])
		search_result.add_row([search_indexof, result_raw[0], result_raw[2],desc[7:27]])
		search_indexof += 1
	print(search_result)
	search_indexof_selected = input('Select a index to continue: ')
	os.system('clear')
	print('\x1b[6;30;42m' + search_result_raw[int(search_indexof_selected) - 1][0] + '\x1b[0m')
	table_result_raw = table(search_result_raw[int(search_indexof_selected) - 1][1].split('.')[0].replace('/', ''))
	table_result = PrettyTable(["Index", "Title"])
	table_indexof = 1
	for result_raw in table_result_raw:
		table_result.add_row([table_indexof, result_raw[0]])
		table_indexof += 1
	print(table_result)
	table_indexof_selected = input('Select a index to continue: ')

	os.system('clear')
	print('\x1b[6;30;42m' + table_result_raw[int(table_indexof_selected) - 1][0] + '\x1b[0m')
	content(table_result_raw[int(table_indexof_selected) - 1][1])
	page_loc = turnpage(table_result_raw[int(table_indexof_selected) - 1][1])
	loc = int(table_indexof_selected) - 1
	var = 1
	while var == 1:
		turnpage_loc = input("\r\n\r\nType ;p<Enter> to turn to previous page\r\n\r\nType ;n<Enter> to turn to next page\r\n\r\nType ;q<Enter> to quit\r\n\r\n")
		if turnpage_loc == ';p' and page_loc[0] != '':
			os.system('clear')
			print('\x1b[6;30;42m' + table_result_raw[loc - 1][0] + '\x1b[0m')
			loc -= 1
			content(source + page_loc[0])
		elif turnpage_loc == ';n' and page_loc[0] != '':
			os.system('clear')
			print('\x1b[6;30;42m' + table_result_raw[loc + 1][0] + '\x1b[0m')
			loc += 1
			#content(source + search_result_raw[int(search_indexof_selected) - 1][1] + page_loc[1])
			content(source + page_loc[1])
			page_loc = turnpage(source + page_loc[1])
		elif turnpage_loc == ';q':
			os.system('clear')
			sys.exit()
