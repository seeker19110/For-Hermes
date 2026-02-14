import subprocess
def run(user_input):
    return subprocess.call(user_input, shell=True)