const fs=require('fs');global.window={};let NEWS=[];
const src=fs.readFileSync('news.js','utf8')+'\n'+fs.readFileSync('piste_data.js','utf8')+';module.exports={NEWS,PISTE};';
fs.writeFileSync('/tmp/_w.js',src.replace(/^const NEWS/m,'NEWS').replace(/^let NEWS/m,'NEWS'));
const {NEWS:N,PISTE:P}=require('/tmp/_w.js');const ago=d=>new Date(Date.now()-d*864e5).toISOString().slice(0,10);
const out={news:N.filter(n=>n.d>=ago(90)).map(n=>({k:n.k,d:n.d,t:n.t,r:n.r,src:n.s})),
 jo:P.jo.filter(x=>x.d>=ago(45)&&x.nat!=='DECRET').map(x=>({d:x.d,t:x.t,nat:x.nat})),
 jp:P.jp.filter(x=>x.d>=ago(45)&&(x.src==='ce'?x.p==='A':/[rl]/.test(x.p||''))).map(x=>({d:x.d,j:x.src==='ce'?(x.jur||'CE'):'Cass. '+x.ch,n:x.n,h:x.h,s:(x.s||'').slice(0,700),sol:x.sol}))};
fs.writeFileSync('weekly_src.json',JSON.stringify(out,null,1));console.log(out.news.length,out.jo.length,out.jp.length);
