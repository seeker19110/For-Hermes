import os
import sys
import msal
import requests
from dotenv import load_dotenv

# Pathing for OpenClaw local execution
ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(ENV_PATH)

CLIENT_ID = os.getenv('SECRETARY_CLIENT_ID')
TENANT_ID = os.getenv('SECRETARY_TENANT_ID')
SCOPES = ['Files.ReadWrite', 'Mail.ReadWrite', 'Mail.Send', 'User.Read']
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID if TENANT_ID else 'common'}"

def get_token():
    if not CLIENT_ID:
        print("CONFIG_ERROR: Missing SECRETARY_CLIENT_ID.")
        sys.exit(1)
    
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    accounts = app.get_accounts()
    
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result: return result['access_token']

    # Start Device Code Flow for CLI/Agent interface
    flow = app.initiate_device_flow(scopes=SCOPES)
    print(f"USER_ACTION_REQUIRED: {flow['message']}")
    result = app.acquire_token_by_device_flow(flow)
    return result.get("access_token")

def handle_mail(action, args):
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    if action == "list":
        r = requests.get("https://graph.microsoft.com/v1.0/me/messages?$top=5", headers=headers)
        print(r.json())
    elif action == "send":
        payload = {
            "message": {
                "subject": args[1],
                "body": {"contentType": "Text", "content": args[2]},
                "toRecipients": [{"emailAddress": {"address": args[0]}}]
            }
        }
        r = requests.post("https://graph.microsoft.com/v1.0/me/sendMail", headers=headers, json=payload)
        print("Mail Sent" if r.status_code == 202 else f"Error: {r.text}")

def handle_drive(action, args):
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    if action == "list":
        r = requests.get("https://graph.microsoft.com/v1.0/me/drive/root/children", headers=headers)
        print(r.json())
    elif action == "upload":
        name, content = args[0], args[1]
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/Secretary_Vault/{name}:/content"
        r = requests.put(url, headers=headers, data=content)
        print(f"File {name} uploaded successfully.")

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(0)
    cmd = sys.argv[1]
    if cmd == "check-config":
        if not CLIENT_ID: print("CONFIG_ERROR")
        else: print("CONFIG_OK")
    elif cmd == "mail": handle_mail(sys.argv[2], sys.argv[3:])
    elif cmd == "drive": handle_drive(sys.argv[2], sys.argv[3:])