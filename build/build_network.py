import os as _os
B = _os.path.dirname(_os.path.abspath(__file__)) + '/'
"""Build network.json for the planner: stations (complexes), services, edges, walk links."""
import json, math, re, sys, collections
sys.path.insert(0, B)
from lines_extra import EXTRA, TUBE_META

import os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data') + '/'
osm = json.load(open(D + 'tfl_stations.json'))['features']
tfl = json.load(open(D + 'tube_network_tfl.json'))
osis = json.load(open(D + 'osis.json'))['2020']

def dist_m(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    x = (lo2 - lo1) * math.cos((la1 + la2) / 2)
    return 6371000 * math.hypot(x, la2 - la1)

def base(n):
    n = re.sub(r'\s*\((Rail|DLR|DLR 1|Tram|Central|H&C Line|Dist&Picc Line|Bakerloo|Circle Line)\)', '', n)
    n = n.replace('-Underground', '').replace('(H&C Line)', '').strip()
    fix = {'Battersea Power': 'Battersea Power Station', 'Paddington': 'Paddington',
           "King's Cross St. Pancras": "King's Cross St Pancras", 'St. James\'s Park': "St James's Park",
           "St. John's Wood": "St John's Wood", "St. Paul's": "St Paul's", 'Walthamstow Queens Road': "Walthamstow Queen's Road",
           'Queens Road Peckham': "Queens Road Peckham"}
    return fix.get(n, n)

# raw stops: rid -> dict(name, lat, lon, modes:set)
raw = {}
osm_by_base = collections.defaultdict(list)
for f in osm:
    p = f['properties']; lon, lat = f['geometry']['coordinates']
    osm_by_base[base(p['name'])].append((p['id'], lat, lon))
osm_pos = {f['properties']['id']: (f['geometry']['coordinates'][1], f['geometry']['coordinates'][0]) for f in osm}

def add_raw(rid, name, lat, lon, mode):
    r = raw.setdefault(rid, {'name': base(name), 'lat': lat, 'lon': lon, 'modes': set()})
    r['modes'].add(mode)

services = []  # dict(line, stops[rid])
lines = {}

# Tube from TfL sequences
for ln in tfl['lines']:
    nm, col, wait, speed = TUBE_META[ln['id']]
    lines[ln['id']] = {'name': nm, 'mode': 'tube', 'colour': col, 'wait': wait, 'speed': speed}
    seen = set()
    for br in ln['branches']['outbound']:  # outbound segments only; continuation handled by router
        k = tuple(br)
        if k in seen: continue
        seen.add(k)
        services.append({'line': ln['id'], 'stops': br})
        for rid in br:
            s = tfl['stations'][rid]
            add_raw(rid, s['name'], s['lat'], s['lon'], 'tube')

# drop services that are strict contiguous sub-sequences of another service on the same line
def is_sub(a, b):
    n = len(a)
    for seq in (b, b[::-1]):
        for i in range(len(seq) - n + 1):
            if seq[i:i + n] == a: return True
    return False
pruned = []
for s in services:
    if any(t is not s and t['line'] == s['line'] and len(t['stops']) > len(s['stops']) and is_sub(s['stops'], t['stops']) for t in services):
        continue
    pruned.append(s)
services = pruned

tube_by_base = collections.defaultdict(list)
for rid, r in list(raw.items()):
    tube_by_base[r['name']].append(rid)

unresolved = []
def resolve(name, mode):
    cands = osm_by_base.get(name, [])
    pref = {'dlr': ('940GZZDL',), 'tram': ('940GZZCR',)}.get(mode, ('910G',))
    for p in pref:
        for c in cands:
            if c[0].startswith(p): return c
    for c in cands:
        if not c[0].startswith('940GZZLU'): return c
    if cands: return cands[0]
    if tube_by_base.get(name):
        rid = tube_by_base[name][0]; r = raw[rid]; return (rid, r['lat'], r['lon'])
    unresolved.append((mode, name)); return None

for lid, L in EXTRA.items():
    lines[lid] = {k: L[k] for k in ('name', 'mode', 'colour', 'wait', 'speed')}
    for seq in L['services']:
        stops = []
        for n in seq:
            c = resolve(n, L['mode'])
            if not c: continue
            add_raw(c[0], n, c[1], c[2], L['mode'])
            stops.append(c[0])
        services.append({'line': lid, 'stops': stops})

if unresolved:
    print('UNRESOLVED', unresolved)

# ---- merge raw stops into complexes: same base name & within 350 m
groups = collections.defaultdict(list)
for rid, r in raw.items(): groups[r['name']].append(rid)
complex_of = {}
complexes = []
MODE_LABEL = {'tube': 'Underground', 'overground': 'Overground', 'elizabeth': 'Elizabeth line', 'dlr': 'DLR', 'tram': 'Tram'}
for name, rids in groups.items():
    clusters = []
    for rid in rids:
        p = (raw[rid]['lat'], raw[rid]['lon'])
        for cl in clusters:
            if any(dist_m(p, (raw[o]['lat'], raw[o]['lon'])) <= 350 for o in cl):
                cl.append(rid); break
        else:
            clusters.append([rid])
    for cl in clusters:
        modes = set().union(*(raw[r]['modes'] for r in cl))
        label = name
        if len(clusters) > 1:
            label = f"{name} ({'/'.join(sorted(MODE_LABEL[m] for m in modes))})"
        lat = sum(raw[r]['lat'] for r in cl) / len(cl); lon = sum(raw[r]['lon'] for r in cl) / len(cl)
        cid = len(complexes)
        complexes.append({'name': label, 'lat': round(lat, 6), 'lon': round(lon, 6), 'rids': cl})
        for r in cl: complex_of[r] = cid
    if len(clusters) > 1:
        print('SPLIT', name, [[raw[r]['modes'] for r in cl] for cl in clusters])

# ---- edges
def ride_min(a, b, line):
    d = dist_m((complexes[a]['lat'], complexes[a]['lon']), (complexes[b]['lat'], complexes[b]['lon'])) / 1000
    v = lines[line]['speed'] * min(1.6, 1 + max(0, d - 2.5) / 8)
    return round(0.5 + d / v * 60, 1)

out_services = []
for s in services:
    cs = []
    for rid in s['stops']:
        c = complex_of[rid]
        if not cs or cs[-1] != c: cs.append(c)
    times = [ride_min(cs[i], cs[i + 1], s['line']) for i in range(len(cs) - 1)]
    out_services.append({'line': s['line'], 'stops': cs, 't': times})

# ---- walking links from OSI list (only between different complexes)
walks = {}
for row in osis:
    a, b = row[0], row[1]
    if a in complex_of and b in complex_of:
        ca, cb = complex_of[a], complex_of[b]
        if ca == cb: continue
        d = dist_m((complexes[ca]['lat'], complexes[ca]['lon']), (complexes[cb]['lat'], complexes[cb]['lon']))
        k = tuple(sorted((ca, cb)))
        walks[k] = round(2 + d * 1.3 / 80, 1)
# same-name split stations always get a walk link
by_base = collections.defaultdict(list)
for i, c in enumerate(complexes): by_base[re.sub(r' \(.*\)$', '', c['name'])].append(i)
for nm, ids in by_base.items():
    for i in ids:
        for j in ids:
            if i < j:
                d = dist_m((complexes[i]['lat'], complexes[i]['lon']), (complexes[j]['lat'], complexes[j]['lon']))
                if d < 1500: walks.setdefault((i, j), round(2 + d * 1.3 / 80, 1))

# lines per complex
lines_at = collections.defaultdict(set)
for s in out_services:
    for c in s['stops']: lines_at[c].add(s['line'])
# drop complexes no service uses
used = sorted(lines_at)
remap = {old: new for new, old in enumerate(used)}
stations = [{'n': complexes[o]['name'], 'lat': complexes[o]['lat'], 'lon': complexes[o]['lon'],
             'l': sorted(lines_at[o])} for o in used]
for s in out_services: s['stops'] = [remap[c] for c in s['stops']]
walks_out = [[remap[a], remap[b], t] for (a, b), t in walks.items() if a in remap and b in remap]

net = {'generated': '2026-10-09', 'lines': lines, 'stations': stations, 'services': out_services, 'walks': walks_out,
       'credits': 'Tube sequences: TfL Unified API (via tube-map, MIT). Other modes & interchanges: O. O\'Brien / OpenStreetMap contributors (CC-BY-NC, ODbL).'}
json.dump(net, open(B + 'network.json', 'w'), separators=(',', ':'), ensure_ascii=False)
cnt = collections.Counter()
for st in stations:
    for l in st['l']: cnt[lines[l]['mode']] += 0
mode_st = collections.defaultdict(set)
for i, st in enumerate(stations):
    for l in st['l']: mode_st[lines[l]['mode']].add(i)
print('stations', len(stations), {m: len(v) for m, v in mode_st.items()}, 'services', len(out_services), 'walks', len(walks_out))
