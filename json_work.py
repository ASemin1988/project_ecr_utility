import json



def open_json_file(name):
    with open(name, 'r', encoding='utf-8') as file:
        return json.load(file)



