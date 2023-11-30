import browser_cookie3
import requests
import bs4 as bs
import shutil
import os
import sys
import time


def login():
    s = requests.Session()

    r = s.get("https://www.vut.cz/login/intra", stream=True)
    loginSoup = bs.BeautifulSoup(r.text,'lxml')

    loginSupa = loginSoup.find('input',attrs={'name' : 'sv[fdkey]'})

    fdkey = loginSupa.get('value')

    login_data = {
    'special_p4_form' : 1,
    'login_form' : 1,
    'sentTime' : round(time.time()),
    'sv[fdkey]' : fdkey,
    'LDAPlogin' : '',
    'LDAPpasswd' : '',
    'login' : ''

    }

    s.post('https://www.vut.cz/login/in', data=login_data)
    return s




def upload_file_session(s, url, file_path):
    r = s.get(url, stream=True)
    # get delete file url
    r = s.get(url, stream=True)
    soup = bs.BeautifulSoup(r.text,'lxml')
    text1 = soup.find_all('a', string = "Smazat")

    # delete file if exists
    if (text1):
        deleteUrl = "https://www.vut.cz/studis/" +text1[0]['href']
        r = s.get(deleteUrl, stream=True)
        print(r.status_code)
        print("deleting file on URL: " +deleteUrl)

    # get keys
    print("getting keys")
    r = s.get(url, stream=True)
    print(r.status_code)
    soup = bs.BeautifulSoup(r.text,'lxml')
    supa = soup.find('input',attrs={'id' : 's_tkey'})
    s_tkey = supa.get('value')
    supa = soup.find('input',attrs={'id' : 's_key'})
    s_key = supa.get('value')


    # file to upload
    files = {
        'soubor': open(file_path, 'rb')
    }

    # data to upload
    Data = {
        's_tkey' : s_tkey,
        's_key' : s_key,
        'formID' : 'formAddFile',
        'btnSubmit' : 1,
        'soubor' : open(file_path, 'rb')
    }

    # upload file
    print("uploading file...")
    response = s.post(url,data=Data, files=files)
    print(response.status_code)
    print("file uploaded")

def upload_file_cookie(c, url, file_path):
    r = requests.get(url,cookies=c, stream=True)
    # get delete file url
    r = requests.get(url,cookies=c, stream=True)
    soup = bs.BeautifulSoup(r.text,'lxml')
    text1 = soup.find_all('a', string = "Smazat")

    # delete file if exists
    if (text1):
        deleteUrl = "https://www.vut.cz/studis/" +text1[0]['href']
        r = requests.get(deleteUrl,cookies=c, stream=True)
        print(r.status_code)
        print("deleting file on URL: " +deleteUrl)

    # get keys
    print("getting keys")
    r = requests.get(url,cookies=c, stream=True)
    print(r.status_code)
    soup = bs.BeautifulSoup(r.text,'lxml')
    supa = soup.find('input',attrs={'id' : 's_tkey'})
    s_tkey = supa.get('value')
    supa = soup.find('input',attrs={'id' : 's_key'})
    s_key = supa.get('value')


    # file to upload
    files = {
        'soubor': open(file_path, 'rb')
    }

    # data to upload
    Data = {
        's_tkey' : s_tkey,
        's_key' : s_key,
        'formID' : 'formAddFile',
        'btnSubmit' : 1,
        'soubor' : open(file_path, 'rb')
    }

    # upload file
    print("uploading file...")
    response = requests.post(url,data=Data,cookies=c, files=files)
    print(response.status_code)
    print("file uploaded")



cj = browser_cookie3.brave()

#'https://www.vut.cz/studis/student.phtml?sn=zadani_odevzdani&registrace_zadani_id=988079&apid=268243'
url = sys.argv[1]
#'xceska06.zip'
file_path = sys.argv[2]

s = login()

#upload_file_session(s, url, file_path)
upload_file_cookie(cj, url, file_path)