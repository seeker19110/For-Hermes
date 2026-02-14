const fs=require("node:fs");
module.exports=async function({count=20}={}){
 const path=process.env.THREEMA_INBOX_PATH||"./inbox.jsonl";
 if(!fs.existsSync(path)) return {ok:true,removed:0};
 const lines=fs.readFileSync(path,"utf8").split("\n");
 fs.writeFileSync(path,lines.slice(count).join("\n"));
 return {ok:true,removed:count};
};
