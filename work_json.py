import json



def open_json_file():
    with open('./fiscal_information.json', 'r', encoding='utf-8') as file:
        return json.load(file)


