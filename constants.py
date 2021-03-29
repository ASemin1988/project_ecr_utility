import json
import os
from pathlib import Path

class Constants:
        with open('fiscal_information.json') as json_file:
            fiscal_inform = json.loads(json_file.read())
