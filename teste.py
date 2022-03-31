import requests
import json

from requests.auth import HTTPBasicAuth
request = requests.get('https://api.github.com/user', auth=HTTPBasicAuth('wesleisantos25@hotmail.com', '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'))
todo = str(json.loads(request.content))
with open('retorno.json', 'a') as file:
    file.write(todo)