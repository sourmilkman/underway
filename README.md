# Underway

A personal, offline map and journey planner for London's Underground, Elizabeth line, Overground, DLR and trams.

**Install:** open https://sourmilkman.github.io/underway/ in Chrome on Android, then choose *Install app* (or *Add to Home screen*). After the first visit it works with no signal.

## What's here
- `index.html`, `sw.js`, `manifest.webmanifest`, icons: the app (served by GitHub Pages).
- `pdf.min.js`, `pdf.worker.min.js`: Mozilla PDF.js (Apache-2.0), for viewing your own downloaded map offline.
- `build/`: the pipeline that produces the app.

## Rebuilding
```
cd build
python3 build_network.py   # stations, lines, services, timings -> network.json
python3 layout.py          # schematic layout -> layout.json
python3 geometry.py        # line paths, markers, labels -> geom.json
python3 assemble.py        # writes index.html and sw.js to the repo root
```
Needs Python 3 with numpy, scipy and shapely.

## Data and accuracy
- Tube sequences: TfL Unified API (September 2026).
- Other modes and interchanges: O. O'Brien / OpenStreetMap contributors (CC-BY-NC, ODbL). Personal, non-commercial use only.
- Journey times are estimates from distance, typical line speeds and average waits. No live delay information.
