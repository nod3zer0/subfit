import browser_cookie3
import requests
import bs4 as bs
import shutil
import os
import sys
cj = browser_cookie3.brave()

#'https://www.vut.cz/studis/student.phtml?sn=zadani_odevzdani&registrace_zadani_id=988079&apid=268243'
url = sys.argv[1]
#'xceska06.zip'
file_path = sys.argv[2]

# get delete file url
r = requests.get(url, cookies=cj, stream=True)
soup = bs.BeautifulSoup(r.text,'lxml')
text1 = soup.find_all('a', string = "Smazat")

# delete file if exists
if (text1):
    deleteUrl = "https://www.vut.cz/studis/" +text1[0]['href']
    r = requests.get(deleteUrl, cookies=cj, stream=True)
    print(r.status_code)
    print("deleting file on URL: " +deleteUrl)

# get keys
print("getting keys")
r = requests.get(url, cookies=cj, stream=True)
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
response = requests.post(url,data=Data, cookies=cj, files=files)
print(response.status_code)
print("file uploaded")
