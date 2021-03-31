import json


line_kkt_inform = "-" * 30
line_kkt_license = "-" * 34
lines = "-" * 80
connect_wait = 2
connect_tries = 0
max_connect_tries = 120

def open_json_file():
    with open('./fiscal_information.json', 'r', encoding='utf-8') as test:
        return json.load(test)

file_json = open_json_file()