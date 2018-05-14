Sample Project to use Talk2M Live data througth the APIv2


First steps:
============

You have to install python 3 (Avoid python 3.6.4 with Microsoft Windows (see: https://bugs.python.org/issue32394 ))

Install requirements
	pip install -r requirements.txt

Install an 'eWON Flexy' with firmware >= 12.3s0PR
Register it in talk2m, lets call it: 'EWON_NAME'
Configure some tags in your ewon Flexy and turn on the OPCUA Server for the group of your tags.


execute the example:
cd APIv2
Update the credentials file with you own credentials
python example.py [-h] [-c [CREDENTIALS_FILE]] [-d [LOG_LEVEL]] [-a] [-t] EWON_NAME

positional arguments:
  EWON_NAME             your eWON name registered in your T2M account

optional arguments:
  -h, --help            show this help message and exit
  -c [CREDENTIALS_FILE]
                        your credential file
  -d [LOG_LEVEL]        Activate debug mode & specify your loglevel
                        (WARN,INFO)
  -a                    Get account information
  -t                    Get tags details


This script will connect the the ewon flexy to get its tags, subscribe to each tag's value changes and print a line for each of those changes.
