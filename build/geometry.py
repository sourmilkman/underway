import os as _os
B = _os.path.dirname(_os.path.abspath(__file__)) + '/'
"""Turn layout into drawable geometry: octilinear edge paths with parallel offsets, station markers, label placement."""
import json, math
from shapely.geometry import LineString, Point, Polygon, box
from shapely.affinity import rotate as srot
from shapely.strtree import STRtree

net = json.load(open(B + 'network.json'))
xy = json.load(open(B + 'layout.json'))['xy']
S = net['stations']; LINES = net['lines']
ORDER = ['elizabeth', 'central', 'piccadilly', 'district', 'circle', 'hammersmith-city', 'metropolitan', 'jubilee', 'northern',
         'bakerloo', 'victoria', 'waterloo-city', 'mildmay', 'windrush', 'weaver', 'suffragette', 'lioness', 'liberty', 'dlr', 'tram']
LW = 0.17      # line width (map units)
FS = 0.32      # label font size
CHW = 0.56     # avg char width / font size

edge_lines = {}
for s in net['services']:
    st = s['stops']
    for a, b in zip(st, st[1:]):
        k = (min(a, b), max(a, b)); edge_lines.setdefault(k, set()).add(s['line'])

def octi(a, b):
    ax, ay = a; bx, by = b; dx, dy = bx - ax, by - ay
    ang = math.degrees(math.atan2(dy, dx)); dev = abs(((ang + 22.5) % 45) - 22.5)
    if dev < 2.0: return [a, b]
    sx = 1 if dx >= 0 else -1; sy = 1 if dy >= 0 else -1
    if abs(dx) >= abs(dy):
        d = abs(dy); s = abs(dx) - d
        p1 = (ax + sx * s / 2, ay); p2 = (p1[0] + sx * d, by)
    else:
        d = abs(dx); s = abs(dy) - d
        p1 = (ax, ay + sy * s / 2); p2 = (bx, p1[1] + sy * d)
    return [a, p1, p2, b]

def offset_poly(pts, off):
    if off == 0: return pts
    out = []
    n = len(pts)
    def nrm(p, q):
        dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy) or 1
        return (-dy / L, dx / L)
    for i in range(n):
        if i == 0: nx, ny = nrm(pts[0], pts[1]); out.append((pts[0][0] + nx * off, pts[0][1] + ny * off)); continue
        if i == n - 1: nx, ny = nrm(pts[-2], pts[-1]); out.append((pts[-1][0] + nx * off, pts[-1][1] + ny * off)); continue
        n1 = nrm(pts[i - 1], pts[i]); n2 = nrm(pts[i], pts[i + 1])
        mx, my = n1[0] + n2[0], n1[1] + n2[1]; ml = math.hypot(mx, my) or 1
        mx, my = mx / ml, my / ml; cos = mx * n1[0] + my * n1[1] or 1
        out.append((pts[i][0] + mx * off / cos, pts[i][1] + my * off / cos))
    return out

r3 = lambda v: round(v, 3)
paths = {l: [] for l in LINES}
edge_geom = {}
max_par = [1] * len(S)
for (a, b), ls in edge_lines.items():
    ls = sorted(ls, key=ORDER.index); m = len(ls)
    base = octi(tuple(xy[a]), tuple(xy[b]))
    edge_geom[(a, b)] = base
    max_par[a] = max(max_par[a], m); max_par[b] = max(max_par[b], m)
    for k, l in enumerate(ls):
        pts = offset_poly(base, (k - (m - 1) / 2) * LW)
        paths[l].append('M' + 'L'.join(f'{r3(x)} {r3(y)}' for x, y in pts))

# markers
markers = []
for i, s in enumerate(S):
    inter = len(s['l']) > 1 or i in {w[0] for w in net['walks']} | {w[1] for w in net['walks']}
    r = min(0.3, 0.18 + LW * 0.4 * (max_par[i] - 1)) if inter else 0.12
    markers.append([r3(xy[i][0]), r3(xy[i][1]), r3(r), 1 if inter else 0])

# ---- label placement
line_geoms = [LineString(g).buffer(LW * 0.5 * len(edge_lines[k]) + 0.04) for k, g in edge_geom.items()]
mark_geoms = [Point(m[0], m[1]).buffer(m[2] + 0.22) for m in markers]
obst = line_geoms + mark_geoms
tree = STRtree(obst)

def label_poly(i, cand):
    x, y = xy[i]; r = markers[i][2]; w = len(S[i]['n']) * FS * CHW; h = FS * 1.05; g = r + 0.12
    kind = cand
    if kind == 'E': return box(x + g, y - h / 2, x + g + w, y + h / 2)
    if kind == 'W': return box(x - g - w, y - h / 2, x - g, y + h / 2)
    if kind == 'N': return box(x - w / 2, y - g - h, x + w / 2, y - g)
    if kind == 'S': return box(x - w / 2, y + g, x + w / 2, y + g + h)
    if kind == 'NE': return box(x + g * 0.8, y - g * 0.8 - h, x + g * 0.8 + w, y - g * 0.8)
    if kind == 'SE': return box(x + g * 0.8, y + g * 0.8, x + g * 0.8 + w, y + g * 0.8 + h)
    if kind == 'NW': return box(x - g * 0.8 - w, y - g * 0.8 - h, x - g * 0.8, y - g * 0.8)
    if kind == 'SW': return box(x - g * 0.8 - w, y + g * 0.8, x - g * 0.8, y + g * 0.8 + h)
    if kind in ('R1', 'R2'):  # rotated -45 deg (up-right) / +45 (down-right)
        b = box(x + g, y - h / 2, x + g + w, y + h / 2)
        return srot(b, -45 if kind == 'R1' else 45, origin=(x, y))
    if kind in ('R3', 'R4'):  # rotated text going left
        b = box(x - g - w, y - h / 2, x - g, y + h / 2)
        return srot(b, 45 if kind == 'R3' else -45, origin=(x, y))
CANDS = ['E', 'W', 'N', 'S', 'NE', 'SE', 'NW', 'SW', 'R1', 'R2', 'R3', 'R4']
PREF = {c: k * 0.02 for k, c in enumerate(CANDS)}
for c in ('R1', 'R2', 'R3', 'R4'): PREF[c] += 0.8

order = sorted(range(len(S)), key=lambda i: (-len(S[i]['l']), -max_par[i]))
labels = ['E'] * len(S); polys = [label_poly(i, 'E') for i in range(len(S))]
def cost_of(i, c, poly, others):
    cost = PREF[c]
    for j in tree.query(poly):
        if j == len(line_geoms) + i: continue
        g = obst[j]; a = poly.intersection(g).area / (FS * FS)
        cost += (8.0 if j >= len(line_geoms) else 5.0) * a
    for q in others:
        if poly.intersects(q): cost += 14.0 * poly.intersection(q).area / (FS * FS) + 1.0
    return cost
lab_tree_polys = None
for it in range(4):
    for i in order:
        others_idx = STRtree(polys).query(label_poly(i, 'E').buffer(FS * 30))
        others = [polys[k] for k in others_idx if k != i]
        best = None
        for c in CANDS:
            poly = label_poly(i, c)
            cst = cost_of(i, c, poly, others)
            if best is None or cst < best[0]: best = (cst, c, poly)
        labels[i] = best[1]; polys[i] = best[2]
placed = polys
bad = 0
for i, p in enumerate(placed):
    for q in placed[i + 1:]:
        if p.intersects(q) and p.intersection(q).area > 0.01: bad += 1
print('label overlaps', bad)

geom = {'edges': {f'{a}-{b}': [[r3(x), r3(y)] for x, y in g] for (a, b), g in edge_geom.items()}, 'lw': LW, 'fs': FS, 'paths': {l: ''.join(v) for l, v in paths.items() if v}, 'markers': markers, 'labels': labels,
        'size': [r3(max(p[0] for p in xy)), r3(max(p[1] for p in xy))]}
json.dump(geom, open(B + 'geom.json', 'w'), separators=(',', ':'))
print('bytes', len(json.dumps(geom)))
