import requests

URL = "https://maker.ifttt.com/trigger/Door_Broken/with/key/m1Hn2_dctzv0VybhDaSEfZcman_WyKct5SA-aFEaM8n"

location = "IFTTT"

PARAMS = {'address': location}

r = requests.get(url = URL, params = PARAMS)

