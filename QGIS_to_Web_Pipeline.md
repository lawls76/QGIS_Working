# QGIS-to-Web Pipeline: How This Codebase Demonstrates Technical Use of QGIS

## Analogy: The Blueprint-to-Brochure Pipeline

Think of this like an architecture firm designing a venue:

- **QGIS is the drafting table** — where a GIS analyst drew the seating polygons (shapes representing each seat/slip) on top of an aerial photo of The Anchor marina, assigned ticket numbers, prices, and descriptions to each polygon, then exported everything.
- **The Python/Flask app is the print shop** — it takes those exported drawings and turns them into an interactive web brochure that customers can click on.

QGIS did the *authoring*. This codebase does the *serving*.

## Pipeline Diagram

```
 ┌──────────────────────────────────────────────────────────────┐
 │                     QGIS 3.36 (Desktop)                      │
 │                                                              │
 │  1. Load aerial GeoTIFF of The Anchor marina                │
 │  2. Draw MultiPolygon features for each seat/slip           │
 │  3. Attach attributes: Ticket Num, Descrip, Unit Price...   │
 │  4. Export → .geojson files                                  │
 │  5. Export → Cloud Optimized GeoTIFF (COG) for raster       │
 │                                                              │
 │  Project files saved as .qmd metadata                       │
 └──────────┬──────────────────────────────┬────────────────────┘
            │                              │
            ▼                              ▼
   Seat_Slip_New.geojson          Anchor_BM_geo.tif
   (vector polygons with          (raster image hosted
    seat attributes)               on GitHub)
            │                              │
            ▼                              ▼
 ┌──────────────────────────────────────────────────────────────┐
 │                    Flask app (app.py)                         │
 │                                                              │
 │  • Loads .geojson from static/Data/                         │
 │  • Fetches COG tiles via TiTiler API                        │
 │  • Folium stitches both into a Leaflet map                  │
 │  • Serves interactive HTML to browser                       │
 └──────────────────────────────────────────────────────────────┘
            │
            ▼
 ┌──────────────────────────────────────────────────────────────┐
 │                   Browser (Leaflet.js)                        │
 │                                                              │
 │  • Raster tile layer = the venue aerial image                │
 │  • GeoJSON overlay  = clickable seat polygons                │
 │  • Popups show seat name, price, purchase button             │
 └──────────────────────────────────────────────────────────────┘
```

## Where QGIS Fits: Step by Step

### Step 1 — QGIS Creates the Spatial Data

The `.qmd` files (`Seating_Slip_Update.qmd`, `Seat_New.json.qmd`) are QGIS layer metadata files from QGIS 3.36. They store the coordinate reference system (Web Mercator / EPSG:3857) and layer metadata. These prove the polygons were authored in QGIS, not hand-coded.

### Step 2 — QGIS Exports to GeoJSON

The evolution is visible in the multiple GeoJSON files — each represents a version of the spatial data as it was refined in QGIS:

| File | Role |
|------|------|
| `SeatSlip.geojson` | Earliest export (raw) |
| `Seating_Slip_Update.geojson` | Refined version |
| `static/Data/Seat_Slip_New.geojson` | **Final version** used by app.py |
| `static/Data/Seat_New_1.geojson` | Alternate iteration |

The final GeoJSON (`Seat_Slip_New.geojson`) has the collection name `"TheAnchor_Ticket"` with CRS84 coordinates — a standard QGIS export format. Each feature is a `MultiPolygon` with properties like `Ticket Num`, `Site Code`, `Descrip`, `Unit Price`.

### Step 3 — QGIS Produces the Raster (COG)

The aerial image of The Anchor (`Anchor_BM_geo.tif`) was georeferenced in QGIS and exported as a Cloud Optimized GeoTIFF. It is hosted on GitHub and served through TiTiler (`Titiler_Raster_Serve.py` was the test script for this). The COG format specifically enables tile-based streaming — QGIS can export to this format via `gdal_translate` or the Raster > Export menu.

### Step 4 — Flask/Folium Consumes What QGIS Produced

`app.py` loads the GeoJSON (line 151-153), iterates through each feature to build popups (lines 158-177), then overlays the polygons with tooltips (lines 182-201) on top of the raster tiles (lines 96-107). Folium generates Leaflet-compatible HTML server-side.

## Summary

This codebase is a demonstration of the full QGIS-to-web pipeline — using QGIS as the GIS authoring tool to digitize venue features and georeference raster imagery, then serving those outputs through a Python web stack. The QGIS work is the *upstream data production step*; the Flask app is the *downstream delivery step*.
