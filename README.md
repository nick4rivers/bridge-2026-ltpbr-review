# Bridge LTPBR Treatment Review

Leaflet web map of 2026 as-built low-tech process-based restoration (LTPBR) structures on Bridge Creek, John Day Basin, Oregon, with design reaches colored by treatment type.

**For end-of-season review by BLM and Trout Unlimited only.** Field-recorded data; preliminary and subject to QA/QC.

## Files
- `index.html`: the map (Leaflet 1.9.4 from unpkg, Esri/CARTO basemaps)
- `data/bridge_asbuilt_2026.js`: reaches + as-built points, simplified and bundled (works from file:// and GitHub Pages)
- `scripts/prep_data.py`: rebuilds the data file from the source GeoJSON

## Rebuild data
```
python3 scripts/prep_data.py "/path/to/Bridge Creek" data.json
printf 'window.BRIDGE_DATA = ' > data/bridge_asbuilt_2026.js && cat data.json >> data/bridge_asbuilt_2026.js && echo ';' >> data/bridge_asbuilt_2026.js
```
Sources: `Bridge As Built 2026/Bridge_Raw_AsBuilt_20261117.geojson` and `Bridge As Built 2026/Bridge Creek Reaches.geojson`.

## Host on GitHub Pages
Push this folder to a repo, then Settings → Pages → deploy from branch (root).
