from fastapi import FastAPI,Request
import os,json,datetime

app=FastAPI()
INBOX=os.getenv("THREEMA_INBOX_PATH","./inbox.jsonl")
TOKEN=os.getenv("THREEMA_CALLBACK_TOKEN","")

@app.post("/threema/callback")
async def cb(req:Request):
 q=req.query_params.get("token","")
 if TOKEN and q!=TOKEN:
  return {"ok":False}
 data=await req.json()
 entry={"ts":datetime.datetime.utcnow().isoformat(),"payload":data}
 with open(INBOX,"a",encoding="utf-8") as f:
  f.write(json.dumps(entry)+"\n")
 return {"ok":True}
