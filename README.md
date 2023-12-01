
# AutoSubmit

It is a simple script to submit your code to the online studis.

## Features

- configurable with config file
- multiple types of authentication
  - prompt for username and password
  - login file with username and password
  - get cookie from browser (optional: needs package `browser-cookie3`)
- automaticly compress archive before submitting
- check file hashes after submitting

## What does it do when submitting

1. creates archive if specified
2. gets login information
3. checks if file already submitted
   1. removes old submission
4. submits file
5. checks if file was submitted correctly (`--check` option)
   1. downloads file into `--check_folder`
   2. compares hashes

## Requirements

- python3
- Rest is in `requirements.txt`

## Installation

### Install requirements

```bash
pip3 install -r requirements.txt
```

### install in usr/local/bin

```bash
sudo cp AutoSubmit.py /usr/local/bin/AutoSubmit
sudo chmod +x /usr/local/bin/AutoSubmit
```

## Usage

### From commandline

Prompt for username and password:

```bash
python3 autosubmit.py --url <studis_submission_url> --file <file_to_submit>
```

Use login file:

```bash
python3 autosubmit.py --url <studis_submission_url> --file <file_to_submit> --login_file <login_file>
```

Use cookie from browser:

```bash
python3 autosubmit.py --url <studis_submission_url> --file <file_to_submit> --cookie <cookie_name>
```

### with config file

Running in same folder as config file:

```bash
python3 autosubmit.py
```

Running with config file in different folder:

```bash
python3 autosubmit.py --config <path_to_config_file>
```

## Config file

The config file is a simple yaml file.

Example config file:

```yaml
# filepath to file to submit
file: xlogin.tar
# command for creating archive (leave blank if you dont want to create archive)
archive_command: tar -cvf xlogin.tar file1.c file2.c
# url of where to upload file
url: https://www.vut.cz/studis/student.phtml?sn=zadani_odevzdani&registrace_zadani_id=971964&apid=268279
#compares hasesh of uploaded and local file after upload
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

## config values

- `file` - path to file to submit
- `archive_command` - command for creating archive (leave blank if you dont want to create archive)
- `url` - url of where to upload file
- `check` - compares hashes of uploaded and local file after upload
- `check_folder` - where to download file after uploading for hash checking (folders will be created, files will be owerwritten!)
- `browser` - for login with browser cookies fill in browser
- `login_file` - fill in path to yaml file with login information
- `login_type` - browser_cookies/login_file/prompt/prompt_force
  - browser_cookies - get cookie from browser (optional: needs package `browser-cookie3`)
  - login_file - use login file (path specified in `login_file`)
  - prompt - prompt for username and password
    -  if there is a login file, it will use username from there
  - prompt_force - prompt for username and password, even if there is a login file

## Example login file

```yaml
username: xlogin00
password: password
```

if there is only username, you can use prompt and it will ask only for password

```yaml
username: xlogin00
```

## TODO

- [ ] moodle support
- [ ] support multiple files