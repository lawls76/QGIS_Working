# The Anchor — Interactive Venue Map

Interactive mapping application for **The Anchor** marina in Nassau, Bahamas. Displays seating and ticket areas as clickable GeoJSON polygons on a Leaflet map, overlaid on a Cloud Optimized GeoTIFF (COG) aerial raster.

## How It Works

1. **QGIS** (desktop GIS) was used to digitize seating polygons on top of a georeferenced aerial photo, assign attributes (ticket number, price, description), and export to GeoJSON + COG formats.
2. **Flask + Folium** loads the GeoJSON and fetches COG raster tiles via the TiTiler API, then generates a full Leaflet map server-side.
3. **Leaflet.js** renders the interactive map in the browser — raster tiles for the venue image, clickable polygon overlays for each seat/slip with popup details and images.

See [`QGIS_to_Web_Pipeline.md`](QGIS_to_Web_Pipeline.md) for a detailed breakdown of the QGIS-to-web pipeline.

## Tech Stack

- **Python 3.9** / Flask / Folium
- **Leaflet.js** (v1.7.1, client-side)
- **TiTiler API** (COG tile serving via `titiler.xyz`)
- **QGIS 3.36** (upstream data authoring)

## Quick Start

```bash
cd Map_Test
source .venv/bin/activate
python app.py
```

The Flask dev server starts with debug mode enabled. Open the URL shown in the terminal.

## Project Structure

```
Map_Test/
├── app.py                          # Main Flask app (current entry point)
├── app_LatestWorking.py            # Previous stable version
├── main.py                         # Original reference implementation
├── Titiler_Raster_Serve.py         # Utility for testing TiTiler COG metadata
├── static/
│   ├── css/universal.css           # Full-viewport map styling
│   ├── js/universal.js             # Leaflet map init (mostly handled by Folium)
│   └── Data/
│       └── Seat_Slip_New.geojson   # Primary seating polygon data
├── templates/
│   ├── index.html                  # Base Leaflet template
│   └── TiTiler.py                  # FastAPI app for local COG serving
├── SeatSlip.geojson                # Earlier GeoJSON export
├── Seating_Slip_Update.geojson     # Refined GeoJSON export
├── *.qmd                           # QGIS layer metadata files
├── A_index.html                    # Generated map output
└── popup_index.html                # Generated map output
```

## Data

The GeoJSON features are `MultiPolygon` geometries with these properties:

| Property     | Description                        |
|--------------|------------------------------------|
| `id`         | Feature identifier                 |
| `Type`       | Seating/slip category              |
| `Ticket Num` | Ticket number                      |
| `Site Code`  | Location code                      |
| `Descrip`    | Human-readable description         |
| `Unit Price` | Price in USD                       |
| `image_url`  | URL to associated seat/slip image  |

## External Services

- **TiTiler** (`https://titiler.xyz`) — Development seed demo endpoint for COG tile serving
- **GitHub-hosted GeoTIFF** — Aerial raster imagery fetched via TiTiler
