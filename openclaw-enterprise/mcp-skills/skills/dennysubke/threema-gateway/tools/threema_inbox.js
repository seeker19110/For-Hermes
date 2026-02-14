const fs=require("node:fs");
module.exports=async function({limit=20}={}){
 const path=process.env.THREEMA_INBOX_PATH||"./inbox.jsonl";
 if(!fs.existsSync(path)) return {ok:true,messages:[]};
 const lines=fs.readFileSync(path,"utf8").trim().split("\n").filter(Boolean);
 return {ok:true,messages:lines.slice(-limit).map(l=>JSON.parse(l))};
};
