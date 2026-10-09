const net = require('./network.json'); const Router = require('./router.js');
const R = new Router(net); const S = net.stations;
const id = n => { const i = S.findIndex(s => s.n === n); if (i < 0) throw new Error('no ' + n); return i; };
const fmt = j => `${j.total} min, ${j.changes} ch: ` + j.legs.map(l => l.type === 'ride' ? `${net.lines[l.line].name}[${S[l.from].n}→${S[l.to].n} ${l.nStops}st ${l.mins}m tw ${l.towards.map(x=>S[x].n).join("/")}]` : l.type === 'walk' ? `walk ${S[l.from].n}→${S[l.to].n} ${l.mins}m` : `chg ${l.mins}m`).join(' ');
const pairs = process.argv.slice(2).length ? [process.argv.slice(2)] : [
 ["King's Cross St Pancras","Waterloo"],["Heathrow Terminal 5","Canary Wharf"],["Edgware","High Barnet"],
 ["Brixton","Walthamstow Central"],["Wimbledon","Stratford"],["Richmond","Barking Riverside"],
 ["Watford Junction","Lewisham"],["New Addington","Bank"],["Bethnal Green (Underground)","Bethnal Green (Overground)"],
 ["Reading","Shenfield"],["Chesham","Woolwich Arsenal"],["Morden","Upminster"],["Euston","Victoria"],["Oxford Circus","Bank"]];
for (const [a, b] of pairs) { console.log(`\n== ${a} → ${b}`); const t=Date.now(); for (const j of R.routes(id(a), id(b))) console.log('  ' + fmt(j)); console.log('  ('+(Date.now()-t)+'ms)'); }
