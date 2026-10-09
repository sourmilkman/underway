// Journey router: Dijkstra over (service, stop) states with change and wait costs.
(function (root) {
  function Router(net) {
    this.net = net;
    const S = net.stations.length;
    this.at = Array.from({ length: S }, () => []); // station -> [[svc, idx]]
    net.services.forEach((s, si) => s.stops.forEach((c, i) => this.at[c].push([si, i])));
    this.walks = Array.from({ length: S }, () => []);
    net.walks.forEach(([a, b, t]) => { this.walks[a].push([b, t]); this.walks[b].push([a, t]); });
    this.off = []; let o = 0;
    net.services.forEach((s, si) => { this.off[si] = o; o += s.stops.length; });
    this.N = o;
  }

  // Minimal binary heap
  function Heap() { this.a = []; }
  Heap.prototype.push = function (k, v) {
    const a = this.a; a.push([k, v]); let i = a.length - 1;
    while (i > 0) { const p = (i - 1) >> 1; if (a[p][0] <= a[i][0]) break; [a[p], a[i]] = [a[i], a[p]]; i = p; }
  };
  Heap.prototype.pop = function () {
    const a = this.a, top = a[0], last = a.pop();
    if (a.length) { a[0] = last; let i = 0; for (;;) { const l = 2 * i + 1, r = l + 1; let m = i;
      if (l < a.length && a[l][0] < a[m][0]) m = l; if (r < a.length && a[r][0] < a[m][0]) m = r;
      if (m === i) break; [a[m], a[i]] = [a[i], a[m]]; i = m; } }
    return top;
  };

  Router.prototype.changeTime = function (station, fromLine, toLine) {
    if (fromLine === toLine) return 1.5; // same line, different service (often same platform)
    const n = this.net.stations[station].l.length;
    return n >= 4 ? 5 : 4;
  };

  // opts: {ban:Set(lineIds), changePenalty:number}
  // State = (service, stop index, direction). dir 1 = travelling along the stop list, 0 = against it.
  Router.prototype.search = function (from, to, opts = {}) {
    const net = this.net, ban = opts.ban || new Set(), extra = opts.changePenalty || 0;
    const M = this.N * 2;
    const dist = new Float64Array(M).fill(Infinity), prev = new Int32Array(M).fill(-1), how = new Array(M);
    const h = new Heap();
    const lineOf = si => net.services[si].line;
    const wait = si => net.lines[lineOf(si)].wait;
    const node = (si, i, dir) => (this.off[si] + i) * 2 + dir;
    const relax = (n, d, p, kind) => { if (d < dist[n] - 1e-9) { dist[n] = d; prev[n] = p; how[n] = kind; h.push(d, n); } };
    const board = (si, i, d, p, kind) => { relax(node(si, i, 1), d, p, kind); relax(node(si, i, 0), d, p, kind); };
    for (const [si, i] of this.at[from]) if (!ban.has(lineOf(si))) board(si, i, wait(si), -1, 'start');
    for (const [b, t] of this.walks[from]) for (const [si, i] of this.at[b]) if (!ban.has(lineOf(si))) board(si, i, t + wait(si), -1, { walk: [from, b, t] });
    const svcOf = k => { let lo = 0, hi = this.off.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (this.off[m] <= k) lo = m; else hi = m - 1; } return lo; };
    const decode = n => { const k = n >> 1, si = svcOf(k); return { si, i: k - this.off[si], dir: n & 1 }; };
    let best = -1, endWalk = null, bestD = Infinity;
    while (h.a.length) {
      const [d, n] = h.pop(); if (d > dist[n]) continue;
      if (d >= bestD) break;
      const { si, i, dir } = decode(n), s = net.services[si], st = s.stops[i], lastI = s.stops.length - 1;
      if (st === to) { best = n; bestD = d; endWalk = null; break; }
      // ride on
      if (dir === 1 && i < lastI) relax(n + 2, d + s.t[i], n, 'ride');
      if (dir === 0 && i > 0) relax(n - 2, d + s.t[i - 1], n, 'ride');
      for (const [sj, j] of this.at[st]) {
        if (sj === si || ban.has(lineOf(sj))) continue;
        const t = net.services[sj];
        // through-running onto the next segment of the same line in the same direction
        if (t.line === s.line && dir === 1 && i === lastI && j === 0) { relax(node(sj, 0, 1), d, n, 'cont'); continue; }
        if (t.line === s.line && dir === 0 && i === 0 && j === t.stops.length - 1) { relax(node(sj, j, 0), d, n, 'cont'); continue; }
        board(sj, j, d + this.changeTime(st, s.line, t.line) + extra + wait(sj), n, 'change');
      }
      for (const [b, t] of this.walks[st]) {
        if (b === to && d + t < bestD) { bestD = d + t; best = n; endWalk = { t }; }
        for (const [sj, j] of this.at[b]) if (!ban.has(lineOf(sj))) board(sj, j, d + t + extra + wait(sj), n, { walk: [st, b, t] });
      }
    }
    if (best < 0) return null;
    const chain = []; let n = best;
    while (n !== -1) { chain.push(n); n = prev[n]; }
    chain.reverse();
    return this.toJourney(chain.map(n => { const x = decode(n); x.how = how[n]; return x; }), endWalk, from, to);
  };

  Router.prototype.toJourney = function (chain, endWalk, from, to) {
    const net = this.net, legs = [];
    let cur = null;
    for (const c of chain) {
      const s = net.services[c.si];
      if (c.how === 'ride' && cur) { cur.stops.push(s.stops[c.i]); cur.segs.push([c.si, c.i]); cur.dir = c.dir; continue; }
      if (c.how === 'cont' && cur) { cur.segs.push([c.si, c.i]); cur.dir = c.dir; continue; }
      if (c.how && c.how.walk) legs.push({ type: 'walk', from: c.how.walk[0], to: c.how.walk[1], mins: c.how.walk[2] });
      else if (c.how === 'change' && cur) legs.push({ type: 'change', at: s.stops[c.i], mins: this.changeTime(s.stops[c.i], cur.line, s.line) });
      cur = { type: 'ride', line: s.line, stops: [s.stops[c.i]], segs: [[c.si, c.i]], dir: c.dir };
      legs.push(cur);
    }
    if (endWalk) legs.push({ type: 'walk', from: legs[legs.length - 1].stops.slice(-1)[0], to, mins: endWalk.t });
    // compute ride details
    let total = 0;
    const out = [];
    for (const L of legs) {
      if (L.type !== 'ride') { total += L.mins; out.push(L); continue; }
      if (L.stops.length < 2) continue; // boarded and immediately left (walk transfer artefact)
      let mins = 0;
      for (let k = 1; k < L.segs.length; k++) {
        const [s1, i1] = L.segs[k - 1], [s2, i2] = L.segs[k];
        if (s1 === s2) mins += net.services[s1].t[Math.min(i1, i2)];
      }
      // direction: termini reachable by continuing the way we travelled
      const [ls, li] = L.segs[L.segs.length - 1], [ps, pi] = L.segs[L.segs.length - 2] || L.segs[0];
      const fwd = L.dir === 1;
      const towards = this.termini(ls, fwd);
      const wait = net.lines[L.line].wait;
      total += mins + wait;
      out.push({ type: 'ride', line: L.line, from: L.stops[0], to: L.stops[L.stops.length - 1], stops: L.stops, nStops: L.stops.length - 1, mins: Math.round(mins * 10) / 10, wait, towards });
    }
    // merge consecutive change markers produced by dropped zero-length rides
    const clean = [];
    for (const L of out) { const p = clean[clean.length - 1]; if (L.type === 'change' && p && p.type !== 'ride') continue; clean.push(L); }
    while (clean.length && clean[clean.length - 1].type === 'change') clean.pop();
    while (clean.length && clean[0].type === 'change') clean.shift();
    const rides = clean.filter(l => l.type === 'ride');
    return { from, to, legs: clean, total: Math.round(total), changes: Math.max(0, rides.length - 1),
             sig: rides.map(r => r.line + ':' + r.from + '>' + r.to).join('|'), lines: rides.map(r => r.line) };
  };

  Router.prototype.termini = function (si, fwd) {
    const net = this.net, res = new Set(), seen = new Set();
    const go = (si, fwd, depth) => {
      const key = si + (fwd ? '+' : '-'); if (seen.has(key) || depth > 8) return; seen.add(key);
      const s = net.services[si], endSt = fwd ? s.stops[s.stops.length - 1] : s.stops[0];
      let more = false;
      for (const [sj, j] of this.at[endSt]) {
        const t = net.services[sj]; if (sj === si || t.line !== s.line) continue;
        if (fwd && j === 0) { more = true; go(sj, true, depth + 1); }
        if (!fwd && j === t.stops.length - 1) { more = true; go(sj, false, depth + 1); }
      }
      if (!more) res.add(endSt);
    };
    go(si, fwd, 0);
    return [...res];
  };

  // Up to k distinct good routes
  Router.prototype.routes = function (from, to, k = 3) {
    if (from === to) return [];
    const found = new Map();
    const add = j => { if (j && !found.has(j.sig)) found.set(j.sig, j); };
    const best = this.search(from, to); if (!best) return [];
    add(best);
    add(this.search(from, to, { changePenalty: 8 }));
    const tried = new Set();
    const queue = [[]];
    while (queue.length && tried.size < 14) {
      const banList = queue.shift();
      const key = banList.slice().sort().join(','); if (tried.has(key)) continue; tried.add(key);
      const j = banList.length ? this.search(from, to, { ban: new Set(banList) }) : best;
      if (!j) continue; add(j);
      if (banList.length < 2) for (const l of new Set(j.lines)) queue.push(banList.concat(l));
    }
    const list = [...found.values()].sort((a, b) => a.total - b.total || a.changes - b.changes);
    const limit = list[0].total * 1.5 + 10;
    // prefer variety: drop routes whose line sequence equals a faster one (only different change point)
    const seen = new Set(), res = [];
    for (const j of list) {
      if (j.total > limit) continue;
      const ls = j.lines.join('>'); if (seen.has(ls)) continue; seen.add(ls); res.push(j);
      if (res.length >= k) break;
    }
    return res;
  };

  root.Router = Router;
  if (typeof module !== 'undefined') module.exports = Router;
})(typeof globalThis !== 'undefined' ? globalThis : this);
