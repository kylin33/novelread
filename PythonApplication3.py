# -*- coding: utf-8 -*-
import urllib
from bs4 import BeautifulSoup
from urllib.request import urlopen

import os
import sys
import json
import re
import pymysql

from colorama import init
import ssl
from pymysql.cursors import Cursor
ssl._create_default_https_context = ssl._create_unverified_context

# from utils.plots import output_to_target
init(strip=not sys.stdout.isatty())
from termcolor import cprint 
from pyfiglet import figlet_format
from prettytable import PrettyTable

from socket import error as SocketError
import errno

source = "https://www.biqugeapp.com"
rex = r"""(?<=[}\]"'])\s*,\s*(?!\s*[{["'])"""

def search(keywords):
	keyname = urllib.parse.quote(keywords)
	result = []
	try:
		search = urlopen("https://sou.jiaston.com/search.aspx?key=" + keyname + "&page=1&siteid=app2").read().decode('GBK')
	except SocketError as e:
		if e.errno != errno.ECONNRESET:
			raise
		pass
	bookinfo = BeautifulSoup(search, features='html.parser').getText()
	bookinfo = json.loads(bookinfo)['data']

	for items in bookinfo[0:]:
		result.append([items['Id'], 
			items['Name'], 
			items['Author'], 
			items['Desc'][:20]]
        )
	return result

def table(bookid):
    bookid_ = int( int(bookid)/1000)+1
    # print(bookid, str(bookid_) )
    page = 'https://infos.anchengcn.com/BookFiles/Html/' + str(bookid_) + '/'+ bookid + '/index.html'
    table = urlopen(page).read()
	# print(table)
    output_list = BeautifulSoup(table, features='html.parser').getText()
    output_list = re.sub(rex, "", output_list, 0)
    output_list = json.loads(output_list)['data']['list']
    
    tables = []
    
    for link in output_list:
        link_list = link['list']
        for li in link_list:
            tables.append([li['name'],li['id']])

    return page,tables

def content(web, page):
    content_src = web.replace('infos', 'content').replace('index.html', '')
    content = urlopen(content_src+ str(page)+ '.html').read()
    out_texts = BeautifulSoup(content, features='html.parser').getText()
    text = json.loads(out_texts)['data']['content']
    # print(text.replace('\u3000','').replace('\r\n', ''))
    print(text)


def turnpage(page):
	turnpage = urlopen(page).read().decode('GBK')
	pointer = BeautifulSoup(turnpage, features='html.parser')
	pointer_p = pointer.find('div', id="page_bar").find('a', id='prevLink').get('href')
	pointer_n = pointer.find('div', id="page_bar").find('a', id='nextLink').get('href')
	if pointer_p == '':
		pointer_p = 'none'
	return [pointer_p, pointer_n]

def createdb():
    global cursor, db
    try:
        db = pymysql.connect(host='localhost', user='root', password='123', database='noval', charset = 'utf8')
    except:
        print("连接失败")
        exit(-1)
    cursor = db.cursor()
    # sql = "select * from information.TABLES where TABLE_NAME = 'NOVAL';"
    # if(cursor.execute(sql)):
    #     print('历史记录在')
    # else:
    sql = """CREATE TABLE IF NOT EXISTS NOVAL(
                Noval CHAR(20) NOT NULL,
                Id INT,
                Author CHAR(20),
                Chapter CHAR(100));"""
    cursor.execute(sql)
    # cursor.close()
    # db.close()

def addNoval(readed_li):
    sql = "insert into NOVAL (Noval, Id, Author) values (%s, %s, %s)"
    global cursor, db 
    cursor.execute(sql, readed_li)
    db.commit()

def  findNoval(readed_li):
    novalname = readed_li[0]
    sql = "select chapter from NOVAL where Noval=%s;"
    global cursor 
    cursor.execute(sql, novalname)
    flag = cursor.fetchall()
    return flag

def updatedb(readed_li, table_result):
    novalName = readed_li[0]
    chapterName = table_result
    sql = "update NOVAL set Chapter=%s where Noval=%s;"
    global cursor, db
    cursor.execute(sql , [chapterName, novalName])
    db.commit()


def read():
    os.system('clear')
    createdb();
    cprint(figlet_format('Reader', font='doom'), 'green', attrs=['bold'])
    #os.system('clear') use 'cls' for windows
    print('\x1b[6;30;42m' + 'Read the novel in your terminal' + '\x1b[0m')
    keywords = input("输入书名搜索:")
    # readed_li.append(keywords)
    search_result_raw = search(keywords)
    search_result = PrettyTable(["Index", "Title", "Author", "Updated to"])
    search_indexof = 1
    for result_raw in search_result_raw:
        search_result.add_row([search_indexof, result_raw[1], result_raw[2], result_raw[3]])
        search_indexof += 1
    print(search_result)
    search_indexof_selected = input('Select a index to continue: ')
    readed_li = [search_result_raw[int(search_indexof_selected) - 1][1], int(search_result_raw[int(search_indexof_selected) - 1][0]), search_result_raw[int(search_indexof_selected) - 1][2]]
    # print(readed_li)
    os.system('clear')
    chapter = findNoval(readed_li)
    if(chapter):
        print(chapter)
    else:
        print("这是新书")
        addNoval(readed_li)
    print('\x1b[6;30;42m' + search_result_raw[int(search_indexof_selected) - 1][1] + '\x1b[0m')
    table_web, table_result_raw = table(search_result_raw[int(search_indexof_selected) - 1][0])
    table_result = PrettyTable(["Index", "Title"])
    table_indexof = 1
    for result_raw in table_result_raw:
        table_result.add_row([table_indexof, result_raw[0]])
        table_indexof += 1
    print(table_result)
    table_indexof_selected = input('Select a index to continue: ')
    table_indexof_selected = int(table_indexof_selected)

    os.system('clear')
    print('\x1b[6;30;42m' + table_result_raw[table_indexof_selected - 1][0] + '\x1b[0m')
    content(table_web, table_result_raw[table_indexof_selected - 1][1])
    # page_loc = turnpage(table_result_raw[int(table_indexof_selected) - 1][1])
    loc = int(table_indexof_selected) - 1
    var = 1
    while var == 1:
        turnpage_loc = input("\r\n\r\nType ;p<Enter> to turn to previous page\r\n\r\nType ;n<Enter> to turn to next page\r\n\r\nType ;q<Enter> to quit\r\n\r\n")
        if turnpage_loc == ';p' :
            os.system('clear')
            print('\x1b[6;30;42m' + table_result_raw[loc - 1][0] + '\x1b[0m')
            loc -= 1
            table_indexof_selected -= 1
            content(table_web, table_result_raw[table_indexof_selected - 1][1])
        elif turnpage_loc == ';n' :
            os.system('clear')
            print('\x1b[6;30;42m' + table_result_raw[loc + 1][0] + '\x1b[0m')
            loc += 1
            table_indexof_selected += 1
            content(table_web,  table_result_raw[table_indexof_selected - 1][1])
            updatedb(readed_li,  table_result_raw[loc + 1][0])
            # page_loc = turnpage(source + page_loc[1])
        elif turnpage_loc == ';q':
            os.system('clear')
            sys.exit()
        elif turnpage_loc == ';r':
            read()


if __name__ == "__main__":
    global cursor , db
    read()			