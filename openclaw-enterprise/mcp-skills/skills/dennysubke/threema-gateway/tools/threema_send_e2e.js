const { spawn } = require("node:child_process");
const fs = require("node:fs");

function mustEnv(name){
 const v=process.env[name];
 if(!v) throw new Error(`Missing env ${name}`);
 return v;
}

function allowlist(){
 return (process.env.THREEMA_ALLOWED_RECIPIENTS||"").split(",").map(s=>s.trim()).filter(Boolean);
}

module.exports=async function({to,text}){
 if(!allowlist().includes(to)){
  return {ok:false,error:"Recipient not allowed"};
 }
 const from=mustEnv("THREEMA_GATEWAY_ID");
 const secret=mustEnv("THREEMA_GATEWAY_SECRET");
 const key=fs.readFileSync(mustEnv("THREEMA_PRIVATE_KEY_PATH"),"utf8").trim();

 return await new Promise(resolve=>{
  const child=spawn("threema-gateway",["send_e2e",to,from,secret,key],{stdio:["pipe","pipe","pipe"]});
  let out="",err="";
  child.stdout.on("data",d=>out+=d.toString());
  child.stderr.on("data",d=>err+=d.toString());
  child.on("close",code=>{
   if(code===0) resolve({ok:true,response:out.trim()});
   else resolve({ok:false,error:err.trim()});
  });
  child.stdin.write(Buffer.from(text,"utf8"));
  child.stdin.end();
 });
};
