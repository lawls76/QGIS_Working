# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Interactive venue mapping application for "The Anchor" in Nassau, Bahamas. Displays seating/ticket areas as GeoJSON polygons on a Leaflet map with Cloud Optimized GeoTIFF (COG) raster tile overlays.

## Running the Application

```bash
cd Map_Test
source .venv/bin/activate    # Python 3.9.10 virtualenv
python app.py                # Starts Flask dev server with debug=True
```

No `requirements.txt` exists. Key dependencies: Flask, folium, geojson, httpx.

## Architecture

**Stack:** Python Flask → Folium (server-side map generation) → Leaflet.js (client-side rendering)

**Data flow:**
1. `app.py` fetches COG raster tile metadata from TiTiler API (`titiler.xyz`) for a GeoTIFF hosted on GitHub
2. Loads seating polygon data from `static/Data/Seat_Slip_New.geojson`
3. Folium builds the full Leaflet map server-side with tile layers + GeoJSON features + popups
4. Flask serves the generated HTML to the browser

**Key files in `Map_Test/`:**
- `app.py` — Current main entry point (Flask server, Folium map construction, GeoJSON popup rendering)
- `app_LatestWorking.py` — Previous stable version (slightly fewer features)
- `main.py` — Original reference implementation with AJAX polling pattern for dynamic GeoJSON updates
- `Titiler_Raster_Serve.py` — Standalone utility for testing TiTiler COG metadata/tile fetching
- `templates/TiTiler.py` — FastAPI app for local COG serving via TiTiler factory
- `static/Data/Seat_Slip_New.geojson` — Primary seating/ticket polygon data (properties: id, Type, Ticket Num, Site Code, Descrip, Unit Price, image_url)

**Frontend assets:**
- `static/css/universal.css` — Full-viewport map styling
- `static/js/universal.js` — Leaflet map initialization (mostly commented/incomplete; Folium handles most JS generation)
- `templates/index.html` — Basic Leaflet template with marker loop

## External Dependencies

- **TiTiler API** (`https://titiler.xyz`) — Developmentseed demo endpoint used for COG tile serving
- **GitHub-hosted GeoTIFF** — Raster imagery fetched via TiTiler from a GitHub raw URL
- **Leaflet CDN** (v1.7.1) — Loaded client-side

## Notes

- No automated tests or CI/CD pipeline exist
- Multiple versioned copies of the app exist (`app.py`, `app_LatestWorking.py`, `app_working.py`, `main.py`) — `app.py` is current
- Generated HTML map files (`A_index.html`, `popup_index.html`) are checked in as output artifacts
- `.obsidian/` directory is an Obsidian notes vault, not part of the application
