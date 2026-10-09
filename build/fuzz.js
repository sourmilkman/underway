const net=require('./network.json'); const Router=require('./router.js'); const R=new Router(net); const S=net.stations;
let n=0,fail=0,bad=0,maxT=0,maxP=null,t0=Date.now(),slow=0;
const rnd=(()=>{let x=12345;return()=>(x=(x*1103515245+12345)%2147483648)/2147483648})();
for(let k=0;k<3000;k++){const a=Math.floor(rnd()*S.length),b=Math.floor(rnd()*S.length); if(a===b)continue; n++;
 const t=Date.now(); const rs=R.routes(a,b); if(Date.now()-t>60)slow++;
 if(!rs.length){fail++; if(fail<5)console.log('NO ROUTE',S[a].n,'->',S[b].n); continue;}
 for(const j of rs){ // continuity check
   let pos=a, ok=true;
   for(const l of j.legs){ if(l.type==='ride'){ if(l.from!==pos)ok=false; pos=l.to; if(l.nStops<1)ok=false;} else if(l.type==='walk'){ if(l.from!==pos)ok=false; pos=l.to; } }
   if(pos!==b)ok=false; if(!ok){bad++; if(bad<4)console.log('BAD',S[a].n,'->',S[b].n,JSON.stringify(j.legs.map(l=>[l.type,l.from,l.to])));}
 }
 if(rs[0].total>maxT){maxT=rs[0].total;maxP=S[a].n+' -> '+S[b].n;}
}
console.log({n,fail,bad,maxT,maxP,slow,avgms:(Date.now()-t0)/n});
