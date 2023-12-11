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
from datetime import datetime
import re
# optional imports
try:
    import browser_cookie3
except ImportError:
    browser_cookie3 = None




submission_time = 0
start_of_submission=0

def parse_args():
    """parses arguments from command line
    """
    argumentList = sys.argv[1:]
    config = {}
    # Options
    options = "hf:a:u:cb:l:t:"

    # Long options
    long_options = ["help","config_file=","file=", "archive_command=", "url=", "check", "check_folder=", "browser=", "login_file=", "login_type=", "username=", "password=" ]


    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)

        # checking each argument
        for currentArgument, currentValue in arguments:

            if currentArgument in ("-h", "--help"):
                print_help()
                exit(0)
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
            elif currentArgument in ("--check_folder"):
                config['check_folder'] = currentValue
            elif currentArgument in ("--config_file"):
                config['config_file'] = currentValue
            elif currentArgument in ("--username"):
                config['username'] = currentValue
            elif currentArgument in ("--password"):
                config['password'] = currentValue

    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
        sys.exit(2)
    return config

def print_help():
    """prints help
    """
    print("subfit")
    print("Simple script to submit your project to the studis.")
    print("")
    print("usage:")
    print("subfit (-u | --url) \"<studis_submission_url>\" (-f | --file) <file_to_submit>")
    print("[-l | --login_type (browser_cookies --browser <browser>) | (login_file --login_file <path_to_login_file>) | prompt | args --username <username> --password <password>]))]")
    print("[(--config_file <path_to_config_file>)]")
    print("")
    print("argument description:")
    print("- file - path to file to submit (short command line argument: -f)")
    print("- archive_command - command for creating archive (leave blank if you dont want to create archive) (short command line argument: -a)")
    print("- url - url of the submission page in Studis (image bellow) (short command line argument: -u) ![submit_page](./docs/img/submit_page.png)")
    print("- check - verifies uploaded file by downloading it from Studis and comparing hashes with the original file (short command line argument: -c)")
    print("  - check_folder - destination path for downloaded files from studis (folders will be created, and files will be overwritten!)")
    print("- login_type - used method for obtaining user credentials during submission (short command line argument: -l). Applicable values are:")
    print("  - browser_cookies - get the cookie from the browser")
    print("  - login_file - use login file (path specified in login_file)")
    print("  - prompt - prompt for username and password")
    print("  - args - use username and password from arguments")
    print("- browser - for login with browser cookies fill in the browser. Applicable only with *browser_cookies* as a value for login type.")
    print("- login_file - destination path for yaml login file storing user credentials to Studis. Applicable only with *login_file* as a value for login type.")
    print("- username - username for login. Applicable only with *args* as a value for login type.")
    print("- password - password for login. Applicable only with *args* as a value for login type.")


def load_config(path, config):
    """loads yaml config file
       replaces only empty config values
    """
    if (not os.path.isfile(path)):
        print(colored("[ERR] config file not found", 'red'))
        exit(1)

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

def check_config(config):
    """checks if config is valid
    """
    if (not "url" in config):
        print(colored("[ERR] url not specified", 'red'))
        exit(1)
    if (not "file" in config):
        print(colored("[ERR] file not specified", 'red'))
        exit(1)
    if (not "login_type" in config or config["login_type"] is None):
        if ("browser" in config):
            config["login_type"] = "browser_cookies"
        elif ("login_file" in config):
            config["login_type"] = "login_file"
        else:
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

def load_login_file(path):
    """loads login_file
    """

    if (not os.path.isfile(path)):
        print(colored("[ERR] login_file not found", 'red'))
        exit(1)
    login_list = []
    with open(path) as f:
        login_list = yaml.load(f, Loader=yaml.FullLoader)

    if (not isinstance(login_list,dict)):
        print(colored("[ERR] login_file has syntax error", 'red'))
        exit(1)

    if (not login_list):
        print(colored("[ERR] login_file is empty", 'red'))
        exit(1)



    return login_list

def login(username, password):
    """logs in to studis
    """
    s = requests.Session()

    r = s.get("https://www.vut.cz/login/intra", stream=True)
    loginSoup = bs.BeautifulSoup(r.text,'lxml')

    loginSupa = loginSoup.find('input',attrs={'name' : 'sv[fdkey]'})

    fdkey = loginSupa.get('value')

    if (not fdkey):
        print(colored("[ERR] fdkey not found", 'red'))
        exit(1)


    login_data = {
    'special_p4_form' : 1,
    'login_form' : 1,
    'sentTime' : round(time.time()),
    'sv[fdkey]' : fdkey,
    'LDAPlogin' : username,
    'LDAPpasswd' : password,
    'login' : ''

    }

    response = s.post('https://www.vut.cz/login/in', data=login_data)

    if (response.status_code == 200):
        print(colored("[OK] response: 200", 'green'))
    else:
        print(colored("[ERR] response: " + response.status_code, 'red'))
        exit(1)

    return s




def upload_file(s, url, file_path, login_type):
    """uploads file to specified url from studis
    """
    if (not os.path.isfile(file_path)):
        print(colored("[ERR] file not found", 'red'))
        exit(1)
    if (url is None or url == ""):
        print(colored("[ERR] url not specified", 'red'))
        exit(1)

    r = s.get(url, stream=True)
    # get delete file url
    r = s.get(url, stream=True)
    soup = bs.BeautifulSoup(r.text,'lxml')
    text1 = soup.find_all('a', string = "Smazat")

    # delete file if exists
    if (text1):
        print("getting delete url")
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
    print(colored("uploading file..."))
    response = s.post(url,data=Data, files=files)
    if (r.status_code == 200):
        print(colored("[OK] response: 200", 'green'))
    else:
        print(colored("[ERR] response: " + r.status_code, 'red'))
    print("file uploaded")


def download_file(s, url, filename, downloadFolder):
    """ downloads file from specified url from studis
    """
    r = s.get(url, stream=True)
    soup = bs.BeautifulSoup(r.text,'lxml')

    supa =  soup.find_all('a', string = os.path.dirname(filename) + os.path.basename(filename).lower())
    if (not supa):
        print(colored("[ERR] file not found", 'red'))
        print(colored("[ERR] file not uploaded correctly", 'red') + colored("!!!", 'red', attrs=['blink']))
        exit(1)

    downloadUrl = "https://www.vut.cz/studis" + supa[0]['href'].removeprefix(".")
    print("downloading file:" + filename + " from URL: " + downloadUrl)
    r = s.get(downloadUrl, stream=True)
    if (r.status_code == 200):
         print(colored("[OK] response: 200", 'green'))
    else:
        print(colored("[ERR] response: " + r.status_code, 'red'))
        exit(1)
    print("creating: " + downloadFolder)
    os.makedirs(downloadFolder, exist_ok=True)
    with open(os.path.join(downloadFolder,"downloaded"), 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)
    print("file downloaded")


def compare_hashes(file1, file2):
    """ compares hashes of two files
    """
    hash1 = os.system("md5sum " + file1)
    hash2 = os.system("md5sum " + file2)
    if (hash1 == hash2):
        return True
    else:
        return False

def get_submission_time(s,url):
    """ gets submission file
    """
    r = s.get(url, stream=True)
    soup = bs.BeautifulSoup(r.text,'lxml')
    supa =  soup.find_all('small', string=True)
    if (supa):
        return supa[0].text
    else:
        print(colored("[ERR] submission time not found, probably not submited!", 'red'))
        exit(1)

def get_session_by_login_type(config):
    """ gets session by login type
    """

    login_type = config["login_type"]
    login_file = config["login_file"] if "login_file" in config else None
    browser = config["browser"] if "browser" in config else None
    password = config["password"] if "password" in config else None
    username = config["username"] if "username" in config else None

    login_info = {}
    if (login_file is not None):
        login_info = load_login_file(login_file)


    if (login_type == "login_file"):
        if (not "username" in login_info):
            print(colored("[WARN] username not specified in login_file", 'yellow'))
            login_info["username"] = input("Enter username: ")
        if (not "password" in login_info):
            print(colored("[WARN] password not specified in login_file", 'yellow'))
            login_info["password"] = getpass.getpass(prompt='Enter password: ', stream=None)
        s = login(login_info["username"], login_info["password"]);
    elif (login_type == "args"):
        if (username is None):
            print(colored("[ERR] username not specified", 'red'))
            exit(1)
        if (password is None):
            print(colored("[ERR] password not specified", 'red'))
            exit(1)
        s = login(username, password)
    elif (login_type == "browser_cookies"):

        if (browser_cookie3 is None):
            print(colored("[ERR] browser_cookie3 not installed", 'red'))
            print(colored("[INFO] for enabling authentification with browser cookie install browser_cookie3 (pip3 install browser_cookie3)", 'yellow'))
            print(colored("[INFO] or use other type of authentification (prompt, login_file)", 'yellow'))
            exit(1)


        if (not browser or browser == ""):
            print(colored("[ERR] browser not specified (example: --browser chromium)", 'red'))
            exit(1)
        try:
            if (browser == "chrome"):
                cj = browser_cookie3.chrome()
            elif (browser == "firefox"):
                cj = browser_cookie3.firefox()
            elif (browser == "brave"):
                cj = browser_cookie3.brave()
            elif (browser == "opera"):
                cj = browser_cookie3.opera()
            elif (browser == "edge"):
                cj = browser_cookie3.edge()
            elif (browser == "chromium"):
                cj = browser_cookie3.chromium()
            elif (browser == "vivaldi"):
                cj = browser_cookie3.vivaldi()
            elif (browser == "safari"):
                cj = browser_cookie3.safari()
        except(browser_cookie3.BrowserCookieError):
            print(colored("[ERR] browser not found", 'red'))
            exit(1)
        s = requests.Session()
        s.cookies = cj
    elif (login_type == "prompt"):
        username = input("Enter username: ")
        password = getpass.getpass(prompt='Enter password: ', stream=None)
        s = login(username, password)
    else:
        print(colored("[ERR] login_type not specified", 'red'))
        exit(1)
    return s

def archive_file(archive_command):
    """ archives file with specified command
    """
    res = os.system(archive_command)
    if (res == 0):
        print(colored("[OK] archive succesfull",'green'))
    else:
        print(colored("[ERR] archive unsuccesfull",'red'))
        exit(1)

def check_file_upload(s, url, file_path, check_folder):
    """ checks if file was uploaded correctly
    """
    print("Checking if file was uploaded correctly.")
    print("downloading file")
    download_file(s,  url, os.path.basename(file_path), check_folder)
    print("comparing hashes")
    if (compare_hashes(file_path, os.path.join(check_folder,"downloaded"))):
        print(colored("[OK] upload succesfull: files are equal", 'green'))
    else:
        print(colored("[ERR] upload unsuccesfull: files are not equal", 'red'))

def get_assignment_url(s, url):
    """ gets assignment url
    """
    print("getting assignment url")
    r = s.get(url, stream=True)
    if (r.status_code == 200):
        print(colored("[OK] response: 200", 'green'))
    else:
        print(colored("[WARN] response: " + r.status_code, 'yellow'))
        exit(1)

    soup = bs.BeautifulSoup(r.text,'lxml')
    supa =  soup.select_one("a[href*='student.phtml?sn=zadani_detail&zid=']")

    if (supa):
        return "https://www.vut.cz/studis/" + supa.get('href')
    else:
        print(colored("[WARN] assignment name not found", 'yellow'))

def main():

    start_of_submission = datetime.now().strftime(
                    '%d.%m.%Y %H:%M:%S.%f')

    config = parse_args()
    if ("config_file" in config):
        config = load_config(config["config_file"], config)
    elif os.path.isfile("subfit_config.yml"):
        config = load_config("subfit_config.yml", config)

    config = check_config(config)

    #s = get_session_by_login_type(config["login_type"], config["login_file"] if "login_file" in config else None, config["browser"] if "browser" in config else None)

    s = get_session_by_login_type(config)
    if ("archive_command" in config and config["archive_command"] != "" and config["archive_command"] is not None):
        archive_file(config["archive_command"])

    upload_file(s, config["url"], config["file"], config["login_type"])
    time_of_submission_local = datetime.now();

    if ("check" in config and config["check"]):
        check_file_upload(s, config["url"], config["file"], config["check_folder"])

    assignment_url = get_assignment_url(s, config["url"])

    print("")
    print("File was succesfully uploaded to assignment at url: " + assignment_url)
    print("All done")
    print("submission started:\t\t" + str(start_of_submission))
    submission_time_studis = get_submission_time(s,config["url"])
    print("time of submission (local): \t" + str(time_of_submission_local.strftime(
                    '%d.%m.%Y %H:%M:%S.%f')))
    print("time of submission (studis):\t" + str(submission_time_studis))
    print("time taken: \t\t\t" +  str((time_of_submission_local - datetime.strptime(start_of_submission,'%d.%m.%Y %H:%M:%S.%f')).total_seconds() ) + " seconds")

if __name__ == "__main__":
    main()