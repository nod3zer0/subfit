# subfit: fit easy submit

Subfit is a simple script to submit your project to the studis.

## Features

- configurable with config file
- supports multiple types of authentication
  - prompt for username and password
  - use login file with username or username and password
  - gets cookie from the browser
- automatically compresses archive before submitting
- downloads the archive after submission from Studis and compares hashes with original file 
- prints time of submission from studis

## What does it do when submitting

1. creates archive if specified
2. gets login information
3. checks if the file has already been submitted
   1. removes old submission
4. submits file
5. checks if the file was submitted correctly (`--check` option)
   1. downloads file into `--check_folder`
   2. compares hashes
6. gets the time of submission in studis, and prints its value

## Requirements

- python3
- pip3
- Rest is in `requirements.txt`

## Installation

### Clone repository

Download this repository to the folder where you want to have subfit installed.

```bash
git clone https://github.com/nod3zer0/AutoSubmit.git
```

### Install requirements

```bash
pip3 install -r requirements.txt
```

### install in usr/local/bin

```bash
sudo chmod +x subfit.py
sudo ln -rs subfit.py /usr/local/bin/subfit   
```

### Updating

If you installed it with symbolic link. You can just use `git pull` from where you have downloaded this repository.

## Command line usage

```bash
subfit (-u | --url) "<studis_submission_url>" (-f | --file) <file_to_submit>
[-l | --login_type (browser_cookies --browser <browser>) | (login_file --login_file <path_to_login_file>) | prompt)]
[(-a | --archive_command) <archive_command>] [(-c | --check --check_folder <path_to_check_folder)]
```

Arguments are described in the configuration section. Command line values have precedence over configuration values. Required arguments need to be specified either in command line or in the config file.

### With config file

Running in the same folder as the config file (with name subfit_config.yml):

```bash
subfit
```

Running with the config file in a different folder:

```bash
subfit --config <path_to_config_file>
```

### Without config file

Prompt for username and password:

```bash
subfit --url "<studis_submission_url>" --file <file_to_submit>
```

Use login file:

```bash
subfit --url "<studis_submission_url>" --file <file_to_submit> --login_type login_file --login_file <login_file> 
```

Use cookie from browser:

```bash
subfit --url "<studis_submission_url>" --file <file_to_submit> --login_type browser_cookies --browser chrome
```

## Configuration file

The config file is a simple yaml file. If it is named `subfit_config.yml` it will be loaded automatically. 

Example config file:

```yaml
# filepath to file to submit
file: xlogin.tar
# command for creating archive (leave blank if you dont want to create archive)
archive_command: tar -cvf xlogin.tar file1.c file2.c
# url of where to upload file
url: https://www.vut.cz/studis/student.phtml?sn=zadani_odevzdani&registrace_zadani_id=971964&apid=268279
#compares hashes of uploaded and local file after upload
check: true
#where to download file after uploading for hash checking
#(folders will be created, files will be owerwritten!)
check_folder: test_folder
# for login with browser cookies fill in browser
browser: brave
# fill in path to yaml file with login information
login_file: /home/username/login.yml
#broser_cokies/login_file/prompt
login_type: login_file
```

## Configuration values

Specifying any of the listed value as command line arguments overrides stored value in configuration. If the config is named `subfit_config.yml` it will be loaded automatically.

- `file` - path to file to submit (short command line argument: `-f`)
- `archive_command` - command for creating archive (leave blank if you dont want to create archive) (short command line argument: `-a`)
- `url` - url of the submission page in Studis (image bellow) (short command line argument: `-u`) ![submit_page](./docs/img/submit_page.png)
- `check` - verifies uploaded file by downloading it from Studis and comparing hashes with the original file (short command line argument: `-c`)
  - `check_folder` - destination path for downloaded files from studis (folders will be created, and files will be overwritten!)
- `login_type` - used method for obtaining user credentials during submission (short command line argument: `-l`). Applicable values are:
  - **browser_cookies** - get the cookie from the browser
  - **login_file** - use login file (path specified in `login_file`)
  - **prompt** - prompt for username and password
- `browser` - for login with browser cookies fill in the browser. Applicable only with *browser_cookies* as a value for login type.
    - accepted values: chrome, firefox, brave, opera, edge, chromium, vivaldi, safari 
- `login_file` - destination path for yaml login file storing user credentials to Studis. Applicable only with *login_file* as a value for login type.

## Example login.yml file

```yaml
username: xlogin00
password: password
```

The password field is optional in the login file:

```yaml
username: xlogin00
```

During submission, the password prompt will appear if the password field is omitted.

## How to prepare subfit for your project

1. create config file in your project folder
   1. set `file` to the file you want to submit (usually archive file with the specified format by the  project assignment)
   2. optionally set `archive_command` to any valid bash command for creating archive before the submission begins
   3. set `url` to the submission url project page![submit_page](./docs/img/submit_page.png)
   4. optionally set `check` to true to verify file after upload
      1. set `check_folder` to the folder where to download file for checking
   5. set `login_type` to login type
      1. for example `login_type: login_file`
          1. set `login_file` to path to login file
2. run `subfit` in your project folder. The file will be submitted and optionally verified if `check` is set to true.

## Parsing values

### How does login work?

Each time the login page is refreshed, it gets a new sv[fdkey] from the server. So this script first gets this value from the login page, and then sends it back with username, password, and timestamp, to get the session cookie.

### How does file submission work?

First, it gets the page with the submission form and gets the s_key and s_tkey (which is new every time the page gets refreshed). Then it sends the file these values and the session.

## TODO

- [ ] moodle (ELEARNING) support
- [ ] support multiple files
- [ ] git hook after merge/commit to master
- [ ] save cookies for later use for faster submissions
