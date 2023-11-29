import browser_cookie3
import requests
import shutil
import os
cj = browser_cookie3.brave()



def download_file(url, root_des_path='./'):
    local_filename = url.split('/')[-1]
    local_filename = os.path.join(root_des_path, local_filename)
    # r = requests.get(link, cookies=cj)
    with requests.get(url, cookies=cj, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    return local_filename

a = download_file("https://www.vut.cz/studis/zadani_soubor.php?reg_zadani_soubor_id=302118")

#r = requests.get('https://www.vut.cz/studis/student.phtml?sn=zadani_odevzdani&operation=delete&registrace_zadani_id=988079&reg_zadani_soubor_id=302098&apid=268243',cookies=cj, stream=True)

url = 'https://www.vut.cz/studis/student.phtml?sn=zadani_odevzdani&registrace_zadani_id=988079&apid=268243'
file_path = 'xceska06.zip'  # Replace this with your file path

headers = {
    'authority': 'www.vut.cz',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'referer': 'https://www.vut.cz/studis/student.phtml?sn=zadani_odevzdani&operation=delete&registrace_zadani_id=988079&reg_zadani_soubor_id=302099&apid=268243',
    'origin': 'https://www.vut.cz',
    'sec-ch-ua': '"Brave";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    # Add other necessary headers here
}


files = {
    'soubor': open(file_path, 'rb')
}

Data = {
    's_tkey' : 'Cs0BfT6Cx0',
    's_key' : 'c449b6526e',
    'formID' : 'formAddFile',
    'btnSubmit' : 1,
    'soubor' : open(file_path, 'rb')
}

response = requests.post(url,data=Data, cookies=cj, files=files)

print(response.status_code)
print(response.text)# This will display the response content