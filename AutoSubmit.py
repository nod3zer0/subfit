#!/bin/python3
from termcolor import colored, cprint
import requests
import bs4 as bs
import shutil
import os
import sys
import time
import getopt
import yaml
import getpass
# optional imports
try:
    import browser_cookie3
except ImportError:
    browser_cookie3 = None

"""parses arguments from command line
"""
def parseArgs():

    config = {}

    argumentList = sys.argv[1:]

    # Options
    options = "hf:a:u:cb:l:t:"

    # Long options
    long_options = ["help","file=", "archive_command=", "url=", "check", "check_folder=", "browser=", "login_file=", "login_type=" ]


    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)

        # checking each argument
        for currentArgument, currentValue in arguments:

            if currentArgument in ("-h", "--Help"):
                print ("Displaying Help")
            elif currentArgument in ("-f", "--file"):
                config['file'] = currentValue
            elif currentArgument in ("-a", "--archive_command"):
                config['archive_command'] = currentValue
            elif currentArgument in ("-u", "--url"):
                config['url'] = currentValue
            elif currentArgument in ("-c", "--check"):
                config['check'] = True
            elif currentArgument in ("-b", "--browser"):
                config['browser'] = currentValue
            elif currentArgument in ("-l", "--login_file"):
                config['login_file'] = currentValue
            elif currentArgument in ("-t", "--login_type"):
                config['login_type'] = currentValue
            elif currentArgument in ("-cb", "--check_folder"):
                config['check_folder'] = currentValue
            elif currentArgument in ("-cf", "--config_file"):
                config['config_file'] = currentValue

    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
        sys.exit(2)
    return config

    """loads yaml config file
    """
def loadConfig(path, config):
    with open(path) as f:
        file_config = yaml.load(f, Loader=yaml.FullLoader)

    # overwrite conly empty config values
    for key in file_config:
        if (not key in config):
            config[key] = file_config[key]

    if (not "url" in config):
        print(colored("[ERR] url not specified", 'red'))
        exit(1)
    if (not "file" in config):
        print(colored("[ERR] file not specified", 'red'))
        exit(1)
    if (not "login_type" in config or config["login_type"] is None):
        config["login_type"] = "prompt"
    if (config["login_type"] == "login_file"):
        if (not "login_file" in config):
            print(colored("[ERR] login_file not specified", 'red'))
            exit(1)
    elif (config["login_type"] == "browser_cookies"):
        if (not "browser" in config):
            print(colored("[ERR] browser not specified", 'red'))
            exit(1)
    elif ("check" in config and config["check"]):
        if (not "check_folder" in config):
            print(colored("[ERR] check_folder not specified", 'red'))
            exit(1)

    return config

def loadLoginFile(path):
    with open(path) as f:
        login_list = yaml.load(f, Loader=yaml.FullLoader)

    return login_list

def login(username, password):
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
    'LDAPlogin' : username,
    'LDAPpasswd' : password,
    'login' : ''

    }

    s.post('https://www.vut.cz/login/in', data=login_data)
    return s



    """uploads file to specified url from studis
    """
def upload_file_session(s, url, file_path, login_type):
    r = s.get(url, stream=True)
    # get delete file url
    r = s.get(url, stream=True)
    soup = bs.BeautifulSoup(r.text,'lxml')
    text1 = soup.find_all('a', string = "Smazat")

    # delete file if exists
    if (text1):
        deleteUrl = "https://www.vut.cz/studis/" +text1[0]['href']
        r = s.get(deleteUrl, stream=True)
        if (r.status_code == 200):

             print(colored("[OK] response: 200", 'green'))
        else:
            print(colored("[ERR] response: " + r.status_code, 'red'))
            exit(1)
        print("deleting file on URL: " +deleteUrl)

    # get keys
    print("getting keys")
    r = s.get(url, stream=True)

    if (r.status_code == 200):
        print(colored("[OK] response: 200", 'green'))
    else:
        print(colored("[ERR] response: " + r.status_code, 'red'))
        exit(1)

    soup = bs.BeautifulSoup(r.text,'lxml')
    supa = soup.find('input',attrs={'id' : 's_tkey'})
    if (not supa):
        print(colored("[ERR] not logged in", 'red'))
        if (login_type == "prompt"):
            print(colored("[INFO] wrong password or username", 'yellow'))
        if (login_type == "login_file"):
            print(colored("[INFO] wrong login_file", 'yellow'))
        if (login_type == "browser_cookies"):
            print(colored("[INFO] try going onto this adress in specified browser, then try again. Or use other type of authentification.", 'yellow'))
            print(colored("[INFO] "+ url , 'yellow'))
        exit(1)
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
    if (r.status_code == 200):
        print(colored("[OK] response: 200", 'green'))
    else:
        print(colored("[ERR] response: " + r.status_code, 'red'))
    print("file uploaded")

""" downloads file from specified url from studis
"""
def downloadFile(s, url, filename, downloadFolder):
    r = s.get(url, stream=True)
    soup = bs.BeautifulSoup(r.text,'lxml')

    supa =  soup.find_all('a', string = filename)
    downloadUrl = "https://www.vut.cz/studis" + supa[0]['href'].removeprefix(".")
    print("downloading file:" + filename + " from URL: " + downloadUrl)
    print(downloadUrl)
    r = s.get(downloadUrl, stream=True)
    if (r.status_code == 200):
         print(colored("[OK] response: 200", 'green'))
    else:
        print(colored("[ERR] response: " + r.status_code, 'red'))
        exit(1)
    print(downloadFolder)
    os.makedirs(downloadFolder, exist_ok=True)
    with open(os.path.join(config["check_folder"],"downloaded"), 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)
    print("file downloaded")

""" compares hashes of two files
"""
def compareHashes(file1, file2):
    hash1 = os.system("md5sum " + file1)
    hash2 = os.system("md5sum " + file2)
    if (hash1 == hash2):
        return True
    else:
        return False



config = parseArgs()
if ("config_file" in config):
    config = loadConfig(config["config_file"], config)
else:
    config = loadConfig("config.yml", config)


# #'https://www.vut.cz/studis/student.phtml?sn=zadani_odevzdani&registrace_zadani_id=988079&apid=268243'
# url = sys.argv[1]
# #'xceska06.zip'
# file_path = sys.argv[2]



login_info = loadLoginFile(config["login_file"])
if (config["login_type"] == "login_file"):
    if (not "username" in login_info):
        print(colored("[ERR] username not specified in login_file", 'red'))
        exit(1)
    if (not "password" in login_info):
        print(colored("[ERR] password not specified in login_file", 'red'))
        exit(1)
    s = login(login_info["username"], login_info["password"]);
elif (config["login_type"] == "browser_cookies"):

    if (browser_cookie3 is None):
        print(colored("[ERR] browser_cookie3 not installed", 'red'))
        print(colored("[INFO] for enabling authentification with browser cookie install browser_cookie3 (pip3 install browser_cookie3)", 'yellow'))
        print(colored("[INFO] or use other type of authentification (prompt, login_file)", 'yellow'))
        exit(1)


    if (not config["browser"]):
        print(colored("[ERR] browser not specified (example: --browser chromium)", 'red'))
        exit(1)

    if (config["browser"] == "chrome"):
        cj = browser_cookie3.chrome()
    elif (config["browser"] == "firefox"):
        cj = browser_cookie3.firefox()
    elif (config["browser"] == "brave"):
        cj = browser_cookie3.brave()
    elif (config["browser"] == "opera"):
        cj = browser_cookie3.opera()
    elif (config["browser"] == "edge"):
        cj = browser_cookie3.edge()
    elif (config["browser"] == "chromium"):
        cj = browser_cookie3.chromium()
    elif (config["browser"] == "vivaldi"):
        cj = browser_cookie3.vivaldi()
    elif (config["browser"] == "safari"):
        cj = browser_cookie3.safari()
    s = requests.Session()
    s.cookies = cj
elif (config["login_type"] == "prompt" or config["login_type"] == "prompt_force"):
    if ("username" in login_info and login_info["login_type"] == "prompt_force"):
        print(colored("[INFO] using username form login_file, if you want to specify username use --login_type prompt_force", 'blue'))
        username = login_info["username"]
    else:
        username = input("Enter username: ")
    password = getpass.getpass(prompt='Enter password: ', stream=None)
    s = login(username, password)
else:
    print(colored("[ERR] login_type not specified", 'red'))
    exit(1)

# archive file
if (config["archive_command"]):
    res = os.system(config["archive_command"])
    if (res == 0):
        print(colored("[OK] archive succesfull",'green'))
    else:
        print(colored("[ERR] archive unsuccesfull",'red'))
        exit(1)

upload_file_session(s, config["url"], config["file"], config["login_type"])


if (config["check"]):
    print("Checking if file was uploaded correctly.")
    print("downloading file")
    downloadFile(s, config["url"], os.path.basename(config["file"]), config["check_folder"])
    print("comparing hashes")
    if (compareHashes(config["file"], os.path.join(config["check_folder"],"downloaded"))):
        print(colored("[OK] upload succesfull: files are equal", 'green'))
    else:
        print(colored("[ERR] upload unsuccesfull: files are not equal", 'red'))




