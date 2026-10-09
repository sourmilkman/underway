import os as _os
B = _os.path.dirname(_os.path.abspath(__file__)) + '/'
"""Compute an original schematic (octilinear-leaning) layout from geographic station positions."""
import json, math, sys
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree

net = json.load(open(B + 'network.json'))
S = net['stations']; n = len(S)
LAT0, LON0 = 51.513, -0.112
geo = np.array([[(s['lon'] - LON0) * 111.32 * math.cos(math.radians(LAT0)), -(s['lat'] - LAT0) * 110.57] for s in S])

# fisheye: expand centre, compress suburbs
r = np.hypot(geo[:, 0], geo[:, 1]) + 1e-9
B = 4.5
rf = B * np.arcsinh(r / B) ** 1.0
rf = 6.0 * np.arcsinh(r / 1.5)
p0 = geo * (rf / r)[:, None]
WA = 1.0 / (1 + (r / 9.0) ** 2)
WA[[i for i, st in enumerate(S) if st['l'] == ['tram']]] *= 0.05

edges = set(); bends = set()
for s in net['services']:
    st = s['stops']
    for a, b in zip(st, st[1:]):
        if a != b: edges.add((min(a, b), max(a, b)))
    for a, b, c in zip(st, st[1:], st[2:]):
        if len({a, b, c}) == 3: bends.add((a, b, c))
E = np.array(sorted(edges)); Bn = np.array(sorted(bends))
# scale so median edge length = 1
med = np.median(np.linalg.norm(p0[E[:, 1]] - p0[E[:, 0]], axis=1))
p0 = p0 / med * 1.0
print('stations', n, 'edges', len(E), 'bends', len(Bn), 'median scale', med)

W = dict(anchor=0.02, oct=1.0, short=6.0, long=0.04, bend=0.6, rep=8.0, segrep=6.0)
DMIN = 1.1
SEGMIN = 0.55

def energy(x):
    p = x.reshape(-1, 2); g = np.zeros_like(p); En = 0.0
    # anchor
    d = p - p0; En += W['anchor'] * (WA[:, None] * d ** 2).sum(); g += 2 * W['anchor'] * WA[:, None] * d
    v = p[E[:, 1]] - p[E[:, 0]]; L2 = (v ** 2).sum(1) + 1e-9; L = np.sqrt(L2)
    th = np.arctan2(v[:, 1], v[:, 0])
    # octilinear
    En += W['oct'] * (1 - np.cos(8 * th)).sum()
    dth = 8 * W['oct'] * np.sin(8 * th)
    gth = np.stack([-v[:, 1], v[:, 0]], 1) / L2[:, None] * dth[:, None]
    np.add.at(g, E[:, 1], gth); np.add.at(g, E[:, 0], -gth)
    # length
    sh = np.minimum(0, L - 1.0)
    En += W['short'] * (sh ** 2).sum() + W['long'] * ((L - 1.0) ** 2).sum()
    dL = 2 * W['short'] * sh + 2 * W['long'] * (L - 1.0)
    gl = v / L[:, None] * dL[:, None]
    np.add.at(g, E[:, 1], gl); np.add.at(g, E[:, 0], -gl)
    # bends (prefer straight continuation)
    a, b, c = Bn[:, 0], Bn[:, 1], Bn[:, 2]
    v1 = p[b] - p[a]; v2 = p[c] - p[b]
    l1 = (v1 ** 2).sum(1) + 1e-9; l2 = (v2 ** 2).sum(1) + 1e-9
    t1 = np.arctan2(v1[:, 1], v1[:, 0]); t2 = np.arctan2(v2[:, 1], v2[:, 0])
    En += W['bend'] * (1 - np.cos(t2 - t1)).sum()
    dd = W['bend'] * np.sin(t2 - t1)  # dE/dt2 ; dE/dt1 = -dd
    g2 = np.stack([-v2[:, 1], v2[:, 0]], 1) / l2[:, None] * dd[:, None]
    g1 = np.stack([-v1[:, 1], v1[:, 0]], 1) / l1[:, None] * (-dd)[:, None]
    np.add.at(g, c, g2); np.add.at(g, b, -g2); np.add.at(g, b, g1); np.add.at(g, a, -g1)
    # repulsion
    pairs = cKDTree(p).query_pairs(DMIN, output_type='ndarray')
    if len(pairs):
        i, j = pairs[:, 0], pairs[:, 1]
        dv = p[j] - p[i]; dl = np.sqrt((dv ** 2).sum(1)) + 1e-9
        ov = DMIN - dl
        En += W['rep'] * (ov ** 2).sum()
        gr = -2 * W['rep'] * ov[:, None] * dv / dl[:, None]
        np.add.at(g, j, gr); np.add.at(g, i, -gr)
    # keep stations off other lines' edges
    mid = (p[E[:, 0]] + p[E[:, 1]]) / 2
    halfL = L / 2
    tree = cKDTree(mid)
    cand = tree.query_ball_point(p, r=halfL.max() + SEGMIN)
    pi, ei = [], []
    for k, lst in enumerate(cand):
        for e in lst:
            if E[e, 0] != k and E[e, 1] != k: pi.append(k); ei.append(e)
    if pi:
        pi = np.array(pi); ei = np.array(ei)
        A = p[E[ei, 0]]; Bp = p[E[ei, 1]]; P = p[pi]
        ab = Bp - A; t = np.clip(((P - A) * ab).sum(1) / ((ab ** 2).sum(1) + 1e-9), 0, 1)
        q = A + ab * t[:, None]; dv = P - q; dl = np.sqrt((dv ** 2).sum(1)) + 1e-9
        m = dl < SEGMIN
        if m.any():
            pi, ei, t, dv, dl = pi[m], ei[m], t[m], dv[m], dl[m]
            ov = SEGMIN - dl
            En += W['segrep'] * (ov ** 2).sum()
            gp = -2 * W['segrep'] * ov[:, None] * dv / dl[:, None]
            np.add.at(g, pi, gp)
            np.add.at(g, E[ei, 0], -gp * (1 - t)[:, None])
            np.add.at(g, E[ei, 1], -gp * t[:, None])
    return En, g.ravel()

x = p0.ravel().copy()
for stage, (wo, wb) in enumerate([(0.0, 2.0), (0.3, 2.0), (1.0, 2.0), (3.0, 2.5), (8.0, 3.0)]):
    W['oct'] = wo; W['bend'] = wb
    res = minimize(energy, x, jac=True, method='L-BFGS-B', options={'maxiter': 1500})
    x = res.x
    p = x.reshape(-1, 2); v = p[E[:, 1]] - p[E[:, 0]]
    th = np.degrees(np.arctan2(v[:, 1], v[:, 0])); dev = np.abs(((th + 22.5) % 45) - 22.5)
    print('stage', stage, 'E=%.1f' % res.fun, 'mean dev %.2f°' % dev.mean(), '>5°: %d' % (dev > 5).sum())

p = x.reshape(-1, 2)
p -= p.min(0)
out = {'xy': [[round(float(a), 3), round(float(b), 3)] for a, b in p]}
json.dump(out, open(B + 'layout.json', 'w'))
print('extent', p.max(0))
